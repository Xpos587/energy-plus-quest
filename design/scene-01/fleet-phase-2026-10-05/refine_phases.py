from pathlib import Path
import json,itertools
import cv2,numpy as np
from scipy.spatial import cKDTree
cv2.setNumThreads(1)
ROOT=Path('/home/michael/Github/energy-plus-quest'); OUT=Path(__file__).resolve().parent
G=ROOT/'design/scene-01/kling-green-loop-2026-10-05/assembly/candidate-22.75s';B=ROOT/'design/scene-01/kling-blue-keys-2026-10-05/assembly/candidate-20s'
env=np.load(OUT/'envelopes.npz');gb=env['green'];bb=env['blue'];gs=env['green_straight'];bs=env['blue_straight'];n=np.arange(1092);gi=n%546
def load(folder,boxes):
 masks=[];trees=[];points=[]
 for i,box in enumerate(boxes):
  a=cv2.imread(str(folder/'rgba-frames'/f'{i+1:04}.png'),-1)[:,:,3]>127
  x0,y0,x1,y1=box;masks.append(a[y0:y1+1,x0:x1+1])
  contours,_=cv2.findContours(a.astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  p=np.vstack(contours).reshape(-1,2);points.append(p);trees.append(cKDTree(p))
 return masks,trees,points
gm,gt,gp=load(G,gb);bm,bt,bp=load(B,bb)
def matrices(a,b,am,bm,at,bp,symmetric=False):
 dx=np.maximum(np.maximum(a[:,None,0]-b[None,:,2],b[None,:,0]-a[:,None,2]),0)
 dy=np.maximum(np.maximum(a[:,None,1]-b[None,:,3],b[None,:,1]-a[:,None,3]),0)
 dist=np.hypot(dx,dy);over=np.zeros(dist.shape,dtype='int32')
 for i,j in zip(*np.where(dist==0)):
  if symmetric and j<i:continue
  x0=max(a[i,0],b[j,0]);x1=min(a[i,2],b[j,2]);y0=max(a[i,1],b[j,1]);y1=min(a[i,3],b[j,3])
  ma=am[i][y0-a[i,1]:y1-a[i,1]+1,x0-a[i,0]:x1-a[i,0]+1];mb=bm[j][y0-b[j,1]:y1-b[j,1]+1,x0-b[j,0]:x1-b[j,0]+1]
  over[i,j]=int((ma&mb).sum())
  if over[i,j]==0:dist[i,j]=max(0,float(at[i].query(bp[j],k=1)[0].min())-np.sqrt(2))
  if symmetric:dist[j,i]=dist[i,j];over[j,i]=over[i,j]
 return dist,over
if (OUT/'opaque-pair-matrices.npz').exists():
 cache=np.load(OUT/'opaque-pair-matrices.npz');gg=cache['gg'];ggov=cache['ggov'];cross=cache['cross'];cov=cache['cov']
else:
 gg,ggov=matrices(gb,gb,gm,gm,gt,gp,True);cross,cov=matrices(gb,bb,gm,bm,gt,bp)
 np.savez(OUT/'opaque-pair-matrices.npz',gg=gg,ggov=ggov,cross=cross,cov=cov)
def stable(a):return a & np.roll(a,3)&np.roll(a,-3)
gstarts=np.where(stable(gs))[0][::3];gstarts=np.unique(np.r_[0,gstarts]);gstarts=gstarts[gstarts!=0]
bstarts=np.where(stable(bs))[0][::3]
sgap=np.array([gg[np.arange(546),(np.arange(546)+d)%546].min() for d in range(546)])
sov=np.array([ggov[np.arange(546),(np.arange(546)+d)%546].sum() for d in range(546)])
valid=[]
for i,r in enumerate(gstarts):
 for y in gstarts[i+1:]:
  clear=min(sgap[r],sgap[y],sgap[(y-r)%546])
  if clear>=4:valid.append((int(r),int(y),float(clear)))
best=None;eligible=len(valid)
for b in bstarts:
 bi=(np.floor(n*480/1092).astype(int)+b)%480
 bgap=np.array([cross[(gi+p)%546,bi].min() for p in range(546)])
 bov=np.array([cov[(gi+p)%546,bi].sum() for p in range(546)])
 bframes=np.array([(cov[(gi+p)%546,bi]>0).sum() for p in range(546)])
 for r,y,far in valid:
  score=min(far,bgap[0],bgap[r],bgap[y]); pixels=int(bov[0]+bov[r]+bov[y]);frames=int(bframes[0]+bframes[r]+bframes[y])
  rank=(score,-pixels,-frames,far)
  if best is None or rank>best[0]:best=(rank,r,y,int(b))
print('REFINED',best,'eligible_far3',eligible,flush=True)
if best is None:raise RuntimeError('No far3 phase combination with4px clearance and straight opening on searched lattice')
_,r,y,b=best;idx={'green':gi,'red':(gi+r)%546,'yellow':(gi+y)%546,'blue':(np.floor(n*480/1092).astype(int)+b)%480};pairs=[]
for a,z in itertools.combinations(idx,2):
 d=cross[idx[a],idx[z]] if z=='blue' else gg[idx[a],idx[z]]
 ov=cov[idx[a],idx[z]] if z=='blue' else ggov[idx[a],idx[z]];k=int(d.argmin());ko=int(ov.argmax())
 pairs.append({'pair':[a,z],'conservative_body_gap_px':float(d[k]),'min_gap_time_s':k/24,'overlap_frames':int((ov>0).sum()),'total_overlap_pixels_across_frames':int(ov.sum()),'max_overlap_pixels':int(ov.max()),'max_overlap_time_s':ko/24,'source_frames_at_max_overlap':[int(idx[a][ko]),int(idx[z][ko])]})
report={'period_seconds':45.5,'fps':24,'frames_checked':1092,'phases_source_frames':{'green':0,'red':r,'yellow':y,'blue':b},'phases_source_seconds':{'green':0,'red':r/24,'yellow':y/24,'blue':b/24},'blue_phase_output_seconds':b/480*45.5,'pairs':pairs,'search':{'opening_straight_rule':'trailer PCA axis cardinal<=12deg; cab-to-trailer axis articulation<=8deg; neighbors+-3frames also qualify','source_phase_lattice_stride':3,'green_opening_anchor':0,'valid_far3_combinations_min4px':eligible,'green_opening_candidates':len(gstarts)+1,'blue_opening_candidates':len(bstarts)},'geometry':'alpha>127 at actual native pixels. AABB positive separation provides conservative gap; overlapping AABBs are refined with exact pixel intersection and contour KDTree nearest-distance minus sqrt(2) to account for pixel extent. Every opaque alpha pixel included, including extraction fringe.','assumptions':['Red/yellow use actual green RGBA geometry with phase only; future appearance-edit motion not yet available and must be separately checked.','Blue20s source slowed to45.5s using floor source sampling; green22.75s repeats twice.','All four opening poses gated on observed geometry, not native routes.','No road/world collision claim; check is rendered cab/trailer alpha envelope.'],'status':'NO OPAQUE OVERLAP ON SEARCHED CANDIDATE' if all(p['overlap_frames']==0 for p in pairs) else 'COLLISIONS REMAIN; DO NOT CALL PASS'}
(OUT/'refined-phase-report.json').write_text(json.dumps(report,indent=2))
gr=json.loads((G/'green-tracking.json').read_text())['rows'];br=json.loads((B/'blue-tracking.json').read_text())['rows']
base=cv2.imread(str(ROOT/'design/scene-01/kling-layer-extract-2026-10-05/empty-map-padded.png'))
times=sorted(set([0,1091]+[int(p['max_overlap_time_s']*24) for p in pairs]+[int(p['min_gap_time_s']*24) for p in pairs]+list(range(0,1092,96))))
colors={'green':(60,165,35),'red':(40,50,225),'yellow':(30,205,245),'blue':(230,125,35)};tiles=[]
for k in times:
 frame=base.copy()
 for c,indices in idx.items():
  source=B if c=='blue' else G;j=int(indices[k]);a=cv2.imread(str(source/'rgba-frames'/f'{j+1:04}.png'),-1);alpha=a[:,:,3:4]/255;frame=(a[:,:,:3]*alpha+frame*(1-alpha)).astype('uint8')
  contours,_=cv2.findContours((a[:,:,3]>127).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(frame,contours,-1,colors[c],2)
  cab=(br if c=='blue' else gr)[j]['cab_px'];cv2.putText(frame,c,(int(cab[0])+10,int(cab[1])-10),0,.4,colors[c],1,cv2.LINE_AA)
 cv2.putText(frame,f't={k/24:.3f}s | red/yellow contours are green-path proxies',(10,20),0,.45,(25,25,25),1)
 if k==0:cv2.imwrite(str(OUT/'refined-opening.png'),frame)
 tiles.append(cv2.resize(frame,(640,360)))
while len(tiles)%3:tiles.append(np.full_like(tiles[0],245))
cv2.imwrite(str(OUT/'refined-contact-sheet.png'),np.vstack([np.hstack(tiles[i:i+3]) for i in range(0,len(tiles),3)]))
print(json.dumps(report,indent=2),flush=True)
