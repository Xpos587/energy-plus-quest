import json,math,pickle
from pathlib import Path
import numpy as np
import shapely as sh
from shapely.geometry import MultiPoint,box
P=Path(__file__).resolve().parent
base=P.parents[1]/'controlled-motion-2026-10-04'
src=(base/'v2b/search_routes.py').read_text()
vehicle_scale=.85
exec(src[src.index('def length'):src.index('blue_spec=')])
N=2304;vehicle_scale=.85
specs=[[-2.25,29.8,-28.5,30.5,10],[-29.8,1.8,-28.5,30.3,12],[-29.8,29.8,-28.5,30.5,12],[-2.25,29.8,-28.5,30.5,10]]
laps=[2,2,2,2]
poses=[motion(s,l,2 if i==1 else 0) for i,(s,l) in enumerate(zip(specs,laps))]
bodies=[polygons(a,i)for i,a in enumerate(poses)]
for i,b in enumerate(bodies):
 env=sh.union_all(b);hits=[n for n,g in static.items()if sh.intersects(env,g)];off=float(sh.area(sh.difference(env,road)))
 print('ROUTE',i,off,hits,flush=True)
np.save(P/'raw.npy',np.stack(poses));
step=16;M=N//step
compat={}
for i in range(4):
 for j in range(i+1,4):
  compat[i,j]=np.array([float(sh.distance(bodies[i][::8,:,None],np.roll(bodies[j],-d,axis=0)[::8,None,:]).min())for d in range(0,N,step)])
  print('PAIR',i,j,compat[i,j].max(),flush=True)
def gap(i,j,a,b):return compat[i,j][(b-a)%M]
best=(-1,None)
for b in range(M):
 for c in range(M):
  floor=min(gap(0,1,0,b),gap(0,2,0,c),gap(1,2,b,c))
  if floor<=best[0]:continue
  gaps=np.minimum.reduce([np.full(M,floor),gap(0,3,0,np.arange(M)),gap(1,3,b,np.arange(M)),gap(2,3,c,np.arange(M))])
  k=int(gaps.argmax())
  if gaps[k]>best[0]:best=(float(gaps[k]),[0,b,c,k])
print('BEST',best,flush=True)
phases=[x*step for x in best[1]]
chosen=np.concatenate([np.roll(a,-f,axis=0)for a,f in zip(poses,phases)],axis=1)
for k in range(8):chosen[:,k,3]=np.unwrap(chosen[:,k,3])
end=chosen[0].copy();end[:,3]+=np.repeat(laps,2)*2*np.pi
chosen=np.concatenate([chosen,end[None]])
np.save(P/'motion.npy',chosen)
sweeps=[]
for i in range(4):
 body=polygons(chosen[:,2*i:2*i+2],i)
 for part in range(2):
  h=hulls[2*i+part];d=np.abs(np.diff(chosen[:,2*i+part,3]));error=float((np.max(np.linalg.norm(h,axis=1))*(1-np.cos(d/2))).max())+.0001
  sweeps.append(sh.buffer(sh.convex_hull(sh.union(body[:-1,part],body[1:,part])),error))
off=[int((sh.area(sh.difference(v,road))>.001).sum())for v in sweeps]
hits=[int(sh.intersects(v,obstacles).sum())for v in sweeps]
pairs={f'{i+1}-{j+1}':min(float(sh.distance(sweeps[a],sweeps[b]).min())for a in (i*2,i*2+1)for b in (j*2,j*2+1))for i in range(4)for j in range(i+1,4)}
report=dict(frames=N,seconds=96,laps=laps,specs=specs,phases=phases,pair_clearances=pairs,offroad=off,static_hits=hits,speeds=[length(s)*l/96 for s,l in zip(specs,laps)])
(P/'report.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
