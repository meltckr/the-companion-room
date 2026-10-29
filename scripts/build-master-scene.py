"""Build the single detailed pet-spa master, render it, and export browser geometry.

Blender --background --python scripts/build-master-scene.py -- \
 --out assets/cinematic --export evidence/master-scene.json --only hero --samples 64

All views and browser geometry derive from this scene. Equipment remains a generic
concept; dimensions, ramp pitch, clearances and specifications need design review.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector

spec=importlib.util.spec_from_file_location('cinematic',Path(__file__).with_name('render-cinematic.py'))
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
GROUP='all'
M={}


def args_parse():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--export');p.add_argument('--samples',type=int,default=64);p.add_argument('--width',type=int,default=3840);p.add_argument('--hero-width',type=int,default=2560);p.add_argument('--only',default='all',choices=['all','hero','closeup','rinse','overview','entrance','wash','dry']);p.add_argument('--save-only',action='store_true');p.add_argument('--cpu',action='store_true');p.add_argument('--future-bay',action='store_true')
 return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def mark(obj,mat=None,group=None):
 obj['viewer_group']=group or GROUP
 if mat:obj.data.materials.append(mat)
 return obj


def mat(name,rgb,rough=.5,metal=0,kind=0):
 m,b=R.material(name,rgb,rough,metal);m['viewer_color']=list(rgb);m['viewer_rough']=rough;m['viewer_kind']=kind;M[name]=m
 return m,b


def materials():
 mat('forest',(.15,.255,.205),.37)
 mat('shadow',(.065,.10,.083),.5)
 mat('bronze',(.33,.29,.20),.32,.65)
 m,b=mat('stainless',(.67,.71,.70),.26,.92)
 b.inputs['Anisotropic'].default_value=.35
 m,b=mat('rubber',(.12,.15,.14),.82)
 mat('porcelain',(.78,.75,.69),.4,kind=1)
 mat('limestone',(.76,.73,.67),.5)
 mat('plaster',(.9,.88,.83),.82,kind=3)
 mat('oak',(.58,.43,.29),.43,kind=2)
 mat('oak_edge',(.43,.31,.20),.49,kind=2)
 mat('grout',(.45,.46,.42),.9)
 mat('linen',(.89,.88,.81),.92)
 mat('bottle',(.32,.39,.30),.3)
 mat('amber',(.43,.24,.09),.26)
 mat('label',(.88,.85,.75),.68)
 mat('stop',(.55,.23,.16),.4)
 m,b=mat('led',(.99,.89,.67),.2,kind=5);b.inputs['Emission Color'].default_value=(1,.75,.46,1);b.inputs['Emission Strength'].default_value=3
 m,b=mat('glass',(.81,.88,.91),.06,kind=4);b.inputs['Transmission Weight'].default_value=1;b.inputs['IOR'].default_value=1.0
 m,b=mat('frost',(.76,.83,.82),.4,kind=4);b.inputs['Transmission Weight'].default_value=.7;b.inputs['IOR'].default_value=1.45
 for name,scale,bumpdist,strength in [('stainless',(500,500,2),.000025,.12),('oak',(65,65,.8),.00055,.18),('oak_edge',(60,60,.7),.0005,.18),('porcelain',(2,2,2),.00045,.14),('limestone',(3,3,3),.0005,.12),('plaster',(75,75,75),.0002,.09),('linen',(180,180,180),.001,.55),('rubber',(80,80,80),.0008,.2)]:
  m=M[name];n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF')
  tex=n.new('ShaderNodeTexCoord');mul=n.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=scale;l.new(tex.outputs['Object'],mul.inputs[0])
  noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2;noise.inputs['Detail'].default_value=3;l.new(mul.outputs['Vector'],noise.inputs['Vector'])
  bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=bumpdist;bump.inputs['Strength'].default_value=strength;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],b.inputs['Normal'])
  if name in ('oak','oak_edge','porcelain','limestone'):
   ramp=n.new('ShaderNodeValToRGB');base=b.inputs['Base Color'].default_value[:];low=.76 if name.startswith('oak') else .92;high=1.08 if name.startswith('oak') else 1.025
   ramp.color_ramp.elements[0].color=tuple(v*low for v in base[:3])+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,v*high) for v in base[:3])+(1,)
   l.new(noise.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],b.inputs['Base Color'])


def photographic_maps():
 root=Path(__file__).resolve().parent.parent/'assets'/'materials'
 for name,asset,scale,warm in [('porcelain','marble_01',.65,True),('limestone','marble_01',.65,True),('oak','oak_veneer_01',.7,False),('oak_edge','oak_veneer_01',.7,False)]:
  m=M[name];nodes=m.node_tree.nodes;links=m.node_tree.links;bsdf=nodes.get('Principled BSDF')
  tc=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=.16 if warm else scale;links.new(tc.outputs['Generated'] if warm else tc.outputs['Object'],mapping.inputs[0])
  if warm:
   crop=nodes.new('ShaderNodeVectorMath');crop.operation='ADD';crop.inputs[1].default_value=(.25,.25,.25);links.new(mapping.outputs['Vector'],crop.inputs[0]);mapping=crop
  tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(root/(asset+('_diff_4k.jpg' if warm else '_diff_1k.jpg'))),check_existing=True);tex.projection='BOX';tex.projection_blend=.12;links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
  tint=nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=.35 if warm else .45;tint.inputs[2].default_value=(.85,.80,.70,1) if warm else (.55,.42,.30,1);links.new(tex.outputs['Color'],tint.inputs[1]);links.new(tint.outputs[0],bsdf.inputs['Base Color'])
  rough=nodes.new('ShaderNodeTexImage');rough.image=bpy.data.images.load(str(root/(asset+'_rough_1k.jpg')),check_existing=True);rough.image.colorspace_settings.name='Non-Color';rough.projection='BOX';rough.projection_blend=.12;links.new(mapping.outputs['Vector'],rough.inputs['Vector'])
  remap=nodes.new('ShaderNodeMapRange');remap.inputs['To Min'].default_value=.29 if warm else .35;remap.inputs['To Max'].default_value=.52;links.new(rough.outputs['Color'],remap.inputs['Value']);links.new(remap.outputs[0],bsdf.inputs['Roughness'])
  bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.0007;links.new(rough.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])


def box(name,p,d,material='forest',bevel=.008):
 obj=R.cube(name,p,d,M[material],bevel);mark(obj)
 if bevel:
  obj.modifiers[-1].segments=3
  norm=obj.modifiers.new('Weighted highlights','WEIGHTED_NORMAL');norm.keep_sharp=True
 return obj


def rod(name,a,b,r,material='stainless',vertices=20):
 a=Vector(R.xyz(a));b=Vector(R.xyz(b));v=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=v.length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();mark(o,M[material])
 for poly in o.data.polygons:poly.use_smooth=len(poly.vertices)==4
 return o


def curve(name,points,r,material='stainless',resolution=12):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=resolution;data.bevel_depth=r;data.bevel_resolution=3
 s=data.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for bp,p in zip(s.bezier_points,points):bp.co=R.xyz(p);bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);return mark(obj,M[material])


def torus(name,p,major,minor,material='stainless',rotation=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=R.xyz(p),major_radius=major,minor_radius=minor)
 o=bpy.context.object;o.name=name;o.rotation_euler=rotation;mark(o,M[material])
 for poly in o.data.polygons:poly.use_smooth=True
 return o


def text(name,body,p,size,material='bronze'):
 data=bpy.data.curves.new(name,'FONT');data.body=body;data.align_x='CENTER';data.size=size;data.extrude=.0008;data.bevel_depth=.0003
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=R.xyz(p);o.rotation_euler=(math.pi/2,0,0);return mark(o,M[material])


def cabinetry(name,p,d,doors=2,material='forest'):
 x,y,z=p;w,h,depth=d
 box(name+' carcass',(x,y,z),(w,h,depth),'shadow',.012)
 box(name+' toe kick',(x,y-h/2+.065,z+.035),(w-.12,.13,depth-.08),'shadow',.006)
 width=(w-.025*(doors+1))/doors
 for i in range(doors):
  dx=x-w/2+.025+width/2+i*(width+.025)
  box(name+' door',(dx,y+.05,z+depth/2+.012),(width,h-.15,.035),material,.006)
  rod(name+' handle',(dx+width/2-.075,y+.07,z+depth/2+.05),(dx+width/2-.075,y+.29,z+depth/2+.05),.008,'bronze',12)
 box(name+' top',(x,y+h/2+.035,z),(w+.035,.07,depth+.045),'limestone',.012)


def pump(p,material='bottle'):
 x,y,z=p
 rod('Amenity bottle',(x,y,z),(x,y+.18,z),.043,material,24)
 box('Bottle label',(x,y+.10,z+.041),(.052,.07,.006),'label',.002)
 rod('Bottle neck',(x,y+.18,z),(x,y+.215,z),.015,'shadow',16)
 box('Metered pump',(x+.022,y+.221,z),(.065,.015,.024),'shadow',.006)


def towel(p,rolled=False):
 x,y,z=p
 if rolled:
  rod('Rolled towel',(x-.13,y+.065,z),(x+.13,y+.065,z),.064,'linen',28)
  torus('Towel roll end',(x-.132,y+.065,z),.042,.009,'linen',(0,math.pi/2,0))
  torus('Towel roll inner',(x-.134,y+.065,z),.022,.007,'linen',(0,math.pi/2,0))
 else:
  for i in range(3):box('Folded towel',(x,y+.022+i*.043,z),(.42,.041,.27),'linen',.016)


def ramp(x,z):
 # Animal ramp is a design concept, not an accessibility certification.
 width=.67;length=1.52;rise=.45;a=z+.42;b=a+length
 verts=[(x-width/2,.025,b),(x+width/2,.025,b),(x+width/2,rise,a),(x-width/2,rise,a)]
 mesh=bpy.data.meshes.new('Animal ramp');mesh.from_pydata([R.xyz(v) for v in verts],[],[(0,1,2,3)]);mesh.update()
 o=bpy.data.objects.new('Continuous nonslip ramp',mesh);bpy.context.collection.objects.link(o);mark(o,M['rubber'])
 solid=o.modifiers.new('Ramp thickness','SOLIDIFY');solid.thickness=.025
 bevel=o.modifiers.new('Ramp edges','BEVEL');bevel.width=.006;bevel.segments=3
 for i in range(1,13):
  t=i/13;box('Ramp traction',(x,.027+(rise-.025)*(1-t),a+length*t),(width-.04,.015,.022),'shadow',.004)
 for side in [-1,1]:curve('Ramp side rail',[(x+side*width/2,rise+.025,a),(x+side*width/2,.065,b)],.016)


def washbay(x,z,w=1.72,label='01'):
 # Rounded fabricated surfaces, hollow basin, low entry and accessible service face.
 box('Wash unit plinth',(x,.15,z),(w-.08,.27,.76),'shadow',.015)
 box('Wash unit housing',(x,.25,z),(w,.42,.84),'forest',.035)
 for side in [-1,1]:box('Service face',(x+side*.51,.25,z+.435),(.39,.31,.028),'forest',.008)
 box('Service hatch',(x+w/2+.012,.25,z),(.025,.30,.56),'stainless',.006)
 for i in range(6):box('Service vent',(x+w/2+.03,.15+i*.028,z),(.009,.008,.28),'shadow',.002)
 box('Wash basin floor',(x,.45,z),(w-.06,.055,.83),'stainless',.025)
 box('Nonslip basin mat',(x,.482,z),(w-.19,.018,.63),'rubber',.022)
 for i in range(11):box('Basin drainage grooves',(x-.62+i*.124,.493,z),(.012,.005,.52),'shadow',.002)
 for side in [-1,1]:box('Rounded side splash',(x+side*(w/2-.025),.76,z),(.055,.61,.85),'stainless',.025)
 box('Rounded back splash',(x,.94,z-.40),(w,1.02,.065),'stainless',.028)
 wing=(w-.7)/2
 for side in [-1,1]:box('Front splash wing',(x+side*(.35+wing/2),.76,z+.4),(wing,.61,.065),'stainless',.025)
 # Brushed rounded tubular edges catch soft reflections.
 for side in [-1,1]:curve('Rolled tub rim',[(x+side*(w/2-.025),1.07,z+.36),(x+side*(w/2-.025),1.07,z-.35)],.018)
 box('Control surround',(x,1.30,z-.345),(.53,.30,.07),'stainless',.023)
 box('Control panel',(x,1.30,z-.303),(.48,.25,.018),'shadow',.018)
 text('Unit number',label,(x,1.50,z-.36),.09,'bronze')
 text('Mode legend','WASH   RINSE   DRY',(x,1.365,z-.286),.023,'label')
 for i in range(4):rod('Control button',(x-.15+i*.1,1.27,z-.28),(x-.15+i*.1,1.27,z-.26),.024,'stop' if i==3 else 'bronze',24)
 # Slim wash hose and separate larger flexible dry hose.
 curve('Wash spray hose',[(x-.54,1.35,z-.28),(x-.68,1.07,z-.19),(x-.41,.94,z-.13),(x-.28,1.25,z-.16)],.012,'shadow',18)
 rod('Wash spray handle',(x-.28,1.25,z-.16),(x-.28,1.40,z-.11),.021,'stainless',20)
 rod('Wash spray head',(x-.28,1.40,z-.11),(x-.28,1.39,z-.035),.029,'stainless',20)
 points=[(x+.57,1.4,z-.29),(x+.66,1.16,z-.21),(x+.56,.92,z-.03),(x+.31,.98,z+.12),(x+.31,1.22,z+.16)]
 curve('Dryer flexible hose',points,.032,'shadow',20)
 # Corrugations follow an interpolated polyline, discreet at normal view distance.
 for a,b in zip(points,points[1:]):
  va=Vector(a);vb=Vector(b);v=vb-va;n=max(2,round(v.length/.028))
  for i in range(n):
   p=va+v*(i/n);q=p+v.normalized()*.008;rod('Dryer hose rib',p,q,.036,'rubber',12)
 rod('Dryer nozzle',(x+.31,1.22,z+.16),(x+.22,1.27,z+.34),.048,'shadow',24)
 rod('Dryer nozzle tip',(x+.22,1.27,z+.34),(x+.20,1.28,z+.38),.035,'shadow',24)
 box('Shampoo shelf',(x-.59,1.46,z-.39),(.30,.035,.12),'stainless',.008)
 pump((x-.65,1.48,z-.37));pump((x-.52,1.48,z-.37),'amber')
 ramp(x,z)


def room():
 global GROUP
 GROUP='all';box('Foundation',(0,-.15,0),(7.5,.25,6.9),'shadow',.025)
 # Large rectangular porcelain, finely beveled with real joints.
 box('Tile bedding',(0,-.015,0),(7.3152,.045,6.7056),'grout',0)
 for row in range(6):
  z0=-3.3528+row*1.1176
  for col in range(12):
   x0=-3.6576+col*.6096
   box('Porcelain slab',(x0+.3048,.016,z0+.5588),(.6056,.045,1.1136),'porcelain',.002)
 GROUP='back';box('North backdrop wall',(0,1.5,-3.42),(7.48,3,.14),'forest',.005)
 GROUP='left';box('West backdrop wall',(-3.73,1.5,0),(.14,3,6.84),'forest',.005)
 GROUP='right';box('East lower wall',(3.73,.51,0),(.14,1.02,6.84),'limestone',.005);box('East upper wall',(3.73,2.87,0),(.14,.26,6.84),'limestone',.005)
 for z,d in [(-2.64,1.42),(2.7,1.3)]:box('East window pier',(3.73,1.87,z),(.14,1.7,d),'limestone',.005)
 box('Upper clear glazing',(3.69,2.14,.06),(.025,1.09,3.96),'glass',.001)
 box('Lower privacy glazing',(3.69,1.32,.06),(.025,.55,3.96),'frost',.001)
 for z in [-1.94,.06,2.06]:box('Bronze window mullion',(3.65,1.87,z),(.09,1.73,.037),'bronze',.005)
 box('Window sill',(3.59,1.01,.06),(.25,.07,4.16),'oak',.009)
 GROUP='back'
 # Two warm honed-stone wash niches, with slender oak frames and lit shelves.
 for x in [-2.05,.15]:
  box('Honed stone wash backdrop',(x,1.6,-3.32),(2.03,2.75,.055),'limestone',.008)
  for y in [.9,1.8,2.7]:box('Stone horizontal joint',(x,y,-3.285),(2.02,.003,.004),'grout',0)
  box('Oak amenity shelf',(x,1.90,-3.12),(1.98,.055,.37),'oak',.01)
  box('Shelf concealed light',(x,1.868,-3.05),(1.86,.012,.06),'led',.003)
  for dx in [-.72,.72]:pump((x+dx,1.932,-3.08),'amber')
 for x in [-3.15,-.95,1.25]:
  for i in range(4):box('Oak niche pilaster',(x-.075+i*.05,1.52,-3.23),(.026,2.96,.15),'oak',.005)
 box('Upper cove fascia',(-.95,2.98,-3.18),(4.65,.08,.25),'forest',.005)
 box('Upper concealed wash light',(-.95,2.93,-3.20),(4.5,.012,.1),'led',.002)
 GROUP='left'
 box('Paw rinse oak backing',(-3.64,1.64,1.55),(.045,2.7,1.6),'oak_edge',.004)
 for i in range(20):box('Paw rinse oak slat',(-3.60,1.64,.80+i*.079),(.055,2.7,.032),'oak',.005)
 GROUP='all'
 for p,d in [((0,.08,-3.32),(7.3,.13,.035)),((-3.63,.08,0),(.035,.13,6.7)),((3.63,.08,0),(.035,.13,6.7))]:box('Coved skirting',p,d,'limestone',.012)
 box('Bay splash divider',(-.95,.95,-2.22),(.08,1.86,1.48),'forest',.025)
 for i in range(8):box('Bay divider slat',(-.95,2.43,-2.88+i*.19),(.05,1.12,.033),'oak',.007)
 GROUP='interior'
 box('Ceiling',(0,3.08,0),(7.48,.14,6.87),'plaster',.005)
 for x in [-2.15,.4,2.5]:
  for z in [-2,0,1.9]:
   rod('Recessed downlight trim',(x,3.004,z),(x,2.99,z),.075,'bronze',28)
   rod('Recessed downlight lens',(x,2.99,z),(x,2.984,z),.062,'led',28)
 for x in [-2.12,2.12]:box('Entry return',(x,1.5,3.42),(3.08,3,.14),'limestone',.005)['hero_cutaway']=True
 box('Entry header',(0,2.77,3.42),(1.16,.46,.14),'limestone',.005)['hero_cutaway']=True
 box('Entry door',(0,1.26,3.45),(1.10,2.52,.055),'oak',.012)['hero_cutaway']=True
 rod('Entry handle',(.42,1.02,3.405),(.42,1.28,3.405),.012,'bronze',16)['hero_cutaway']=True
 GROUP='all'


def amenities():
 global GROUP
 washbay(-2.05,-2.5,label='01');washbay(.15,-2.5,label='02')
 cabinetry('Care supplies',(-3.02,1.05,-.35),(1.04,2.04,.68))
 # Paw rinse deliberately shallow, with opening facing the central circulation.
 box('Paw rinse base',(-2.84,.11,1.55),(1.02,.18,1.08),'stainless',.045)
 box('Paw rinse mat',(-2.84,.21,1.55),(.88,.025,.93),'rubber',.025)
 box('Paw rinse back',(-3.31,.52,1.55),(.055,.80,1.08),'stainless',.024)
 for z in [1.04,2.06]:box('Paw rinse side',(-2.84,.34,z),(1.02,.45,.05),'stainless',.024)
 curve('Paw rinse spray',[(-3.24,.95,1.25),(-3.18,.53,1.48),(-3.13,.80,1.81)],.013,'shadow',16)
 rod('Paw spray handle',(-3.13,.8,1.81),(-3.13,1.02,1.81),.023)
 box('Paw landing',(-2.05,.025,1.55),(.48,.035,.92),'rubber',.018)
 cabinetry('Finishing cabinet',(2.99,.43,.28),(1.0,.80,2.03),doors=2)
 # Rotate visible door fronts to face aisle by building additional precise paneling.
 for z in [-.21,.77]:
  box('Finishing aisle door',(2.47,.46,z),(.035,.65,.94),'forest',.008)
  rod('Finishing pull',(2.44,.56,z+.26),(2.44,.75,z+.26),.008,'bronze',12)
 box('Finishing stone worktop',(2.96,.9,.28),(1.10,.065,2.13),'limestone',.014)
 towel((2.95,.94,.90));towel((2.95,.94,.40),True);towel((2.95,1.04,.40),True)
 box('Brush head',(2.72,.96,-.38),(.12,.035,.18),'oak',.04)
 box('Brush handle',(2.72,.96,-.23),(.04,.03,.17),'oak',.014)
 for i in range(4):
  for j in range(6):rod('Brush bristle',(2.685+i*.023,.98,-.44+j*.024),(2.685+i*.023,1.01,-.44+j*.024),.002,'shadow',6)
 # Entry conveniences and restrained retail cabinet.
 box('Bench seat',(1.55,.49,2.85),(1.08,.10,.46),'oak',.025)
 for x in [1.12,1.98]:box('Bench leg',(x,.245,2.85),(.045,.45,.34),'bronze',.007)
 box('Coat rail',(-1.6,1.56,3.29),(1.1,.12,.045),'oak',.01)['hero_cutaway']=True
 for x in [-1.97,-1.6,-1.23]:curve('Coat hook',[(x,1.6,3.24),(x,1.5,3.15),(x,1.54,3.10)],.009,'bronze',12)['hero_cutaway']=True
 box('Phone shelf',(-1.6,1.21,3.18),(1.1,.045,.23),'oak',.01)['hero_cutaway']=True
 cabinetry('Optional retail base',(2.95,.43,2.76),(.74,.8,.40),doors=1)
 box('Retail backing',(2.95,1.49,2.94),(.74,1.23,.05),'forest',.008)
 for x in [2.59,3.31]:box('Retail side',(x,1.49,2.76),(.025,1.23,.40),'forest',.006)
 for y in [.88,1.27,1.66,2.09]:box('Retail shelf',(2.95,y,2.76),(.74,.035,.40),'oak',.006)
 for y in [.90,1.29,1.68]:
  for x in [2.73,2.95,3.17]:pump((x,y,2.66),'amber' if x==2.95 else 'bottle')
 box('Retail light',(2.95,2.06,2.58),(.64,.012,.03),'led',.002)
 box('Entrance mat',(0,.026,2.9),(1.48,.035,.72),'rubber',.02)
 for x in [-2.05,.15]:
  box('Linear drain',(x,.045,-.47),(1.7,.025,.065),'stainless',.005)
  for i in range(25):box('Drain slot',(x-.8+i*.066,.06,-.47),(.023,.004,.043),'shadow',.002)
 GROUP='flex'
 box('Future bay reserve',(2.72,.04,-2.28),(1.62,.04,1.53),'porcelain',.012)
 box('Alcove bench',(2.7,.48,-2.88),(1.44,.09,.40),'oak',.025)
 for x in [2.12,3.28]:box('Alcove leg',(x,.25,-2.88),(.05,.44,.31),'bronze',.006)
 rod('Ceramic planter',(3.05,.07,-1.9),(3.05,.43,-1.9),.20,'limestone',48)
 before=set(bpy.data.objects);R.botanical_plant()
 for o in set(bpy.data.objects)-before:
  mark(o)
  if o.type in ('MESH','CURVE'):
   for m in o.data.materials:
    if 'viewer_color' not in m:
     m['viewer_color']=[.20,.35,.16];m['viewer_rough']=.4;m['viewer_kind']=0
 GROUP='future';washbay(2.70,-2.5,w=1.62,label='03');GROUP='all'


def lighting():
 # Lighting balanced for room-scale depth and warm highlights without white clipping.
 R.area('Window soft daylight',(4.15,2.05,.05),(0,1.0,-.6),440,(.84,.91,1),3.8,1.5)
 R.area('Ceiling bounce',(0,2.99,.2),(0,0,0),95,(1,.89,.75),4.2,3.6)
 R.area('Upper stone wash',(-.97,2.91,-3.10),(-.97,1.9,-3.28),75,(1,.76,.49),4.5,.10)
 for x in [-2.05,.15]:R.area('Under shelf stone wash',(x,1.86,-3.0),(x,.95,-3.25),22,(1,.78,.52),1.84,.08)
 R.area('Metal reflection softbox',(-2.8,2.2,.4),(-.9,.9,-2.5),80,(1,.9,.78),1.4,2.0)
 R.area('Entry soft fill',(0,2.2,3.22),(0,1,-1.5),35,(1,.91,.8),2.8,1.3)
 for x in [-2.15,.4,2.5]:
  for z in [-2,0,1.9]:R.area('Recessed pool',(x,2.98,z),(x,0,z),13,(1,.85,.65),.12)
 # A plain luminous exterior plane gives a neutral winter outlook, never a fake site.
 sky,b=mat('winter_sky',(.78,.85,.90),.9);b.inputs['Emission Color'].default_value=(.60,.72,.84,1);b.inputs['Emission Strength'].default_value=.32
 backdrop=box('Neutral winter outlook',(6.8,2,.05),(.08,30,60),'winter_sky',0);backdrop['viewer_skip']=True
 # Area-light rectangles must illuminate the room without appearing as white
 # polygons through the architectural glazing.
 for light in bpy.context.scene.objects:
  if light.type=='LIGHT':light.visible_camera=False;light.visible_transmission=False


def export_browser(path):
 graph=bpy.context.evaluated_depsgraph_get();vertices=[];items=[]
 for obj in bpy.context.scene.objects:
  if obj.type not in ('MESH','CURVE','FONT') or obj.get('viewer_skip'):continue
  # Simplification affects only the browser export; the render master keeps its bevels.
  simplify=None
  if obj.type=='MESH':
   simplify=obj.modifiers.new('Temporary browser LOD','DECIMATE');simplify.ratio=.38
   graph.update()
  evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();start=len(vertices)//11
  normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
  for tri in mesh.loop_triangles:
   material=obj.data.materials[tri.material_index] if len(obj.data.materials)>tri.material_index else M['plaster']
   rgb=material.get('viewer_color',[.7,.7,.65]);rough=material.get('viewer_rough',.6);kind=material.get('viewer_kind',0)
   for li in tri.loops:
    loop=mesh.loops[li];v=obj.matrix_world@mesh.vertices[loop.vertex_index].co
    n=normal_matrix@mesh.corner_normals[li].vector;n.normalize()
    vertices.extend(round(float(a),5) for a in (v.x,v.z,-v.y,n.x,n.z,-n.y,*rgb,rough,kind))
  count=len(vertices)//11-start
  if count:items.append({'start':start,'count':count,'group':obj.get('viewer_group','all')})
  evaluated.to_mesh_clear()
  if simplify:obj.modifiers.remove(simplify)
 output=Path(path);output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps({'vertices':vertices,'items':items},separators=(',',':')))
 print('BROWSER_EXPORT',len(vertices)//11,'vertices',len(items),'items',output,flush=True)


def main():
 args=args_parse();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 materials();photographic_maps();room();amenities();lighting();scene=R.setup_renderer(args);scene.view_settings.exposure=-.2
 for obj in scene.objects:
  if obj.get('hero_cutaway'):obj['viewer_group']='interior'
 bpy.ops.file.pack_all()
 # Shared scene / different cameras; no photo substitutions.
 views=[('hero',[0,1.75,4.7],[0,1.15,-1.7],False),('closeup',[-.75,1.52,-.05],[-1.9,1.0,-2.5],False),('rinse',[-.45,1.48,2.7],[-2.85,.68,1.5],False),('overview',[8,7.5,9],[0,.7,0],False),('entrance',[0,1.65,2.9],[0,1.65,-2.5],True),('wash',[-.7,1.65,.05],[-.7,1.65,-2.5],True),('dry',[.5,1.65,1.8],[.5,1.65,-2.5],True)]
 for name,pos,target,pano in views:
  c=R.camera(name,pos,target,pano)
  if not pano:c.data.lens=18 if name=='hero' else (38 if name=='overview' else 26)
 for obj in scene.objects:
  g=obj.get('viewer_group');obj.hide_render=(g=='future' and not args.future_bay) or (g=='flex' and args.future_bay)
 if args.export:export_browser(args.export)
 scene.camera=bpy.data.objects['hero'];bpy.ops.wm.save_as_mainfile(filepath=str(out/'pet-spa-master.blend'))
 (out/'master-manifest.json').write_text(json.dumps({'source':'scripts/build-master-scene.py','geometry':'One detailed master for stills, panoramas and browser export','cameras':{n:{'position':p,'target':t,'panoramic':v} for n,p,t,v in views},'panorama_orientation':'All panorama centers face source -Z / north.','note':'Generic equipment and neutral winter outlook; architectural concept.'},indent=2))
 if args.save_only:return
 for name,_,_,pano in views:
  if args.only not in ('all',name):continue
  for obj in scene.objects:
   g=obj.get('viewer_group');obj.hide_render=(g=='future' and not args.future_bay) or (g=='flex' and args.future_bay) or (name=='overview' and g in ('interior','right')) or (name=='hero' and obj.get('hero_cutaway',False))
  scene.camera=bpy.data.objects[name];scene.render.resolution_x=args.width if pano else args.hero_width;scene.render.resolution_y=args.width//2 if pano else round(args.hero_width*9/16);scene.render.filepath=str(out/(name+'.jpg'));print('RENDER_START',name,flush=True)
  try:bpy.ops.render.render(write_still=True)
  except RuntimeError:
   if scene.cycles.device!='GPU':raise
   scene.cycles.device='CPU';bpy.ops.render.render(write_still=True)
  print('RENDER_DONE',name,flush=True)
 for obj in scene.objects:
  g=obj.get('viewer_group');obj.hide_render=(g=='future' and not args.future_bay) or (g=='flex' and args.future_bay)
 scene.camera=bpy.data.objects['hero']
 bpy.ops.wm.save_as_mainfile(filepath=str(out/'pet-spa-master.blend'))

if __name__=='__main__':main()
