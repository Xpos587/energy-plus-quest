import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
frames=(1,239,385,769,1152)
def take():
 s=bpy.context.scene;roots={};crew={}
 for f in frames:
  s.frame_set(f);roots[f]={o.name:[list(row)for row in o.matrix_world]for o in bpy.data.objects if o.name in [f'truck-{i}-{p}'for i in range(1,5)for p in ('tractor','trailer')]}
 for i in range(1,5):
  o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];uv=o.data.uv_layers.active.data
  polys=[p for p in o.data.polygons if p.material_index==1]
  crew[i]={'faces':len(polys),'uv':sorted(tuple(uv[k].uv)for p in polys for k in p.loop_indices),'material':o.data.materials[1].name}
 return {'roots':roots,'crew':crew,'camera':[list(row)for row in s.camera.matrix_world],'ortho':s.camera.data.ortho_scale}
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-clean-v13-2026-10-07/fleet-v13-clean.blend'));old=take()
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v14-native.blend'));new=take()
assert old['roots']==new['roots'];assert old['crew']==new['crew'];assert old['camera']==new['camera'];assert old['ortho']==new['ortho']
# Body/crew contact checks in tractor coordinates for old cabs, no rooftop pipe penetration.
checks=[]
for i in (1,4):
 root=bpy.data.objects[f'truck-{i}-tractor'];o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];t=root.matrix_world.inverted()@o.matrix_world
 pts=[t@o.data.vertices[v].co for p in o.data.polygons if p.material_index==1 for v in p.vertices]
 assert max(p.x for p in pts)-min(p.x for p in pts)<1e-5
 pipe=bpy.data.objects[f'{i} exhaust stack'];back=.08 if i==1 else .30
 assert pipe.location.x+.055<back-.07
 checks.append({'truck':i,'crew_plane_x':round(pts[0].x,5),'crew_z':[min(p.z for p in pts),max(p.z for p in pts)],'exhaust_behind_rear_bulkhead':True})
report={'source':'fleet-v14-native.blend','root_matrices_exact_vs_v13':list(frames),'camera_exact_vs_v13':True,'crew_uv_and_material_exact_vs_v13':{i:{'faces':x['faces'],'material':x['material']}for i,x in new['crew'].items()},'old_cab_checks':checks,'limits':'Static pilot only, no claim of all-frame collision or production/mobile integration validation.'}
(P/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
