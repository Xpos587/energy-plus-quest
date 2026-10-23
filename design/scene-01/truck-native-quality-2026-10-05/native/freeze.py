import bpy,pathlib
O=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/native');bpy.ops.wm.open_mainfile(filepath=str(O/'scania-native-shape-v4-flush.blend'));s=bpy.context.scene
for o in list(bpy.data.objects):
 if 'Flush source cab door skin' in o.name:bpy.data.objects.remove(o,do_unlink=True)
s.camera=bpy.data.objects['shape-gate-front-three-quarter'];s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(O/'native-limitations-final.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-native-limited.blend'));bpy.ops.render.render(write_still=True)
