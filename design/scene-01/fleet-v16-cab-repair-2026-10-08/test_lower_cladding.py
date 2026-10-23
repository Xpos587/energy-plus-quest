"""Regression probe for the open side-cladding strip above the front tire."""
import bpy, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from pathlib import Path
P=Path(__file__).resolve().parent
s=bpy.context.scene;s.frame_set(91);bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get();result=[]
for i in (1,4):
 group=bpy.data.objects[f'WORN {i} isolated cab suspension']
 base=group.matrix_world@Matrix.Translation(Vector((-.8,0,-.9)))
 cab=bpy.data.objects[f'V02 DETAILED {i} complete tractor']
 objects=[cab,*cab.children_recursive]+[o for o in s.objects if o.name.startswith(f'CABREPAIR {i} ')]
 verts=[];faces=[]
 for o in objects:
  if o.type!='MESH' or o.hide_render:continue
  ev=o.evaluated_get(deps);mesh=ev.to_mesh();off=len(verts)
  verts.extend(o.matrix_world@v.co for v in mesh.vertices)
  faces.extend(tuple(off+j for j in f.vertices) for f in mesh.polygons);ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(verts,faces)
 for side in (-1,1):
  p=base@Vector((.8,side*1.2,.88));direction=base.to_3x3()@Vector((0,-side,0));limit=(base.to_3x3()@Vector((0,.4,0))).length
  hit=tree.ray_cast(p,direction.normalized(),limit)
  result.append({'truck':i,'side':side,'coverage':hit[0] is not None})
print(json.dumps(result))
assert all(r['coverage'] for r in result),'Open side-cladding strip above front tire'
