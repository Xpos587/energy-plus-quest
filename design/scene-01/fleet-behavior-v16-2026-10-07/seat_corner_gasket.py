import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
for fn in ('fleet-v16.blend','fleet-v16-motion.blend'):
 bpy.ops.wm.open_mainfile(filepath=str(P/fn))
 for i in (1,4):
  o=bpy.data.objects[f'V14 {i} seated lower windshield gasket']
  for v in o.data.vertices:v.co.y*=1.18;v.co.z*=2.4
  o.location.x=1.84;o.location.z=1.412
 bpy.ops.wm.save_as_mainfile(filepath=str(P/fn))
