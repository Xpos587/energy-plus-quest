import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-painted-projected-v09.blend'));o=bpy.data.objects['V02 DETAILED 3 complete tractor']
for sign in [-1,1]:
 vs=[v.co for v in o.data.vertices if v.co.x<-.95 and v.co.y*sign>.38 and .08<v.co.z<.36]
 print('MirrorPossible',sign,len(vs),[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)])
for z in [.02,.06,.10,.15,.2,.25,.3]:
 vs=[v.co for v in o.data.vertices if v.co.x<-.93 and abs(v.co.y)<.41 and abs(v.co.z-z)<.015]
 print('Frontband',z,len(vs),[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)] if vs else [])
