import bpy
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
s.frame_set(1);s.render.resolution_x=1008;s.render.resolution_y=700;s.render.resolution_percentage=100
layer=s.view_layers[0];layer.use_pass_z=True;layer.use_pass_normal=True;layer.use_pass_cryptomatte_object=True
s.render.image_settings.media_type='MULTI_LAYER_IMAGE';s.render.filepath=str(p/'first-frame-geometry.exr')
bpy.ops.render.render(write_still=True)
