import bpy,json
from pathlib import Path
s=bpy.context.scene;p={}
for f in range(1,289):
 s.frame_set(f);p[str(f)]={o.name:{'position':list(o.location),'rotation':list(o.rotation_euler)} for o in s.objects if o.name.startswith('truck-')}
(Path(__file__).resolve().parent/'frozen-route-baseline.json').write_text(json.dumps(p))
print('BASELINE',len(p),'frames',len(p['1']),'roots')
