import bpy,pathlib,math,json
O=pathlib.Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'green-tractor-turn.blend'));s=bpy.context.scene
mesh=bpy.data.objects['New textured whole green 6x4 tractor'];mesh.rotation_mode='XYZ';mesh.rotation_euler=(0,0,math.pi);s.camera.data.ortho_scale*=1.2
s.render.engine='BLENDER_EEVEE';s.render.fps=24;s.frame_start=1;s.frame_end=144
bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-tractor-turn.blend'))
for frame,name in [(1,'entry'),(42,'apex'),(144,'exit')]:
 s.frame_set(frame);s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
s.render.filepath=str(O/'frames/frame-');bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-tractor-turn.blend'));bpy.ops.render.render(animation=True)
