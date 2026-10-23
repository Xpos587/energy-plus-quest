from pathlib import Path
import json,itertools
import cv2,numpy as np
from scipy.spatial import cKDTree
cv2.setNumThreads(1)
ROOT=Path('/home/michael/Github/energy-plus-quest');OUT=Path(__file__).resolve().parent
G=ROOT/'design/scene-01/kling-green-loop-2026-10-05/assembly/candidate-22.75s';B=ROOT/'design/scene-01/kling-blue-keys-2026-10-05/assembly/candidate-20s';gr=json.loads((G/'green-tracking.json').read_text())['rows'];br=json.loads((B/'blue-tracking.json').read_text())['rows'];env=np.load(OUT/'envelopes.npz');bs=env['blue_straight'];starts=np.where(bs&np.roll(bs,3)&np.roll(bs,-3))[0];n=np.arange(1092)
base=cv2.imread(str(ROOT/'design/scene-01/kling-layer-extract-2026-10-05/empty-map-padded.png'));road=cv2.imread(str(OUT/'roadmask-diagnostic.png'),0)>127;inside=cv2.distanceTransform(road.astype('uint8'),cv2.DIST_L2,cv2.DIST_MASK_PRECISE);outside=cv2.distanceTransform((~road).astype('uint8'),cv2.DIST_L2,cv2.DIST_MASK_PRECISE);signed=inside-outside
def source(folder,rows):
 data=[]
 for i,row in enumerate(rows):
  a=cv2.imread(str(folder/'rgba-frames'/f'{i+1:04}.png'),-1);y,x=np.where(a[:,:,3]>0);x0=max(0,int(x.min())-2);y0=max(0,int(y.min())-2);x1=min(1280,int(x.max())+3);y1=min(720,int(y.max())+3);data.append((x0,y0,a[y0:y1,x0:x1],np.array(row['cab_px'])-[x0,y0]))
 return data
gsrc=source(G,gr);bsrc=source(B,br)
def scaled(src,s):
 result=[];clear=[];off=[]
 for x0,y0,a,anchor in src:
  mat=np.array([[s,0,(1-s)*anchor[0]],[0,s,(1-s)*anchor[1]]],dtype='float32');alpha=cv2.warpAffine(a[:,:,3],mat,(a.shape[1],a.shape[0]),flags=cv2.INTER_LINEAR);m=alpha>127;y,x=np.where(m);box=np.array([x.min()+x0,y.min()+y0,x.max()+x0,y.max()+y0]);pts=np.column_stack([x+x0,y+y0]);contours,_=cv2.findContours(m.astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE);p=np.vstack(contours).reshape(-1,2)+[x0,y0];crop=m[box[1]-y0:box[3]-y0+1,box[0]-x0:box[2]-x0+1];result.append((box,crop,p,cKDTree(p)))
  dist=signed[pts[:,1],pts[:,0]];clear.append(float(dist.min()));off.append(int((dist<0).sum()))
 return result,{'minimum_signed_roadmask_clearance_px':min(clear),'max_opaque_pixels_outside_roadmask_in_source_frame':max(off),'worst_clearance_source_frame':int(np.argmin(clear)),'max_outside_source_frame':int(np.argmax(off))}
def boxgap(a,b):
 dx=np.maximum(np.maximum(a[...,0]-b[...,2],b[...,0]-a[...,2]),0);dy=np.maximum(np.maximum(a[...,1]-b[...,3],b[...,1]-a[...,3]),0);return np.hypot(dx,dy)
def exact(a,b):
 ba,ma,pa,tree=a;bb,mb,pb,_=b;x0=max(ba[0],bb[0]);x1=min(ba[2],bb[2]);y0=max(ba[1],bb[1]);y1=min(ba[3],bb[3]);ov=0
 if x1>=x0 and y1>=y0:ov=int((ma[y0-ba[1]:y1-ba[1]+1,x0-ba[0]:x1-ba[0]+1]&mb[y0-bb[1]:y1-bb[1]+1,x0-bb[0]:x1-bb[0]+1]).sum())
 d=0.0 if ov else max(0,float(tree.query(pb,k=1)[0].min())-np.sqrt(2));return d,ov
