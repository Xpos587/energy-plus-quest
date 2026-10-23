import bpy
from mathutils import Vector
s=bpy.context.scene;s.frame_set(769);bpy.context.view_layer.update()
for i in (1,4):
 r=bpy.data.objects[f'truck-{i}-tractor'];inv=r.matrix_world.inverted()
 for name in (f'{i} exhaust stack',f'V15 {i} connected exhaust plume'):
  o=bpy.data.objects[name];p=[inv@o.matrix_world@Vector(v)for v in o.bound_box];print(name,'local',list(o.location),'bounds',[(min(v[k]for v in p),max(v[k]for v in p))for k in range(3)])
