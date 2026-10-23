from pathlib import Path
import json,pickle,numpy as np,shapely as sh
from shapely.geometry import MultiPoint
P=Path(__file__).resolve().parent
D=json.loads((P.parent/'clearance-source.json').read_text())
road,static=pickle.loads((P.parents[1]/'controlled-motion-2026-10-04/static-cache.pickle').read_bytes());obs=sh.union_all(list(static.values()))
a=np.load(P/'motion.npy');sweeps=[]
for k,item in enumerate(D['hulls']):
 scale=np.linalg.norm(np.asarray(D['frames'][0][k])[:3,0]);h=np.asarray(MultiPoint(np.asarray(item['points'])[:,:2]*scale).convex_hull.exterior.coords)
 c=np.cos(a[:,k,3]);s=np.sin(a[:,k,3]);r=np.stack([c,-s,s,c],axis=-1).reshape(-1,2,2)
 poly=sh.polygons(np.einsum('nij,kj->nki',r,h)+a[:,k,None,:2]);da=np.abs(np.diff(a[:,k,3]));err=float((np.linalg.norm(h,axis=1).max()*(1-np.cos(da/2))).max())+.001
 sweeps.append(sh.buffer(sh.convex_hull(sh.union(poly[:-1],poly[1:])),err))
pairs={f'{i+1}-{j+1}':min(float(sh.distance(sweeps[x],sweeps[y]).min())for x in(i*2,i*2+1)for y in(j*2,j*2+1))for i in range(4)for j in range(i+1,4)}
off=[int((sh.area(sh.difference(x,road))>.001).sum())for x in sweeps];hits=[int(sh.intersects(x,obs).sum())for x in sweeps]
report=dict(source='fresh v20 evaluated mesh bound boxes, swept convex hull and angular buffer',frames=len(a)-1,pair_clearances=pairs,offroad_intervals=off,static_collision_intervals=hits,static_min_distance=[float(sh.distance(x,obs).min())for x in sweeps],passed=not any(off+hits) and min(pairs.values())>.5)
(P/'fresh-hull-proof.json').write_text(json.dumps(report,indent=2));print(report)
for k,x in enumerate(sweeps):
 bad=sh.area(sh.difference(x,road));ids=np.where(bad>.001)[0]
 if len(ids):print(k,[(int(f),a[f,k,:2].tolist(),float(bad[f]))for f in ids[::max(1,len(ids)//4)]])
