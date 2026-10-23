import bpy
from mathutils import Vector
for i in (1,3,4):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];r=o.parent;m=r.matrix_world.inverted()@o.matrix_world
 print('TRANSFORM',i,m)
 for j,mat in enumerate(o.data.materials):
  ids={v for p in o.data.polygons if p.material_index==j for v in p.vertices};pts=[m@o.data.vertices[v].co for v in ids]
  print(j,mat.name,len(ids),[(round(min(v[k] for v in pts),3),round(max(v[k] for v in pts),3))for k in range(3)])
