"""Bake a disposable copy of the master into a shared diffuse-light atlas.
Blender -b --python scripts/bake-browser-lightmap.py -- --source MASTER.blend --out /private/tmp/pet-spa-lightmap-proof --size 2048 --samples 32
Original objects stay separate during baking to preserve Generated/Object material
coordinates and per-object variation. Export concatenates their evaluated triangles.
"""
import argparse
import json
import sys
import time
from pathlib import Path
import bpy


def main():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--size',type=int,default=2048);p.add_argument('--samples',type=int,default=32);p.add_argument('--cpu',action='store_true')
 a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);started=time.time()
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.source).resolve()))
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=a.samples
 scene.cycles.use_denoising=True;scene.cycles.device='CPU'
 if not a.cpu:
  pref=bpy.context.preferences.addons['cycles'].preferences
  try:
   pref.compute_device_type='METAL';pref.get_devices()
   for dev in pref.devices:dev.use=dev.type=='METAL'
   if any(dev.type=='METAL' for dev in pref.devices):scene.cycles.device='GPU'
  except Exception as e:print('METAL unavailable:',e,flush=True)
 # The saved master can contain camera-dependent cutaway flags; restore full room.
 objects=[];future=[]
 for obj in list(scene.objects):
  if obj.type not in ('MESH','CURVE','FONT') or obj.get('viewer_skip'):continue
  obj.hide_set(False);obj.hide_viewport=False
  obj.hide_render=obj.get('viewer_group')=='future'
  (future if obj.hide_render else objects).append(obj)
 bpy.ops.object.select_all(action='DESELECT')
 for obj in objects+future:obj.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.object.convert(target='MESH')
 objects=[bpy.data.objects[o.name] for o in objects];future=[bpy.data.objects[o.name] for o in future]
 bpy.ops.object.select_all(action='DESELECT')
 for obj in objects:obj.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
 bpy.ops.uv.smart_project(angle_limit=1.151917,island_margin=.003,area_weight=1.0,correct_aspect=True,scale_to_bounds=True)
 bpy.ops.object.mode_set(mode='OBJECT')
 image=bpy.data.images.new('Spa diffuse illumination',width=a.size,height=a.size,alpha=False,float_buffer=True)
 image.colorspace_settings.name='Linear Rec.709'
 materials={m for obj in objects for m in obj.data.materials if m}
 for mat in materials:
  mat.use_nodes=True;node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.name='SPA_BAKE_TARGET';node.image=image
  for n in mat.node_tree.nodes:n.select=False
  node.select=True;mat.node_tree.nodes.active=node
 scene.render.bake.use_clear=True;scene.render.bake.margin=8;scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True;scene.render.bake.use_pass_color=True
 print('BAKE_START',len(objects),'objects',a.size,'pixels',scene.cycles.device,flush=True)
 bpy.ops.object.bake(type='DIFFUSE',pass_filter={'DIRECT','INDIRECT','COLOR'},use_clear=True,margin=8)
 # Save raw radiance as linear EXR plus standard display sRGB PNG (no AgX baked in).
 scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='16'
 image.save_render(str(out/'diffuse-light.exr'),scene=scene)
 scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8'
 image.save_render(str(out/'diffuse-light.png'),scene=scene)
 vertices=[];items=[]
 for obj in objects+future:
  mesh=obj.data;mesh.calc_loop_triangles();uv=mesh.uv_layers.active.data if mesh.uv_layers.active else None;matrix=obj.matrix_world;normalmatrix=matrix.to_3x3().inverted().transposed();start=len(vertices)//14
  for tri in mesh.loop_triangles:
   mat=mesh.materials[tri.material_index] if mesh.materials else None
   color=mat.get('viewer_color',[.7,.7,.65]) if mat else [.7,.7,.65];rough=mat.get('viewer_rough',.6) if mat else .6;kind=mat.get('viewer_kind',0) if mat else 0
   for loopidx in tri.loops:
    loop=mesh.loops[loopidx];pos=matrix@mesh.vertices[loop.vertex_index].co;normal=(normalmatrix@mesh.corner_normals[loopidx].vector).normalized()
    tex=uv[loopidx].uv if uv and obj not in future else (-1,-1)
    vertices.extend([round(pos.x,5),round(pos.z,5),round(-pos.y,5),round(normal.x,5),round(normal.z,5),round(-normal.y,5),*color,rough,kind,1.0,round(tex[0],6),round(tex[1],6)])
  count=len(vertices)//14-start
  if count:items.append({'start':start,'count':count,'group':obj.get('viewer_group','all')})
 metadata={'stride':14,'vertices':vertices,'items':items,'lightmap':{'source':str(Path(a.source).resolve()),'png':'diffuse-light.png','exr':'diffuse-light.exr','pngColorSpace':'sRGB','exrColorSpace':'linear Rec.709','viewTransform':'Standard','passes':['DIFFUSE_DIRECT','DIFFUSE_INDIRECT','DIFFUSE_COLOR'],'samples':a.samples,'size':a.size,'ao': '1.0 because actual diffuse lighting already contains occlusion; do not multiply ambient/diffuse lighting again','futureUvSentinel':-1}}
 (out/'scene-lightmapped.json').write_text(json.dumps(metadata,separators=(',',':')))
 print('BAKE_DONE',len(vertices)//14,'vertices',round(time.time()-started,1),'seconds',flush=True)

if __name__=='__main__':main()
