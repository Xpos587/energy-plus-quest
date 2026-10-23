import bpy,json
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-exhaust-v17-2026-10-08/fleet-v17-exhaust.blend'))
bpy.context.scene.frame_set(1)
for i in (1,4):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];r=o.parent
 print('TARGET',i,'root',r.name,'MATRIX',[list(row) for row in o.matrix_local])
 print('MATERIALS',[(j,m.name) for j,m in enumerate(o.data.materials)])
 for j in range(len(o.data.materials)):
  pts=[o.matrix_local@o.data.vertices[k].co for f in o.data.polygons if f.material_index==j for k in f.vertices]
  if pts:print('BOUNDS',j,[min(p[a] for p in pts) for a in range(3)],[max(p[a] for p in pts) for a in range(3)])
 print('CHILDREN',[(c.name,c.hide_render,list(c.location)) for c in r.children_recursive if not c.hide_render])
 for m in o.data.materials:
  if 'windshield' in m.name:
   print('CREW SHADER',m.name,[(n.name,n.type,n.image.filepath if n.type=='TEX_IMAGE' and n.image else '') for n in m.node_tree.nodes])
