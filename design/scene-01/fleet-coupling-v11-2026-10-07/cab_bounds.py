import bpy
from mathutils import Vector
for i in range(1,5):
 r=bpy.data.objects[f'truck-{i}-tractor'];o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];m=r.matrix_world.inverted()@o.matrix_world;pts=[m@v.co for v in o.data.vertices]
 for z in [.865,1.01,1.3,1.7]:
  ps=[p for p in pts if p.z>=z];print(i,z, min(p.x for p in ps))
 print('EXHAUST',[o.name for o in r.children_recursive if not o.hide_render and 'exhaust' in o.name])
 for lo,hi in [(-2.7,-1.8),(-1.8,-.9)]:
  ps=[p for p in pts if lo<p.x<hi and abs(p.y)>.65 and p.z<.71];print('AXLE REGION',lo,hi,[(min(p[k] for p in ps),max(p[k] for p in ps)) for k in range(3)])
