import bpy,pathlib
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/native');bpy.ops.wm.open_mainfile(filepath=str(P/'scania-native-shape-v4.blend'));s=bpy.context.scene
for side in [-1,1]:
 o=bpy.data.objects['Smooth green door outer skin '+str(side)];bpy.data.objects.remove(o,do_unlink=True)
 for nm,loc,scale in [('lowerdoor',(side*57,1.5,68),(2,93,52)),('rear upper door skin',(side*57,19.5,108),(2,57,28))]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name='Smooth '+nm+' '+str(side);o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials['Moderate sage green paint']);m=o.modifiers.new('Manufactured soft edge','BEVEL');m.width=1;m.segments=3
s.camera=bpy.data.objects['shape-gate-front-three-quarter'];s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(P/'shape-gate-v4-final.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'scania-native-shape-v4.blend'));bpy.ops.render.render(write_still=True)
for name in ['orthographic-front','orthographic-side','map-heading-0','map-heading-120','map-heading-240']:
 s.camera=bpy.data.objects[name];s.render.resolution_x=900 if name=='orthographic-front' else 1200 if name=='orthographic-side' else 640;s.render.resolution_y=900 if name=='orthographic-front' else 800 if name=='orthographic-side' else 640;s.render.filepath=str(P/(name+'-v4-final.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'scania-native-shape-v4.blend'))
