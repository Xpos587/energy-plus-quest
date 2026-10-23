from pathlib import Path
import json,itertools
import cv2,numpy as np
from scipy.spatial import cKDTree
cv2.setNumThreads(1)
ROOT=Path('/home/michael/Github/energy-plus-quest');OUT=Path(__file__).resolve().parent
G=ROOT/'design/scene-01/kling-green-loop-2026-10-05/assembly/candidate-22.75s';B=ROOT/'design/scene-01/kling-blue-keys-2026-10-05/assembly/candidate-20s';env=np.load(OUT/'envelopes.npz');cache=np.load(OUT/'opaque-pair-matrices.npz')
gr=json.loads((G/'green-tracking.json').read_text())['rows'];br=json.loads((B/'blue-tracking.json').read_text())['rows'];n=np.arange(1092);far=[114,296,478];gi=np.array([(n+p)%546 for p in far]);bs=env['blue_straight'];starts=np.where(bs&np.roll(bs,3)&np.roll(bs,-3))[0]
base=cv2.imread(str(ROOT/'design/scene-01/kling-layer-extract-2026-10-05/empty-map-padded.png'));hsv=cv2.cvtColor(base,cv2.COLOR_BGR2HSV);road=((hsv[:,:,0]>=90)&(hsv[:,:,0]<=115)&(hsv[:,:,1]>45)&(hsv[:,:,2]>120)).astype('uint8');road=cv2.morphologyEx(road,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8));inside=cv2.distanceTransform(road,cv2.DIST_L2,cv2.DIST_MASK_PRECISE);outside=cv2.distanceTransform(1-road,cv2.DIST_L2,cv2.DIST_MASK_PRECISE);signed=inside-outside;cv2.imwrite(str(OUT/'roadmask-diagnostic.png'),road*255)
def load(folder,count):
 result=[]
 for i in range(count):
  a=cv2.imread(str(folder/'rgba-frames'/f'{i+1:04}.png'),-1);m=a[:,:,3]>127;y,x=np.where(m);box=np.array([x.min(),y.min(),x.max(),y.max()]);result.append((box,m[box[1]:box[3]+1,box[0]:box[2]+1],np.column_stack([x,y])))
 return result
gm=load(G,546);bm=load(B,480);gb=np.array([x[0] for x in gm]);bb=np.array([x[0] for x in bm]);i=np.arange(480)
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
profile=smooth((i-170)/22)*(1-smooth((i-294)/28))
results=[];matrices={};shifts={}
for amp in range(0,11):
 shift=np.rint(amp*profile).astype(int);shifts[amp]=shift;boxes=bb+np.column_stack([shift,np.zeros(480),shift,np.zeros(480)]).astype(int)
 dx=np.maximum(np.maximum(gb[:,None,0]-boxes[None,:,2],boxes[None,:,0]-gb[:,None,2]),0);dy=np.maximum(np.maximum(gb[:,None,1]-boxes[None,:,3],boxes[None,:,1]-gb[:,None,3]),0);matrix=np.zeros((546,480),dtype='int32')
 for x,z in zip(*np.where((dx==0)&(dy==0))):
  a,ma,_=gm[x];b,mb,_=bm[z];b=boxes[z];x0=max(a[0],b[0]);x1=min(a[2],b[2]);y0=max(a[1],b[1]);y1=min(a[3],b[3]);matrix[x,z]=int((ma[y0-a[1]:y1-a[1]+1,x0-a[0]:x1-a[0]+1]&mb[y0-b[1]:y1-b[1]+1,x0-b[0]:x1-b[0]+1]).sum())
 matrices[amp]=matrix;best=None
 for phase in starts:
  bi=(np.floor(n*480/1092).astype(int)+phase)%480;o=matrix[gi,bi];rank=(int(o.sum()),int((o>0).sum()),int(o.max()))
  if best is None or rank<best[0]:best=(rank,int(phase))
 clear=[];off=[]
 for z,(_,_,pts) in enumerate(bm):
  pts=pts+np.array([shift[z],0]);v=signed[pts[:,1],pts[:,0]];clear.append(float(v.min()));off.append(int((v<0).sum()))
 active=shift>0;worst=int(np.argmin(np.where(active,clear,np.inf))) if active.any() else 0
 results.append({'amplitude_px':amp,'blue_phase_source_frame':best[1],'opaque_overlap_pixels_sum':best[0][0],'opaque_overlap_frame_pairs':best[0][1],'max_opaque_overlap_pixels':best[0][2],'min_signed_roadmask_clearance_active_px':min(np.array(clear)[active]).item() if active.any() else None,'max_opaque_pixels_outside_road_active':max(np.array(off)[active]).item() if active.any() else None,'worst_road_source_frame':worst,'baseline_same_frame_road_clearance_px':float(signed[bm[worst][2][:,1],bm[worst][2][:,0]].min())})
 print(results[-1],flush=True)
