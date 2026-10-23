import bpy,pathlib
p=pathlib.Path(__file__).resolve().parent/'green-tractor-turn.blend';bpy.ops.wm.open_mainfile(filepath=str(p));bpy.ops.file.pack_all();bpy.context.scene.frame_set(42);bpy.ops.wm.save_as_mainfile(filepath=str(p));print('Texture packing:',[(i.name,bool(i.packed_file)) for i in bpy.data.images if i.type!='RENDER_RESULT'])
