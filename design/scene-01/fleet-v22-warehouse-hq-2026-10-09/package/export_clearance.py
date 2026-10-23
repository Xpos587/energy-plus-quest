import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();roots=[bpy.data.objects[f'truck-{i}-{p}']for i in range(1,5)for p in ('tractor','trailer')];hulls=[]
for root in roots:
 inv=root.matrix_world.inverted();points=[]
 for o in root.children_recursive:
  if o.type!='MESH' or o.hide_render or o.name.startswith('WHEEL contact'):continue
  points.extend(list(inv@o.matrix_world@Vector(v))for v in o.bound_box)
 hulls.append({'name':root.name,'points':points})
frames=[]
for f in range(1,s.frame_end+2):
 s.frame_set(f);bpy.context.view_layer.update();frames.append([[list(row)for row in o.matrix_world]for o in roots])
(P/'clearance-source.json').write_text(json.dumps({'hulls':hulls,'frames':frames}));print('CLEARANCE_EXPORTED',len(frames))
