import bpy
from mathutils import Vector
from collections import defaultdict
for i in (3,):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];m=o.parent.matrix_world.inverted()@o.matrix_world;vs=o.data.vertices
 parent=list(range(len(vs)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for e in o.data.edges:
  a,b=map(find,e.vertices);parent[b]=a
 groups=defaultdict(list)
 for v in vs:groups[find(v.index)].append(m@v.co)
 for pts in sorted(groups.values(),key=len,reverse=True):
  if len(pts)<50:continue
  bounds=[(round(min(v[k]for v in pts),3),round(max(v[k]for v in pts),3))for k in range(3)]
  print(len(pts),bounds)
