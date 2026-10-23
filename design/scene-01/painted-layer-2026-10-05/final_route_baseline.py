import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene;poses={}
for f in range(1,1154):
 s.frame_set(f);poses[str(f)]={o.name:[list(o.location),list(o.rotation_euler)] for o in s.objects if o.name.startswith('truck-')}
(p/'final-frozen-root-baseline.json').write_text(json.dumps(poses));print('FROZEN ROOT BASELINE COMPLETE',len(poses),'frames including1153')
