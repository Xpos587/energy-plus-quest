import bpy,numpy as np,json
from pathlib import Path
s=bpy.context.scene;o=bpy.data.objects['Mesh_0'];m=o.data
print('IMAGES',[(i.name,list(i.size)) for i in bpy.data.images]);print('BOUNDS',[list(v) for v in o.bound_box]);print('UV',[(u.name,len(u.data)) for u in m.uv_layers]);print('MATERIALS',[x.name for x in m.materials])
i=bpy.data.images['Image_0'];w,h=i.size;pix=np.array(i.pixels[:]).reshape(h,w,4);uv=m.uv_layers.active.data
rows=[]
for f in m.polygons:
 if f.normal.x<-.25:
  center=np.array(f.center[:]); u=np.mean([uv[k].uv[:] for k in f.loop_indices],axis=0);x,y=np.clip((u*[w-1,h-1]).astype(int),[0,0],[w-1,h-1]);c=pix[y,x,:3]
  if c[2]>c[0]*1.15 and c[2]>c[1]*1.05 and c[2]>.13:
   rows.append({'face':f.index,'center':center.tolist(),'rgb':c.tolist(),'uv':u.tolist(),'normal':list(f.normal)})
p=Path('design/scene-01/truck-native-quality-2026-10-05/sources/windshield-blue-candidates.json');p.write_text(json.dumps(rows))
print('BLUECOUNT',len(rows))
if rows:
 a=np.array([r['center'] for r in rows]);print('BLUEBOUNDS',a.min(0),a.max(0));print('ZQUANTILES',np.quantile(a[:,2],[0,.1,.25,.5,.75,.9,1]));print('SAMPLES',rows[::max(1,len(rows)//10)][:10])
