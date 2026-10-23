import bpy
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene;cam=s.camera
with bpy.data.libraries.load(str(P.parent/'fleet-native-v14-2026-10-07/fleet-v14-native.blend'),link=False)as(a,b):b.objects=[cam.name]
src=b.objects[0];cam.rotation_mode=src.rotation_mode;cam.location=src.location;cam.rotation_euler=src.rotation_euler;cam.scale=src.scale;cam.matrix_parent_inverse=src.matrix_parent_inverse;bpy.data.objects.remove(src,do_unlink=True);s.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v15-readable.blend'))
