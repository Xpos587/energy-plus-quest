import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;min_gap={1:1e6,4:1e6};points={}
for i in (1,4):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];points[i]=[v.co.copy() for v in o.data.vertices]
for f in range(1,193):
 s.frame_set(f);bpy.context.view_layer.update()
 for i in (1,4):
  root=bpy.data.objects[f'truck-{i}-tractor'];cab=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];matrix=root.matrix_world.inverted()@cab.matrix_world
  for co in points[i]:
   q=matrix@co
   # Conservative front-tire cylinder envelope in root coordinates.
   if abs(q.x-.8)<.70 and abs(abs(q.y)-.805)<.19:
    gap=math.hypot(q.x-.8,q.z-.355)-.358
    min_gap[i]=min(min_gap[i],gap)
assert min(min_gap.values())>0,min_gap
(P/'wheel-gap-validation.json').write_text(json.dumps({'frames_checked':192,'minimum_cab_vertex_clearance_from_front_tire_envelope_local':min_gap,'method':'all main-cab vertices versus conservative front-tire cylinders; existing front-fender trim remains chassis-mounted; all tire world matrices separately identical to source'},indent=2));print(min_gap)
