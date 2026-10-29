"""Non-destructive image-only OIDN filter for a linear lightmap EXR.
Blender -b --factory-startup --python scripts/denoise-browser-lightmap.py -- --source INPUT.exr --output OUTPUT.png
"""
import argparse
from pathlib import Path
import sys
import bpy

p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.source).resolve();output=Path(a.output).resolve()
if source==output or output.exists():raise RuntimeError('Output must be a new file; original atlas is preserved.')
image=bpy.data.images.load(str(source));image.colorspace_settings.name='Linear Rec.709'
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=image.size[0];scene.render.resolution_y=image.size[1];scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.render.compositor_device='CPU';scene.render.compositor_denoise_device='CPU';scene.render.use_compositing=True
# Blender 5.2 uses a compositor node group attached to the Scene.
graph=bpy.data.node_groups.new('Lightmap image-only OIDN','CompositorNodeTree');graph.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');scene.compositing_node_group=graph
input_node=graph.nodes.new('CompositorNodeImage');input_node.image=image
denoise=graph.nodes.new('CompositorNodeDenoise');denoise.inputs['HDR'].default_value=True
out_node=graph.nodes.new('NodeGroupOutput');graph.links.new(input_node.outputs['Image'],denoise.inputs['Image']);graph.links.new(denoise.outputs['Image'],out_node.inputs['Image'])
# Camera is only a render trigger. Compositor uses the input image at native size.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
cam_data=bpy.data.cameras.new('Compositor trigger');cam=bpy.data.objects.new('Compositor trigger',cam_data);scene.collection.objects.link(cam);scene.camera=cam
output.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(output);bpy.ops.render.render(write_still=True)
print('DENOISE_DONE',str(output),list(image.size),flush=True)
