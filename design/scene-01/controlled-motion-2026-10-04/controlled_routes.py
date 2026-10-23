"""Controlled 48-second loops on unchanged native asphalt; exact hull checks."""
import json,math,pickle
from pathlib import Path
import numpy as np
import shapely as sh
from shapely.geometry import MultiPoint,box
p=Path(__file__).resolve().parent
N=1152
source=np.load(p/'source-motion.npy')
def length(spec):
 l,r,b,t,z=spec;return 2*(r-l+t-b-4*z)+2*math.pi*z
def at(spec,d):
 l,r,b,t,z=spec;d%=length(spec)
 segments=[('line',(l+z,b),(r-z,b)),('arc',(r-z,b+z),(-math.pi/2,0)),('line',(r,b+z),(r,t-z)),('arc',(r-z,t-z),(0,math.pi/2)),('line',(r-z,t),(l+z,t)),('arc',(l+z,t-z),(math.pi/2,math.pi)),('line',(l,t-z),(l,b+z)),('arc',(l+z,b+z),(math.pi,3*math.pi/2))]
 for kind,start,end in segments:
  span=math.dist(start,end) if kind=='line' else z*math.pi/2
  if d<=span:
   a=math.atan2(end[1]-start[1],end[0]-start[0]) if kind=='line' else end[0]+d/z
   v=np.array([math.cos(a),math.sin(a)])
   return (np.array(start)+d*v,a) if kind=='line' else (np.array(start)+z*v,a+math.pi/2)
  d-=span

def motion(spec,laps,pace=0):
 theta=0.;previous=None;poses=[];ds=np.linspace(0,length(spec),4097)
 xs=np.array([at(spec,d)[0][0] for d in ds]);weights=1+pace*np.exp(-((xs+29.8)/10)**2)
 ts=np.concatenate(([0],np.cumsum((weights[:-1]+weights[1:])/2)));ts/=ts[-1]
 for step in range(-N*24,N*8):
  pos,a=at(spec,np.interp((laps*step/(N*8))%1,ts,ds));hitch=pos-3.036*np.array([math.cos(a),math.sin(a)])
  if previous is not None:
   dx,dy=hitch-previous;theta+=(dy*math.cos(theta)-dx*math.sin(theta))/7.062
  previous=hitch
  if step>=0 and step%8==0:poses.append([[*pos,0,a],[*hitch,0,theta]])
 return np.array(poses)

hulls=[np.array(MultiPoint((np.array(t['points'])*t['scale'])[:,:2]).convex_hull.exterior.coords)[:-1] for t in json.loads((p/'source-hulls.json').read_text())]
def polygons(poses,i):
 res=[]
 for part in range(2):
  a=poses[:,part,3];c=np.cos(a);s=np.sin(a);r=np.stack([c,-s,s,c],axis=-1).reshape(-1,2,2)
  res.append(sh.polygons(np.einsum('nij,kj->nki',r,hulls[i*2+part])+poses[:,part,None,:2]))
 return np.stack(res,axis=1)
def infrastructure(n):
 return n.startswith(('continuous ','ground','center line','crosswalk','stop line','EXT ground','EXT street','EXT pavement','EXT road marking','FIX road','FIX private','FIX pavement','FIX curb','FIX marking'))
if (p/'static-cache.pickle').exists():road,static=pickle.loads((p/'static-cache.pickle').read_bytes())
else:
 roadparts=[];static={}
 for o in json.loads((p/'static-geometry.json').read_text()):
  v=np.array(o['vertices'])[:,:2];tri=np.array(o['triangles'])
  if len(tri)==0:continue
  polys=sh.polygons(v[tri]);foot=sh.union_all(polys[sh.area(polys)>1e-9]);n=o['name']
  if n=='continuous street and private yard' or n.startswith(('EXT street','FIX road')):roadparts.append(foot)
  elif not infrastructure(n) and not n.startswith('FX '):static[n]=foot
 road=sh.union_all(roadparts);(p/'static-cache.pickle').write_bytes(pickle.dumps((road,static)))
obstacles=sh.union_all(list(static.values()))
blue_spec=[-29.8,1.8,-29.8,29.8,12]
blue=motion(blue_spec,1,2)
poses=[source[:-1,4:6].copy(),blue,source[:-1,4:6].copy(),source[:-1,4:6].copy()]
bodies=[polygons(a,i) for i,a in enumerate(poses)]
route_checks=[]
for i,b in enumerate(bodies):
 env=sh.union_all(b);off=float(sh.area(sh.difference(env,road)));hits=[n for n,g in static.items() if sh.intersects(env,g)]
 route_checks.append({'truck':i+1,'offroad_area':off,'static_obstacle_hits':hits})
 print('ROUTE',route_checks[-1],flush=True)
