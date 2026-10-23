"""Same-camera cab/trailer visibility, including dense samples in preview."""
import bpy,json,sys
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
sys.path.insert(0,'/home/michael/.local/state/energy-plus-quest/research/2026-09-22-city-polish')
from validate_visibility import templates,build,coverage,semantic_groups
groups=semantic_groups(s);ts=templates(s)
moving=set().union(*(groups[f'truck-{i}'] for i in range(1,5)))
static=build(s,[t for t in ts if t[0] not in moving])
parts={}
for i in range(1,5):
 for part in ('tractor','trailer'):
  root=s.objects[f'truck-{i}-{part}'];names={o.name for o in [root,*root.children_recursive] if not o.hide_render}
  parts[root.name]=[t for t in ts if t[0] in names]
records=[]
frames=sorted(set(range(1,121,6))|set(range(1,1153,24))|{120,1153})
for frame in frames:
 s.frame_set(frame);bpy.context.view_layer.update();dynamic=build(s,[t for t in ts if t[0] in moving]);row={}
 for name,part in parts.items():
  rig=f'truck-{name.split(chr(45))[1]}'
  group=build(s,[t for t in ts if t[0] in groups[rig]]);row[name]=coverage(group,[static,dynamic],s.camera,s,48,region={t[0] for t in part})
 records.append({'frame':frame,'parts':row})
 if len(records)%10==0:print('CAB_VISIBILITY',len(records),'/',len(frames),flush=True)
def minima(rows):return {name:min(r['parts'][name]['visible'] for r in rows) for name in parts}
r={'method':'48x48 projected full-rig silhouette rays, measuring each part only where visible in isolated complete rig; intrinsic trailer-over-chassis occlusion excluded. Every0.25seconds in first5seconds, every1second elsewhere. Camera fixed; all source occluders included.','first5_seconds_minimum':minima([r for r in records if r['frame']<=120]),'full_cycle_sampled_minimum':minima(records),'records':records}
(p/'cab-visibility.json').write_text(json.dumps(r,indent=2))
print(json.dumps({k:v for k,v in r.items() if k!='records'},indent=2))
