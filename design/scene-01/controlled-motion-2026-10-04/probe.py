import bpy,json,math
import numpy as np
from pathlib import Path
s=bpy.context.scene
p=Path('/home/michael/Github/energy-plus-quest/design/scene-01/controlled-motion-2026-10-04')
roots=[s.objects[f'truck-{i}-{part}'] for i in range(1,5) for part in ('tractor','trailer')]
poses=[]
for f in range(1,s.frame_end+2):
 s.frame_set(f)
 poses.append([[*o.location,o.rotation_euler.z] for o in roots])
np.save(p/'source-motion.npy',np.array(poses))
s.frame_set(1)
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
geometry=[]
for root in roots:
 points=[]
 for o in [root,*root.children_recursive]:
  if o.type!='MESH' or o.hide_render:continue
  ev=o.evaluated_get(dg);mesh=ev.to_mesh()
  transform=root.matrix_world.inverted()@o.matrix_world
  points.extend([list(transform@v.co) for v in mesh.vertices]);ev.to_mesh_clear()
 geometry.append({'name':root.name,'scale':list(root.scale),'points':points})
report={'frame_start':s.frame_start,'frame_end':s.frame_end,'fps':s.render.fps,'engine':s.render.engine,'camera':{'name':s.camera.name,'location':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'type':s.camera.data.type,'ortho_scale':s.camera.data.ortho_scale},'resolution':[s.render.resolution_x,s.render.resolution_y], 'roots':[{'name':o.name,'children':[(c.name,c.type,c.hide_render) for c in o.children_recursive]} for o in roots],'identification':[(o.name,o.hide_render) for o in s.objects if 'identification' in o.name]}
(p/'source-scene.json').write_text(json.dumps(report,indent=2));(p/'source-hulls.json').write_text(json.dumps(geometry))
print(json.dumps(report,indent=2))