allresults=[];selected=None
for scale in [1,.98,.96,.94,.92]:
 gl,groad=scaled(gsrc,scale);bl,broad=scaled(bsrc,scale);gb=np.array([x[0] for x in gl]);bb=np.array([x[0] for x in bl]);cross=boxgap(gb[:,None],bb[None,:]);over=np.zeros(cross.shape,dtype='int32')
 for x,z in zip(*np.where(cross<4)):cross[x,z],over[x,z]=exact(gl[x],bl[z])
 scenarios=[]
 for label,far,fixed in [('common-best',[96,259,479],11),('comfortable',[114,296,478],None)]:
  gi=np.array([(n+p)%546 for p in far]);farmin=min(float(boxgap(gb[gi[x]],gb[gi[z]]).min()) for x,z in itertools.combinations(range(3),2));best=None
  for phase in [fixed] if fixed is not None else starts:
   bi=(np.floor(n*480/546).astype(int)+phase)%480;d=cross[gi,bi];ov=over[gi,bi];rank=(min(float(d.min()),farmin),-int(ov.sum()),-int((ov>0).sum()))
   if best is None or rank>best[0]:best=(rank,int(phase))
  rank,phase=best;bi=(np.floor(n*480/546).astype(int)+phase)%480;pairs=[]
  for lane,c in enumerate(['green','red','yellow']):
   d=cross[gi[lane],bi];ov=over[gi[lane],bi];k=int(d.argmin());ko=int(ov.argmax());pairs.append({'pair':[c,'blue'],'conservative_pixel_extent_gap_px':float(d[k]),'minimum_gap_time_s':k/24,'opaque_overlap_frames':int((ov>0).sum()),'max_opaque_overlap_pixels':int(ov.max()),'max_overlap_time_s':ko/24,'minimum_gap_source_frames':[int(gi[lane,k]),int(bi[k])]})
  result={'scenario':label,'scale':scale,'far_source_phases_frames':far,'blue_source_phase_frames':phase,'far3_minimum_aabb_gap_px':farmin,'fleet_minimum_conservative_pixel_extent_gap_px':rank[0],'opaque_overlap_frame_pairs':-rank[2],'opaque_overlap_pixels_across_frames':-rank[1],'passes_opaque_and_2px_margin':bool(rank[0]>=2 and rank[2]==0),'pairs':pairs};scenarios.append(result)
  if result['passes_opaque_and_2px_margin'] and selected is None:selected=dict(result)
 record={'scale':scale,'green_roadmask':groad,'blue_roadmask':broad,'scenarios':scenarios};allresults.append(record);print(json.dumps(record),flush=True)
report={'status':'passing uniform scale found' if selected else 'NO PASS at tested scales down to0.92','selected':selected,'results':allresults,'period_seconds':22.75,'diagnostic_duration_seconds':45.5,'fps':24,'frames_checked_per_scenario':1092,'anchor':'Each actual observed cab-roof centroid in source tracking; xprime=anchor+s*(x-anchor), yprime analogous. Whole RGBA rig scaled uniformly, no east translation, articulation/timing/source phases preserved.','margin':'2px rendered-footprint clearance. For close boxes, closest contour pixel-center distance minus sqrt(2) conservatively accounts for pixel squares. For distant boxes, positive AABB gap is a conservative lower bound.','limitations':['Red/yellow use green RGBA geometry proxies until real alpha exists.','Roadmask metric includes extracted matte fringe and color segmentation error; not physical ground-clearance truth.','Entire truck/scenario scale, not separate cab/trailer adjustment.','Only four requested reductions0.98/0.96/0.94/0.92 were tested; stop at0.92.']};(OUT/'uniform-scale-report.json').write_text(json.dumps(report,indent=2))
chosen=selected or allresults[-1]['scenarios'][1];scale=chosen['scale'];far=chosen['far_source_phases_frames'];phase=chosen['blue_source_phase_frames'];gi=np.array([(n+p)%546 for p in far]);bi=(np.floor(n*480/546).astype(int)+phase)%480
times=sorted(set([0]+[int(p['minimum_gap_time_s']*24) for p in chosen['pairs']]+[int(p['max_overlap_time_s']*24) for p in chosen['pairs']]));tiles=[]
def layer(src,s):
 x0,y0,a,anchor=src;mat=np.array([[s,0,(1-s)*anchor[0]],[0,s,(1-s)*anchor[1]]],dtype='float32');p=a.astype('float32');p[:,:,:3]*=p[:,:,3:4]/255;p=cv2.warpAffine(p,mat,(a.shape[1],a.shape[0]),flags=cv2.INTER_LINEAR);p[:,:,:3]=np.divide(p[:,:,:3],p[:,:,3:4]/255,out=np.zeros_like(p[:,:,:3]),where=p[:,:,3:4]>1e-6);full=np.zeros((720,1280,4),dtype='uint8');full[y0:y0+a.shape[0],x0:x0+a.shape[1]]=np.clip(np.rint(p),0,255).astype('uint8');return full
for k in times:
 for s in [1,scale]:
  frame=base.copy();layers=[]
  for lane in range(3):
   a=layer(gsrc[gi[lane,k]],s);alpha=a[:,:,3:4]/255;frame=(a[:,:,:3]*alpha+frame*(1-alpha)).astype('uint8');layers.append(a[:,:,3]>127)
  a=layer(bsrc[bi[k]],s);alpha=a[:,:,3:4]/255;frame=(a[:,:,:3]*alpha+frame*(1-alpha)).astype('uint8');hit=np.logical_or.reduce(layers)&(a[:,:,3]>127);frame[hit]=(255,0,255)
  cv2.putText(frame,f't={k/24:.3f}s | scale{s:.2f} | red/yellow green proxies',(10,20),0,.45,(25,25,25),1);tiles.append(cv2.resize(frame,(640,360)))
  if k==0:cv2.imwrite(str(OUT/f'uniform-scale-opening-{s:.2f}.png'),frame)
  else:
   cab=br[int(bi[k])]['cab_px'];x=max(0,int(cab[0])-110);y=max(0,int(cab[1])-75);crop=frame[y:y+250,x:x+240];cv2.imwrite(str(OUT/f'uniform-scale-crop-{k}-{s:.2f}.png'),cv2.resize(crop,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
cv2.imwrite(str(OUT/'uniform-scale-contact-sheet.png'),np.vstack([np.hstack(tiles[j:j+2]) for j in range(0,len(tiles),2)]));print('SELECTED',json.dumps(selected),flush=True)
