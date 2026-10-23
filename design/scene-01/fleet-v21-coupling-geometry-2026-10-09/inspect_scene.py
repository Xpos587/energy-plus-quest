import bpy,json
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;s.frame_set(1)
rows=[]
for o in s.objects:
 if o.name.startswith(('truck-4','WHEEL steering 4','WHEEL rotation 4')) or (o.parent and o.parent.name=='truck-4-trailer'):
  rows.append(dict(name=o.name,parent=o.parent.name if o.parent else None,type=o.type,loc=list(o.location),scale=list(o.scale),dim=list(o.dimensions),bbox=[list(v) for v in o.bound_box] if o.type=='MESH' else None))
p=Path(__file__).resolve().parent
(p/'inspection.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
