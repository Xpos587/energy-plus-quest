import bpy,json
from pathlib import Path
p=Path('/home/michael/Github/energy-plus-quest/design/scene-01/controlled-motion-2026-10-04');s=bpy.context.scene;s.frame_set(1)
dg=bpy.context.evaluated_depsgraph_get()
roots=[s.objects[f'truck-{i}-{part}'] for i in range(1,5) for part in ('tractor','trailer')]
moving={o.name for root in roots for o in [root,*root.children_recursive]}
objects=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or o.name in moving:continue
 ev=o.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles()
 objects.append({'name':o.name,'vertices':[list(o.matrix_world@v.co) for v in mesh.vertices],'triangles':[list(t.vertices) for t in mesh.loop_triangles]})
 ev.to_mesh_clear()
(p/'static-geometry.json').write_text(json.dumps(objects))
print('static_meshes',len(objects));print('road_meshes',[o['name'] for o in objects if any(n in o['name'] for n in ('street','road','ground','pavement'))])
