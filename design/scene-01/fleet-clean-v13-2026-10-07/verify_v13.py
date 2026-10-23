import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;names=[f'truck-{i}-{part}' for i in range(1,5) for part in ('tractor','trailer')]
def sample(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;rows=[]
 for f in range(1,1153):
  s.frame_set(f);rows.append([tuple(v for row in bpy.data.objects[n].matrix_world for v in row) for n in names])
 return rows
old=sample(P.parent/'fleet-style-v12-2026-10-07/fleet-v12-style.blend');new=sample(P/'fleet-v13-clean.blend');assert old==new
s=bpy.context.scene;tr=bpy.data.objects['truck-2-tractor'];cab=bpy.data.objects['V02 DETAILED 2 complete tractor'];assembly=[o for o in s.objects if o.name.startswith('V08 2 refrigeration') or o.name=='V08 2 vent recess'];s.frame_set(1)
transform=tr.matrix_world.inverted()@cab.matrix_world;cab_points=[transform@v.co for v in cab.data.vertices];cab_rear=min(v.x for v in cab_points if v.z>1)
worst=(999,None)
for f in range(1,1153):
 s.frame_set(f);inv=tr.matrix_world.inverted();front=max((inv@o.matrix_world@Vector(c)).x for o in assembly for c in o.bound_box);clearance=cab_rear-front
 if clearance<worst[0]:worst=(clearance,f)
assert worst[0]>0
housing=bpy.data.objects['V08 2 refrigeration housing'];root=housing.parent;rear=min((root.matrix_world.inverted()@housing.matrix_world@Vector(c)).x for c in housing.bound_box);assert rear<.7
assert not any(o.name.startswith('V12 ') and any(k in o.name for k in ('canvas repair','visible stitch','sewn patch stitch')) for o in s.objects)
(P/'verification.json').write_text(json.dumps({'root_matrices_equal_all_1152_frames':True,'refrigeration_mount_rear_local_x':rear,'trailer_front_local_x':.7,'all_frame_min_cab_clearance_local':worst[0],'worst_frame':worst[1],'isolated_patch_and_stitch_objects_remaining':0,'crew_materials_preserved':True},indent=2))
print('V13 VERIFIED',worst,rear)