# Smallest collision-free offset, if any; keep road gate independent.
passing=[x for x in results if x['opaque_overlap_frame_pairs']==0];selected=passing[0] if passing else min(results,key=lambda x:x['opaque_overlap_pixels_sum']);amp=selected['amplitude_px'];phase=selected['blue_phase_source_frame'];bi=(np.floor(n*480/1092).astype(int)+phase)%480;matrix=matrices[amp];pairs=[]
for lane,name in enumerate(['green','red','yellow']):
 ov=matrix[gi[lane],bi];ov0=matrices[0][gi[lane],bi];k=int(ov.argmax());k0=int(ov0.argmax());events=[]
 for _,group in itertools.groupby(enumerate(np.where(ov0>0)[0]),lambda x:x[1]-x[0]):
  seq=[int(x[1]) for x in group];events.append([seq[0]/24,seq[-1]/24])
 pairs.append({'pair':[name,'blue'],'baseline_overlap_frames':int((ov0>0).sum()),'baseline_max_pixels':int(ov0.max()),'baseline_time_of_max_s':k0/24,'baseline_overlap_time_ranges_s':events,'source_frames_at_baseline_max':[int(gi[lane,k0]),int(bi[k0])],'cab_centers_at_baseline_max':[gr[int(gi[lane,k0])]['cab_px'],br[int(bi[k0])]['cab_px']],'corrected_overlap_frames':int((ov>0).sum()),'corrected_max_pixels':int(ov.max())})
report={'far3_source_phases_frames':dict(zip(['green','red','yellow'],far)),'far3_minimum_body_gap_px':47.4236228055175,'period_seconds':45.5,'fps':24,'frames':1092,'profile':{'ramp_in_source_frames':[170,192],'hold_source_frames':[192,294],'ramp_out_source_frames':[294,322],'function':'cubic smoothstep; proposed floating rigid X translation, validation uses nearest integer pixel translation','observed_blue_straight_source_frames':[192,291],'scope':'central UP straight plus bounded entry/exit ramps; all other blue frames unchanged'},'offset_sweep':results,'selected':selected,'pairs_at_selected_phase':pairs,'roadmask':'fixed empty-map padded source, HSV road hue90..115 sat>45 value>120, morphological close9; image color proxy, not semantic ground truth. Signed distance positive inside derived asphalt mask. Opaque alpha includes fringe.','status':'collision-free offset found; road gate '+('positive' if selected['min_signed_roadmask_clearance_active_px'] is not None and selected['min_signed_roadmask_clearance_active_px']>0 else 'NOT PASS') if passing else 'NO PASS: no tested offset removed every opaque overlap'}
(OUT/'blue-rigid-offset-report.json').write_text(json.dumps(report,indent=2));tracks=[]
for j,row in enumerate(br):
 tracks.append({'source_frame':j,'source_time_s':j/24,'rigid_x_shift_px':float(amp*profile[j]),'validated_integer_x_shift_px':int(shifts[amp][j]),'original_cab_px':row['cab_px'],'proposed_cab_px':[row['cab_px'][0]+float(amp*profile[j]),row['cab_px'][1]]})
(OUT/'proposed-blue-translation-tracking.json').write_text(json.dumps({'status':'proposal only, not applied runtime','blue_phase_source_frames':phase,'blue_phase_source_seconds':phase/24,'rows':tracks},indent=2))
times=sorted(set([0]+[int(p['baseline_time_of_max_s']*24) for p in pairs]+[int(np.argmin(np.abs(bi-selected['worst_road_source_frame'])))]));tiles=[]
for k in times:
 for corrected in [False,True]:
  frame=base.copy();layers=[]
  for lane,name in enumerate(['green','red','yellow']):
   a=cv2.imread(str(G/'rgba-frames'/f'{int(gi[lane,k])+1:04}.png'),-1);alpha=a[:,:,3:4]/255;frame=(a[:,:,:3]*alpha+frame*(1-alpha)).astype('uint8');layers.append(a[:,:,3]>127)
  a=cv2.imread(str(B/'rgba-frames'/f'{int(bi[k])+1:04}.png'),-1);shift=int(shifts[amp][bi[k]]) if corrected else 0
  if shift:a=np.roll(a,shift,axis=1);a[:,:shift]=0
  alpha=a[:,:,3:4]/255;frame=(a[:,:,:3]*alpha+frame*(1-alpha)).astype('uint8');hit=np.logical_or.reduce(layers)&(a[:,:,3]>127);frame[hit]=(255,0,255)
  cv2.putText(frame,f't={k/24:.3f}s | '+(f'blue +{shift}px' if corrected else 'baseline')+' | red/yellow green geometry proxies',(10,20),0,.45,(25,25,25),1)
  tiles.append(cv2.resize(frame,(640,360)))
  if k!=0:
   cab=br[int(bi[k])]['cab_px'];x=max(0,int(cab[0])-100);y=max(0,int(cab[1])-60);crop=frame[y:y+240,x:x+230];cv2.imwrite(str(OUT/(f'blue-offset-{k}-'+('corrected' if corrected else 'baseline')+'.png')),cv2.resize(crop,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
cv2.imwrite(str(OUT/'blue-offset-contact-sheet.png'),np.vstack([np.hstack(tiles[j:j+2]) for j in range(0,len(tiles),2)]));print(json.dumps(report,indent=2),flush=True)
