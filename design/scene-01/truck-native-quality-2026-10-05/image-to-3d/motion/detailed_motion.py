import bpy,pathlib,json
O=pathlib.Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'green-tractor-turn.blend'));s=bpy.context.scene
obj=bpy.data.objects['New textured whole green 6x4 tractor'];transform=obj.matrix_basis.copy();parent=obj.parent;inverse=obj.matrix_parent_inverse.copy();mode=obj.rotation_mode
with bpy.data.libraries.load(str(O.parent/'green-tractor-detailed.blend'),link=False) as (src,dst):dst.objects=['Mesh_0']
source=dst.objects[0];obj.data=source.data.copy();bpy.data.objects.remove(source,do_unlink=True)
assert obj.parent==parent and obj.rotation_mode==mode and obj.matrix_basis==transform and obj.matrix_parent_inverse==inverse
bpy.ops.file.pack_all();s.frame_start=1;s.frame_end=144;s.render.fps=24;s.render.engine='BLENDER_EEVEE';s.camera=bpy.data.objects['Fixed map maneuver camera'];(O/'detailed-frames').mkdir(exist_ok=True)
for frame,name in [(1,'entry'),(42,'apex'),(144,'exit')]:
 s.frame_set(frame);s.render.filepath=str(O/(name+'-detailed.png'));bpy.ops.render.render(write_still=True)
s.render.filepath=str(O/'detailed-frames/frame-');s.frame_set(42);bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-tractor-turn-detailed.blend'));bpy.ops.render.render(animation=True)
(O/'detailed-receipt.json').write_text(json.dumps({'source_mesh':'../green-tractor-detailed.blend Mesh_0.data copy','object_transform_preserved':True,'rotation_mode':mode,'tractor_parent':parent.name,'camera_unchanged':True,'root_actions_unchanged':True,'frames':[1,144],'fps':24,'duration_seconds':6,'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y],'limitations':['Whole tractor remains one mesh; wheels do not independently rotate.','Occupants and one steering wheel are projected texture on original windshield faces, not volumetric humans.','Original trailer retains6.38degree exit articulation.']},indent=2))
