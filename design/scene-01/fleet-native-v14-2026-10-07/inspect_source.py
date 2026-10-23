import bpy,json
from mathutils import Vector
r=bpy.data.objects['truck-1-tractor']
for root in [r,bpy.data.objects['truck-1-trailer']]:
 for o in root.children_recursive:
  if o.type=='MESH' and not o.hide_render:
   pts=[root.matrix_world.inverted()@o.matrix_world@Vector(v) for v in o.bound_box]
   print(o.name,'BOUNDS',[[round(min(v[j] for v in pts),3),round(max(v[j] for v in pts),3)]for j in range(3)],'MATS',[m.name if m else None for m in o.data.materials])
o=bpy.data.objects['V02 DETAILED 1'];print('MATRIX',o.matrix_local);print('crew',[ (i,m.name) for i,m in enumerate(o.data.materials)])