assert all(x['offroad_area']<.001 and not x['static_obstacle_hits'] for x in route_checks)
angles=[np.rad2deg(np.abs(np.angle(np.exp(1j*(a[:,0,3]-a[:,1,3]))))) for a in poses]
step=4
# Native far loop repeats twice, so retain only first 576 source phases.
candidates=[np.array([f for f in range(0,N if i==1 else N//2,step) if d[f]<3 and (i!=1 or poses[i][f,0,0]<-25)],dtype=int) for i,d in enumerate(angles)]
print('CANDIDATES',[len(c) for c in candidates],flush=True)
assert all(len(c)>0 for c in candidates)
compat={}
for i in range(4):
 for j in range(i+1,4):
  distances=np.full(N//step,np.nan)
  diffs=sorted(set(int((b-a)%N) for a in candidates[i] for b in candidates[j]))
  for d in diffs:
   shifted=np.roll(bodies[j],-d,axis=0)
   distances[d//step]=float(sh.distance(bodies[i][:,:,None],shifted[:,None,:]).min())
   if (i==1 or j==1) and '--strict-nearest' in __import__('sys').argv:
    lot=box(-51.8,-21.8,-32.15,23.2)
    di=sh.distance(sh.union(bodies[i][:,0],bodies[i][:,1]),lot)
    dj=sh.distance(sh.union(shifted[:,0],shifted[:,1]),lot)
    near_margin=(dj-di) if i==1 else (di-dj)
    if near_margin.min()<.1:distances[d//step]=0
  compat[i,j]=distances
  print('PAIR',i+1,j+1,'tested',len(diffs),'max',float(np.nanmax(distances)),flush=True)
def gap(i,j,a,b):return compat[i,j][((b-a)%N)//step]
best=(-1,None)
for a in candidates[0]:
 for b in candidates[1]:
  ab=gap(0,1,a,b)
  if ab<=best[0]:continue
  for c in candidates[2]:
   base=min(ab,gap(0,2,a,c),gap(1,2,b,c))
   if base<=best[0]:continue
   gaps=np.minimum.reduce([np.full(len(candidates[3]),base),gap(0,3,a,candidates[3]),gap(1,3,b,candidates[3]),gap(2,3,c,candidates[3])])
   k=int(np.argmax(gaps))
   if gaps[k]>best[0]:best=(float(gaps[k]),[int(a),int(b),int(c),int(candidates[3][k])])
print('BEST',best,flush=True)
assert best[0]>.3
chosen=np.concatenate([np.roll(a,-f,axis=0) for a,f in zip(poses,best[1])],axis=1)
for k in range(8):chosen[:,k,3]=np.unwrap(chosen[:,k,3])
end=chosen[0].copy();end[:,3]+=np.repeat([2,1,2,2],2)*2*np.pi
chosen=np.concatenate([chosen,end[None]])
sweeps=[]
for i in range(4):
 body=polygons(chosen[:,2*i:2*i+2],i)
 for part in range(2):
  h=hulls[2*i+part];d=np.abs(np.diff(chosen[:,2*i+part,3]));error=float((np.max(np.linalg.norm(h,axis=1))*(1-np.cos(d/2))).max())+.0001
  sweeps.append(sh.buffer(sh.convex_hull(sh.union(body[:-1,part],body[1:,part])),error))
lot=box(-51.8,-21.8,-32.15,23.2)
off=[int((sh.area(sh.difference(v,road))>.001).sum()) for v in sweeps]
hits=[int(sh.intersects(v,obstacles).sum()) for v in sweeps]
inlot=[int(sh.intersects(v,lot).sum()) for v in sweeps]
pair=min(float(sh.distance(sweeps[a],sweeps[b]).min()) for i in range(4) for j in range(i+1,4) for a in (i*2,i*2+1) for b in (j*2,j*2+1))
art=np.rad2deg(np.abs(np.angle(np.exp(1j*(chosen[:,::2,3]-chosen[:,1::2,3])))))
warehouse=np.stack([sh.distance(sh.union(sweeps[i*2],sweeps[i*2+1]),lot) for i in range(4)],axis=1)
hitch=max(float(np.linalg.norm(chosen[:,2*i,:2]-3.036*np.stack([np.cos(chosen[:,2*i,3]),np.sin(chosen[:,2*i,3])],axis=1)-chosen[:,2*i+1,:2],axis=1).max()) for i in range(4))
report={'fps':24,'frames':N,'duration_seconds':48,'phases':best[1],'route_definition':'Far rigs share unchanged source truck3 tractor/trailer motion with different cyclic shifts. Blue follows extended left asphalt loop with trailer hitch kinematics integrated at192Hz after144s settling.','blue_spec':blue_spec,'laps':[2,1,2,2],'initial_articulation_degrees':art[0].tolist(),'max_articulation_degrees':art.max(axis=0).tolist(),'offroad_swept_intervals':off,'static_collision_intervals':hits,'warehouse_lot_swept_intervals':inlot,'pair_clearance_min':pair,'hitch_error':hitch,'warehouse_distance_min':warehouse.min(axis=0).tolist(),'warehouse_distance_max':warehouse.max(axis=0).tolist(),'blue_nearest_warehouse_all_intervals':bool((warehouse[:,1]<warehouse[:,[0,2,3]].min(axis=1)).all()),'blue_near_fraction_under10':float((warehouse[:,1]<10).mean()),'loop_position_error':float(np.abs(chosen[0,:,:2]-chosen[-1,:,:2]).max()),'method':'Actual native evaluated mesh convex hulls, projected asphalt triangle unions and static geometry. Every key interval conservatively enclosed and buffered for angular interpolation. Scene-unit distances.'}
report['passed']=bool(not any(off+hits+inlot) and pair>.1 and hitch<.001 and art[0].max()<3 and art.max()<65 and warehouse[:,1].min()<1 and warehouse[:,[0,2,3]].min()>25)
(p/'route-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
assert report['passed']
np.save(p/'motion.npy',chosen)
