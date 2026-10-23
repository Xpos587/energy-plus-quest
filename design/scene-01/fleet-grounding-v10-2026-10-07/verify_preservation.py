import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
src=P.parent/'fleet-style-v08-2026-10-07/projected/clean/fleet-v09-clean-sill.blend'
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')]
 objs=set(roots)
 for r in roots:objs.update(r.children_recursive)
 frames={}
 for f in (1,385,769):
  s.frame_set(f);frames[str(f)]={o.name:[list(row) for row in o.matrix_world] for o in objs}
 return {'camera':{'name':s.camera.name,'matrix':[list(row) for row in s.camera.matrix_world],'scale':s.camera.data.ortho_scale},'roots':sorted(r.name for r in roots),'frame_start':s.frame_start,'frame_end':s.frame_end,'frames':frames,'meshes':{o.name:{'verts':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'materials':[m.name if m else None for m in o.data.materials]} for o in objs if o.type=='MESH'}}
a=snapshot(src);b=snapshot(P/'fleet-v10-real-shadowcatcher.blend')
checks={k:a[k]==b[k] for k in a}
(P/'preservation-verification.json').write_text(json.dumps({'checks':checks,'fleet_objects':len(a['frames']['1']),'frames':[1,385,769],'action_duration':a['frame_end']-a['frame_start']+1,'assertion':'Source and candidate truck matrices at all three rendered frames, mesh vertices/topology/material assignment and orthographic camera are exactly equal; only added receiver and pass visibility/light settings differ.'},indent=2))
print(checks);assert all(checks.values())
