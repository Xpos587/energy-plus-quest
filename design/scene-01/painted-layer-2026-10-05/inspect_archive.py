import bpy
from pathlib import Path
D=Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-21-live/atlas')
for family in ('old-cab','near-cab','crew-cab'):
 bpy.ops.wm.open_mainfile(filepath=str(D/f'{family}.blend'))
 print('FAMILY',family)
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   print('MESH',o.name,'verts',len(o.data.vertices),'loc',tuple(o.location),'rot',tuple(o.rotation_euler),'scale',tuple(o.scale),'bounds',[(min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)) for i in range(3)],'materials',[(m.name,[(n.type,n.image.filepath if n.type=='TEX_IMAGE' else '') for n in m.node_tree.nodes]) for m in o.data.materials])
 print('IMAGES',[(i.name,i.filepath,bool(i.packed_file)) for i in bpy.data.images])
