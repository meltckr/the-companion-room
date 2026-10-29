"""Render the exported WebGL layout with Blender Cycles.

Blender --background --python scripts/render-cinematic.py -- \
  --scene evidence/scene.json --out assets/cinematic --samples 64

Same geometry and station positions as model.js. Materials, lighting, front wall,
ceiling and a winter courtyard backdrop are presentation treatments. No claim of
construction suitability, real site views, or selected manufactured equipment.
"""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--samples', type=int, default=64)
    parser.add_argument('--width', type=int, default=3840)
    parser.add_argument('--hero-width', type=int, default=2560)
    parser.add_argument('--only', choices=['all', 'hero', 'entrance', 'wash', 'dry'], default='all')
    parser.add_argument('--cpu', action='store_true')
    parser.add_argument('--future-bay', action='store_true')
    parser.add_argument('--save-only', action='store_true')
    return parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def xyz(p):
    return (p[0], -p[2], p[1])


def linear(c):
    return c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4


def material(name, rgb, rough=.6, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*[linear(v) for v in rgb], 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    return mat, bsdf


def textured_material(key):
    r,g,b,rough,kind = key
    steel = abs(r-.682)<.025 and abs(g-.733)<.025 and abs(b-.714)<.025
    if abs(r-.251)<.025 and abs(g-.357)<.025 and abs(b-.314)<.025:
        r,g,b,rough=.17,.285,.225,.38
    elif abs(r-.149)<.025 and abs(g-.235)<.025 and abs(b-.204)<.025:
        r,g,b,rough=.095,.17,.13,.4
    if kind==1:r,g,b,rough=.77,.735,.66,.42
    if kind==2:r,g,b,rough=r*.88,g*.85,b*.83,.43
    mat, bsdf = material(f'finish_{kind}_{r:.2f}_{g:.2f}_{b:.2f}', (r,g,b), rough)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    if kind == 4:
        bsdf.inputs['Base Color'].default_value = (.82,.9,.92,1)
        bsdf.inputs['Roughness'].default_value = .07
        bsdf.inputs['Transmission Weight'].default_value = 1
        bsdf.inputs['IOR'].default_value = 1.45
        return mat
    if kind == 5:
        bsdf.inputs['Emission Color'].default_value = (1,.74,.4,1)
        bsdf.inputs['Emission Strength'].default_value = 4
        return mat
    # Stainless equipment and fixtures are shared by source color.
    if steel:
        bsdf.inputs['Metallic'].default_value = .9
        bsdf.inputs['Roughness'].default_value = .25
        bsdf.inputs['Anisotropic'].default_value = .3
    tex = nodes.new('ShaderNodeTexCoord')
    scale = nodes.new('ShaderNodeVectorMath'); scale.operation = 'MULTIPLY'
    links.new(tex.outputs['Object'],scale.inputs[0])
    scale.inputs[1].default_value = (48,48,.9) if kind == 2 else ((450,450,4) if steel else (5,5,5))
    noise = nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 2.5
    noise.inputs['Detail'].default_value = 3
    links.new(scale.outputs['Vector'],noise.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    low=.77 if kind==2 else .91
    high=1.06 if kind==2 else 1.025
    base=[linear(v) for v in (r,g,b)]
    ramp.color_ramp.elements[0].position=.15
    ramp.color_ramp.elements[0].color=(*[v*low for v in base],1)
    ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[1].color=(*[min(1,v*high) for v in base],1)
    links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
    bump=nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.16 if kind in (1,2) else .08
    bump.inputs['Distance'].default_value=.00065 if kind==2 else (.000035 if steel else .00035)
    links.new(noise.outputs['Fac'],bump.inputs['Height'])
    links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
    return mat


def cube(name, location, dimensions, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz(location))
    obj=bpy.context.object; obj.name=name
    obj.dimensions=(dimensions[0],dimensions[2],dimensions[1])
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod=obj.modifiers.new('Soft edge highlights','BEVEL'); mod.width=bevel;mod.segments=3
    return obj


def area(name, location, target, energy, color=(1,.84,.67), size=3, size_y=None):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.color=color
    data.shape='RECTANGLE' if size_y else 'DISK';data.size=size
    if size_y:data.size_y=size_y
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    obj.location=xyz(location)
    obj.rotation_euler=(Vector(xyz(target))-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj


def import_scene(data, future):
    vertices=data['vertices'];buckets=defaultdict(lambda:([],[]))
    # Keep nonadjacent objects separate by item. Welding restores the original
    # mesh's shared corners so bevels operate on surfaces rather than triangles.
    for index,item in enumerate(data['items']):
        group=item['group']
        if group=='future' and not future or group=='flex' and future:
            continue
        # Replace only the schematic plant's above-pot stems and polygon leaves.
        item_vertices=[vertices[i:i+3] for i in range(item['start']*11,(item['start']+item['count'])*11,11)]
        if group=='flex' and all(2.55<p[0]<3.55 and -2.4<p[2]<-1.4 for p in item_vertices) and min(p[1] for p in item_vertices)>=.4 and max(p[1] for p in item_vertices)>.5:
            continue
        groups=defaultdict(lambda:([],[]))
        for offset in range(item['start']*11,(item['start']+item['count'])*11,33):
            key=tuple(round(vertices[offset+i],5) for i in (6,7,8,9,10))
            positions,faces=groups[key];start=len(positions)
            positions.extend(xyz(vertices[offset+i:offset+i+3]) for i in (0,11,22))
            faces.append((start,start+1,start+2))
        for key,(positions,faces) in groups.items():
            # Adjacent source items remain separate shells but share a material.
            target_positions,target_faces=buckets[key]
            base=len(target_positions);target_positions.extend(positions)
            target_faces.extend(tuple(v+base for v in face) for face in faces)
    for key,(positions,faces) in buckets.items():
        mesh=bpy.data.meshes.new(f'Room finish {key[-1]}');mesh.from_pydata(positions,[],faces);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00002)
        bmesh.ops.dissolve_limit(bm,angle_limit=.001,verts=list(bm.verts),edges=list(bm.edges),delimit={'NORMAL'})
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(mesh);bm.free();mesh.update()
        obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj)
        obj.data.materials.append(textured_material(key))
        if key[-1] not in (4,5):
            bevel=obj.modifiers.new('Fine manufactured edges','BEVEL');bevel.width=.0035;bevel.segments=3;bevel.limit_method='ANGLE'
            normal=obj.modifiers.new('Surface normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=40


def botanical_plant():
    # Ficus-like curved leaves and thin stems, sharing the existing planter position.
    stem_mat,_=material('Living stems',(.20,.28,.12),.72)
    leaves=[]
    for i in range(3):
        mat,bsdf=material(f'Leaf green {i}',(.14+i*.025,.29+i*.025,.12+i*.018),.36)
        bsdf.inputs['Subsurface Weight'].default_value=.06
        bsdf.inputs['Coat Weight'].default_value=.18
        leaves.append(mat)
    for i in range(11):
        angle=i*2.39996
        origin=Vector((3.05,1.9,.43))
        tip=Vector((3.05+math.cos(angle)*(.15+(i%3)*.06),1.9+math.sin(angle)*(.15+(i%3)*.06),.78+(i%4)*.14))
        curve=bpy.data.curves.new('Plant stem','CURVE');curve.dimensions='3D';curve.resolution_u=16;curve.bevel_depth=.006;curve.bevel_resolution=3
        spline=curve.splines.new('BEZIER');spline.bezier_points.add(2)
        for bp,pos in zip(spline.bezier_points,[origin,(origin+tip)/2+Vector((0,0,.08)),tip]):
            bp.co=pos;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
        obj=bpy.data.objects.new('Curved living stem',curve);bpy.context.collection.objects.link(obj);obj.data.materials.append(stem_mat)
        direction=Vector((math.cos(angle)*.8,math.sin(angle)*.8,.35)).normalized()
        side=Vector((-math.sin(angle),math.cos(angle),0))
        length=.28+(i%3)*.035;width=.09+(i%2)*.015
        verts=[];faces=[]
        for row in range(15):
            t=row/14;center=tip+direction*(length*t)+Vector((0,0,.065*math.sin(math.pi*t)-.11*t*t))
            half=width*(math.sin(math.pi*t)**.8)
            for col in range(5):
                u=(col-2)/2
                verts.append(tuple(center+side*(half*u)+Vector((0,0,-.028*abs(u)*math.sin(math.pi*t)))))
        for row in range(14):
            for col in range(4):
                a=row*5+col;faces.append((a,a+1,a+6,a+5))
        mesh=bpy.data.meshes.new('Curved leaf surface');mesh.from_pydata(verts,[],faces);mesh.update()
        leaf=bpy.data.objects.new('Living leaf',mesh);bpy.context.collection.objects.link(leaf);leaf.data.materials.append(leaves[i%3])
        for poly in mesh.polygons:poly.use_smooth=True
        solid=leaf.modifiers.new('Leaf thickness','SOLIDIFY');solid.thickness=.0008


def finish_room():
    plaster,_=material('Warm plaster',(.91,.89,.84),.8)
    oak,_=material('Door oak',(.60,.45,.29),.45)
    metal,_=material('Dark bronze',(.20,.25,.22),.4,.45)
    # Close the presentation cutaway with a residential entry and plaster ceiling.
    cube('Front wall left',(-2.12,1.5,3.4),(3.08,3,.16),plaster,.004)
    cube('Front wall right',(2.12,1.5,3.4),(3.08,3,.16),plaster,.004)
    cube('Entry header',(0,2.77,3.4),(1.16,.46,.16),plaster,.004)
    cube('Entry door',(0,1.26,3.43),(1.1,2.52,.06),oak,.008)
    cube('Door handle',(.42,1.12,3.37),(.035,.27,.055),metal,.006)
    cube('Ceiling',(0,3.10,0),(7.48,.16,6.87),plaster,.005)
    # Actual grout joints on the existing floor, below object placement height.
    grout,_=material('Warm floor grout',(.61,.60,.55),.95)
    for i in range(1,12):cube('Floor joint X',(-3.6576+i*.61,.016,0),(.004,.002,6.7056),grout)
    for i in range(1,11):cube('Floor joint Z',(0,.016,-3.3528+i*.61),(7.3152,.002,.004),grout)
    # A neutral winter courtyard treatment, deliberately no site-specific scenery.
    snow,_=material('Winter ground',(.91,.94,.96),.88)
    cube('Winter courtyard',(8,-.11,.5),(8,.1,18),snow)
    fence,_=material('Courtyard screening',(.57,.60,.58),.85)
    cube('Distant screening',(10,1.25,.5),(.15,2.5,18),fence)
    for z in [-6,-3,1,4,7]:
        bark,_=material(f'Tree bark {z}',(.35,.31,.25),.95)
        cube('Winter tree trunk',(8.5,1.7,z),(.12,3.4,.12),bark,.01)
        for angle in [-.65,.6]:
            branch=cube('Winter branch',(8.5,2.7,z),(.06,1.4,.06),bark,.01)
            branch.rotation_euler[0]=angle
    # Lighting uses watts and metre-scale sources. No hidden branded equipment.
    area('Winter window daylight',(4.1,2.0,.45),(0,1.0,-.2),420,(.84,.91,1),3.1,1.4)
    area('Soft ceiling fill',(0,2.99,.2),(0,0,0),105,(1,.88,.72),4.5,3.8)
    area('Wash bay cove',(-1.02,2.72,-3.05),(-1.02,1,-2.2),85,(1,.77,.50),4.2,.12)
    area('Front bounce',(0,2.4,3.15),(0,1,-1.5),35,(1,.9,.79),3,1.5)
    for x in [-2.15,.4,2.5]:
        for z in [-2,0,1.9]:area('Track luminaire',(x,2.63,z),(x,0,z),11,(1,.86,.67),.12)


def setup_renderer(args):
    scene=bpy.context.scene;scene.render.engine='CYCLES'
    scene.cycles.samples=args.samples;scene.cycles.use_denoising=True
    scene.cycles.max_bounces=8;scene.cycles.diffuse_bounces=4;scene.cycles.glossy_bounces=4
    scene.cycles.transparent_max_bounces=8;scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.025
    scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=95
    scene.render.resolution_percentage=100
    scene.render.film_transparent=False
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.67,.77,.9,1);bg.inputs['Strength'].default_value=.12
    try:scene.view_settings.view_transform='AgX'
    except TypeError:pass
    try:scene.view_settings.look='AgX - Medium High Contrast'
    except TypeError:pass
    scene.view_settings.exposure=-.25
    device='CPU'
    if not args.cpu:
        try:
            prefs=bpy.context.preferences.addons['cycles'].preferences
            prefs.compute_device_type='METAL';prefs.get_devices()
            available=[d for d in prefs.devices if d.type=='METAL']
            if available:
                for d in prefs.devices:d.use=d.type=='METAL'
                scene.cycles.device='GPU';device='METAL'
        except Exception as error:print('Metal unavailable; using CPU:',error)
    print('RENDER_DEVICE',device)
    return scene


def camera(name, location, target, panoramic=False):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    obj.location=xyz(location)
    obj.rotation_euler=(Vector(xyz(target))-obj.location).to_track_quat('-Z','Y').to_euler()
    data.clip_start=.03;data.clip_end=100
    if panoramic:data.type='PANO';data.panorama_type='EQUIRECTANGULAR'
    else:data.type='PERSP';data.lens=20;data.sensor_width=36
    return obj


def main():
    args=arguments();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    data=json.loads(Path(args.scene).read_text())
    if len(data['vertices'])%33:raise ValueError('Expected triangle vertex data with stride 11')
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    import_scene(data,args.future_bay);finish_room();
    if not args.future_bay:botanical_plant()
    scene=setup_renderer(args)
    views=[('hero',[.05,1.72,2.98],[-.30,1.30,-2.35],False),
           ('entrance',[0,1.65,2.9],[0,1.65,-2.5],True),
           ('wash',[-.7,1.65,.05],[-.7,1.65,-2.5],True),
           ('dry',[.5,1.65,1.8],[.5,1.65,-2.5],True)]
    metadata={'layout':'model.js export','coordinate_system':'source Y-up; Blender (x,-z,y)',
              'panorama_orientation':'All panorama centres face source -Z / north wash wall.',
              'status':'Concept lighting and finishes; same schematic equipment geometry.',
              'cameras':{}}
    for name,location,target,pano in views:
        cam=camera(name,location,target,pano);metadata['cameras'][name]={'position':location,'target':target,'panoramic':pano}
        if name=='hero':scene.camera=cam
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'pet-spa-cinematic.blend'))
    (out/'render-manifest.json').write_text(json.dumps(metadata,indent=2))
    if args.save_only:return
    for name,_,_,pano in views:
        if args.only not in ('all',name):continue
        scene.camera=bpy.data.objects[name]
        scene.render.resolution_x=args.width if pano else args.hero_width
        scene.render.resolution_y=args.width//2 if pano else round(args.hero_width*9/16)
        scene.render.filepath=str(out/(name+'.jpg'))
        print('RENDER_START',name,flush=True)
        try:bpy.ops.render.render(write_still=True)
        except RuntimeError:
            if scene.cycles.device!='GPU':raise
            print('GPU render failed; retrying same camera on CPU',flush=True)
            scene.cycles.device='CPU';bpy.ops.render.render(write_still=True)
        print('RENDER_DONE',name,flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'pet-spa-cinematic.blend'))

if __name__=='__main__':main()
