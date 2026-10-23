import bpy
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-v08-finished.blend'));o=bpy.data.objects['V02 DETAILED 3 complete tractor'];ids=set(v for p in o.data.polygons if p.material_index==1 for v in p.vertices);co=[o.data.vertices[v].co for v in ids];print('WIN',[ (min(v[i] for v in co),max(v[i] for v in co)) for i in range(3)])
