import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
roots=[f'truck-{i}-{part}' for i in range(1,5) for part in ('tractor','trailer')]
def snapshots():
 s=bpy.context.scene;out={}
 for f in (1,48,96,144,192):
  s.frame_set(f);bpy.context.view_layer.update();out[f]={name:[list(row) for row in bpy.data.objects[name].matrix_world] for name in roots}
 return out
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-behavior-v16-2026-10-07/fleet-v16-motion.blend'));before=snapshots();camera_before=[list(row) for row in bpy.context.scene.camera.matrix_world]
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v17-exhaust.blend'));after=snapshots();assert before==after
assert camera_before==[list(row) for row in bpy.context.scene.camera.matrix_world]
puffs=list(bpy.data.collections['V17 worldspace exhaust puffs'].objects);assert len(puffs)==22 and all(o.parent is None for o in puffs)
errors=[]
for i in (1,4):
 for slot in range(11):
  f=22+slot*2;bpy.context.scene.frame_set(f);bpy.context.view_layer.update();o=bpy.data.objects[f'V17 truck {i} exhaust puff {slot}'];pipe=bpy.data.objects[f'{i} exhaust stack'];v=[pipe.matrix_world@Vector(c) for c in pipe.bound_box];target=Vector((sum(c.x for c in v)/8,sum(c.y for c in v)/8,max(c.z for c in v)+.018));err=(o.location-target).length;errors.append(err);assert err<.00001
assert all(o.hide_render for o in bpy.data.objects if 'connected exhaust plume' in o.name)
receipt={'route_roots_compared':roots,'frames_compared':[1,48,96,144,192],'root_world_matrices_exactly_equal':True,'camera_world_matrix_exactly_equal':True,'worldspace_unparented_puffs':len(puffs),'stack_emission_checks':len(errors),'max_stack_emission_error_world_units':max(errors),'old_plumes_hidden':True}
(P/'source-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
