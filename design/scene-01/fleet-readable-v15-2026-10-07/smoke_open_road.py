import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
for i in (1,4):
 o=bpy.data.objects[f'V15 {i} connected exhaust plume'];base=sum(v.co.z for v in list(o.data.vertices)[:16])/16;h=max(v.co.z for v in o.data.vertices)-base
 for v in o.data.vertices:v.co.y-=.80*((v.co.z-base)/h)**1.25
 o.data.update();vol=next(n for n in o.data.materials[0].node_tree.nodes if n.type=='PRINCIPLED_VOLUME');vol.inputs['Density'].default_value=5.2;vol.inputs['Color'].default_value=(.20,.24,.27,1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v15-readable.blend'))
