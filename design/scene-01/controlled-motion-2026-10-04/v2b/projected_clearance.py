"""Conservative projected vehicle prisms; pixel gaps, not point distances."""
import json,math
from pathlib import Path
import numpy as np
import shapely as sh
from shapely.geometry import MultiPoint
p=Path(__file__).resolve().parent;base=p.parent
m=np.load(p/'motion.npy');r=json.loads((p/'route-check.json').read_text());source=json.loads((base/'source-hulls.json').read_text());camera=json.loads((base/'source-scene.json').read_text())['camera']
x,y,z=camera['rotation'];cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
rotation=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
scale=r['vehicle_scale_factor'];parts=[]
for k,t in enumerate(source):
 v=np.array(t['points'])*np.array(t['scale'])*scale;h=np.array(MultiPoint(v[:,:2]).convex_hull.exterior.coords)[:-1]
 prism=np.concatenate([np.column_stack([h,np.full(len(h),height)]) for height in (v[:,2].min(),v[:,2].max())])
 a=m[:,k,3];c=np.cos(a);s=np.sin(a);rot=np.zeros((len(m),3,3));rot[:,0,0]=rot[:,1,1]=c;rot[:,0,1]=-s;rot[:,1,0]=s;rot[:,2,2]=1
 world=np.einsum('nij,kj->nki',rot,prism)+m[:,k,None,:3];view=(world-np.array(camera['location']))@rotation
 screen=np.stack([360+view[:,:,0]*720/camera['ortho_scale'],250-view[:,:,1]*720/camera['ortho_scale']],axis=-1)
 parts.append(sh.convex_hull(sh.multipoints(screen)))
rigs=[sh.union(parts[i*2],parts[i*2+1]) for i in range(4)]
pairs={}
for i in range(4):
 for j in range(i+1,4):
  d=sh.distance(rigs[i],rigs[j]);pairs[f'{i+1}-{j+1}']={'minimum_pixels_full_cycle':float(d.min()),'minimum_pixels_first5seconds':float(d[:120].min()),'first_frame_gap_pixels':float(d[0]),'minimum_frame':int(d.argmin()+1),'projected_overlap_frames':int((d<.001).sum())}
report={'render_resolution':[720,500],'method':'Projected prisms enclosing actual native mesh XY hull and complete Z range, including empty volume. Conservative object-to-object gaps; building visibility is separately ray-tested.','pairs':pairs}
(p/'projected-clearance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
