import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
s=bpy.context.scene
assert s.frame_end==1536
out=[]
for i in range(1,5):
 t=bpy.data.objects[f'truck-{i}-tractor'];r=bpy.data.objects[f'truck-{i}-trailer']
 assert abs(bpy.data.objects[f'{i} fifth wheel'].location.x+1.75)<1e-5
 for o in r.children:
  if o.name.startswith(f'WHEEL steering {i} trailer'):assert abs(abs(o.location.y)-.66)<1e-5
 out.append({'truck':i,'saved_coupling_x':bpy.data.objects[f'{i} fifth wheel'].location.x})
print('SAVED_SOURCE_OK',json.dumps(out))
