import bpy
from mathutils import Vector
s=bpy.context.scene;s.frame_set(1)
for i in [1,4]:
 r=bpy.data.objects[f'truck-{i}-trailer'];inv=r.matrix_world.inverted()
 for o in r.children_recursive:
  if o.type!='MESH' or o.hide_render:continue
  ps=[inv@o.matrix_world@Vector(p) for p in o.bound_box];mi=[min(p[k] for p in ps) for k in range(3)];ma=[max(p[k] for p in ps) for k in range(3)]
  if mi[0]<-6.8 and ma[2]<1:print(i,o.name,mi,ma,[(m.name,list(m.diffuse_color)) for m in o.data.materials])
