import bpy
from mathutils import Vector
p='/home/michael/Github/energy-plus-quest/design/scene-01/painted-layer-2026-10-05/painted-vehicles-driver-fixed-optimized.blend'
with bpy.data.libraries.load(p,link=False) as (f,t):t.objects=[n for n in f.objects if n in ['REPAIRED 1 detailed archived chassis','REPAIRED 1 fifth wheel support deck']]
for o in t.objects:
 if o:
  print(o.name,'loc',tuple(o.location),'rot',tuple(o.rotation_euler),'dims',tuple(o.dimensions),'parent',o.parent.name if o.parent else None)
  vs=[o.matrix_world @ Vector(v) for v in o.bound_box];print('bounds',tuple(min(v[j] for v in vs) for j in range(3)),tuple(max(v[j] for v in vs) for j in range(3)))
