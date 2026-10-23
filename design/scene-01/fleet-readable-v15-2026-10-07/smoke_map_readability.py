import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
for i in (1,4):
 o=bpy.data.objects[f'V15 {i} connected exhaust plume'];base=sum(v.co.z for v in list(o.data.vertices)[:16])/16
 for v in o.data.vertices:v.co.z=base+(v.co.z-base)*1.45
 o.data.update();next(n for n in o.data.materials[0].node_tree.nodes if n.type=='PRINCIPLED_VOLUME').inputs['Density'].default_value=3.2
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v15-readable.blend'))
