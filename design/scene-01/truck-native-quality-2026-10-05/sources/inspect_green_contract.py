import bpy, json
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene
out={'colors':{},'camera':{},'components':{},'motion_samples':{}}
for m in bpy.data.materials:
 if m.name.startswith('FIX cab'):
  out['colors'][m.name]={'diffuse':list(m.diffuse_color),'nodes':[{ 'name':n.name,'base_color':list(n.inputs['Base Color'].default_value)} for n in (m.node_tree.nodes if m.node_tree else []) if n.type=='BSDF_PRINCIPLED']}
c=s.camera;out['camera']={'name':c.name,'type':c.data.type,'ortho_scale':c.data.ortho_scale,'lens':c.data.lens,'location':list(c.location),'rotation':list(c.rotation_euler)}
s.frame_set(1)
for o in s.objects:
 if o.parent and o.parent.name.startswith('truck-') and any(t in o.name for t in ['formed enclosed cab','long semitrailer','ladder frame','seated tire','windshield','close-set mirror']):
  pts=[o.matrix_local@Vector(p) for p in o.bound_box]
  out['components'][o.name]={'parent':o.parent.name,'local_bounds_min':[min(p[a] for p in pts) for a in range(3)],'local_bounds_max':[max(p[a] for p in pts) for a in range(3)],'parent_inverse':[list(r) for r in o.matrix_parent_inverse]}
for f in [1,120,240,576,1152]:
 s.frame_set(f);out['motion_samples'][f]={}
 for o in s.objects:
  if o.name.startswith('truck-'):
   out['motion_samples'][f][o.name]={'location':list(o.location),'rotation_z':o.rotation_euler.z,'scale':list(o.scale)}
p=Path('design/scene-01/truck-native-quality-2026-10-05/sources/old-green-contract.json');p.write_text(json.dumps(out,indent=2))
print(json.dumps({'colors':out['colors'],'camera':out['camera'],'cab_bounds':{k:v for k,v in out['components'].items() if 'enclosed cab' in k}},indent=2))
