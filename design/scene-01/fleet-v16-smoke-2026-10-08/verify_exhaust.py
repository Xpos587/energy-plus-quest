import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
roots=[f'truck-{i}-{part}' for i in range(1,5) for part in ('tractor','trailer')]
def snapshots():
 s=bpy.context.scene;out={}
 for f in (1,48,96,144,192):
  s.frame_set(f);bpy.context.view_layer.update();out[f]={name:[list(row) for row in bpy.data.objects[name].matrix_world] for name in roots}
 return out
def geometry_contract():
 return {o.name:{'type':o.type,'data':o.data.name if o.data else None,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []} for o in bpy.data.objects if not o.name.startswith('V16 smoke truck')}
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-behavior-v16-2026-10-07/fleet-v16-motion.blend'));before=snapshots();camera_before=[list(row) for row in bpy.context.scene.camera.matrix_world];geometry_before=geometry_contract()
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v16-smoke.blend'));after=snapshots();assert before==after
assert camera_before==[list(row) for row in bpy.context.scene.camera.matrix_world]
assert geometry_before==geometry_contract()
puffs=list(bpy.data.collections['V16 smoke worldspace exhaust puffs'].objects);assert len(puffs)==26 and all(o.parent is None for o in puffs)
errors=[]
for i in (1,4):
 for slot in range(13):
  f=26+slot*2;bpy.context.scene.frame_set(f);bpy.context.view_layer.update();o=bpy.data.objects[f'V16 smoke truck {i} exhaust puff {slot}'];pipe=bpy.data.objects[f'{i} exhaust stack'];v=[pipe.matrix_world@Vector(c) for c in pipe.bound_box];target=Vector((sum(c.x for c in v)/8,sum(c.y for c in v)/8,max(c.z for c in v)+.018));err=(o.location-target).length;errors.append(err);assert err<.00001
assert all(o.hide_render for o in bpy.data.objects if 'connected exhaust plume' in o.name)
drift_errors=[]
for i in (1,4):
 for f in (48,96,144):
  for slot in (0,5,10):
   age=(f-slot*2)%26;birth=f-age;bpy.context.scene.frame_set(f);loc=bpy.data.objects[f'V16 smoke truck {i} exhaust puff {slot}'].location.copy()
   bpy.context.scene.frame_set(birth);bpy.context.view_layer.update();pipe=bpy.data.objects[f'{i} exhaust stack'];v=[pipe.matrix_world@Vector(c) for c in pipe.bound_box];target=Vector((sum(c.x for c in v)/8,sum(c.y for c in v)/8,max(c.z for c in v)+.018+5*math.sqrt(age/26)));err=(loc-target).length;drift_errors.append(err);assert err<.00001
receipt={'route_roots_compared':roots,'frames_compared':[1,48,96,144,192],'root_world_matrices_exactly_equal':True,'camera_world_matrix_exactly_equal':True,'all_existing_object_data_names_vertex_counts_material_slots_preserved':True,'worldspace_unparented_puffs':len(puffs),'stack_emission_checks':len(errors),'max_stack_emission_error_world_units':max(errors),'no_lateral_drift_checks':len(drift_errors),'max_vertical_only_trajectory_error':max(drift_errors),'old_plumes_hidden':True}
(P/'source-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
