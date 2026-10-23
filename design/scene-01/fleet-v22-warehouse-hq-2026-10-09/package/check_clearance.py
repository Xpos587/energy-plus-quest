from pathlib import Path
import json,pickle,numpy as np,shapely as sh
from shapely.geometry import MultiPoint
P=Path(__file__).resolve().parent
D=json.loads((P/'clearance-source.json').read_text());m=np.asarray(D['frames'])
road,static=pickle.loads((P.parents[1]/'controlled-motion-2026-10-04/static-cache.pickle').read_bytes());obs=sh.union_all(list(static.values()));sweeps=[]
for k,item in enumerate(D['hulls']):
 h=np.asarray(MultiPoint(np.asarray(item['points'])[:,:2]).convex_hull.exterior.coords);v=np.column_stack([h,np.zeros(len(h)),np.ones(len(h))]);xy=np.einsum('nij,kj->nki',m[:,k],v)[:,:,:2]
 poly=sh.polygons(xy);yaw=np.arctan2(m[:,k,1,0],m[:,k,0,0]);delta=np.diff(yaw);delta=np.arctan2(np.sin(delta),np.cos(delta))
 radius=np.linalg.norm(h,axis=1).max()*np.linalg.norm(m[0,k,:3,0]);err=float((radius*(1-np.cos(delta/2))).max())+.001
 sweeps.append(sh.buffer(sh.convex_hull(sh.union(poly[:-1],poly[1:])),err))
pairs={f'{i+1}-{j+1}':min(float(sh.distance(sweeps[x],sweeps[y]).min())for x in(i*2,i*2+1)for y in(j*2,j*2+1))for i in range(4)for j in range(i+1,4)}
off=[int((sh.area(sh.difference(x,road))>.001).sum())for x in sweeps];hits=[int(sh.intersects(x,obs).sum())for x in sweeps]
r={'source':'v22 actual evaluated bounds and all1537 root matrices; v20 static obstacle contract','frames':len(m)-1,'pair_clearances':pairs,'offroad_intervals':off,'static_collision_intervals':hits,'static_min_distance':[float(sh.distance(x,obs).min())for x in sweeps],'passed':not any(off+hits)and min(pairs.values())>.5}
(P/'clearance-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
