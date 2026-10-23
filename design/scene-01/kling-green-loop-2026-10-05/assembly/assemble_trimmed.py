from pathlib import Path
import cv2,numpy as np,json
cv2.setNumThreads(1);r=Path(__file__).resolve().parent;out=r/'candidate-22.75s';out.mkdir(exist_ok=True)
first=r.parents[1]/'kling-layer-extract-2026-10-05';base=cv2.imread(str(first/'empty-map-padded.png'))
configs=[('1',first,0,120),('2a',r/'segment-2a-layer',54,120),('2b',r/'segment-2b-layer',0,120),('3',r/'segment-3-layer',0,120),('4',r/'seam-correction',0,120)]
def cab(a):
 hsv=cv2.cvtColor(a[:,:,:3],cv2.COLOR_BGR2HSV);mask=((a[:,:,3]>127)&(hsv[:,:,0]>35)&(hsv[:,:,0]<90)&(hsv[:,:,1]>65)).astype(np.uint8)
 n,l,s,c=cv2.connectedComponentsWithStats(mask);j=1+np.argmax(s[1:,4]);return c[j]
segments=[]
for name,d,start,end in configs:segments.append((name,[cv2.imread(str(f),cv2.IMREAD_UNCHANGED) for f in sorted((d/'rgba-frames').glob('*.png'))[start:end]]))
# First measure actual cab joins before choosing any bounded correction.
raw=[]
for k,(name,fs) in enumerate(segments):
 nxt,nfs=segments[(k+1)%5];c0=cab(fs[-1]);c1=cab(nfs[0]);raw.append({'from':name,'to':nxt,'cab_vector_px':(c1-c0).tolist(),'cab_step_px':float(np.linalg.norm(c1-c0)),'last_step_px':float(np.linalg.norm(c0-cab(fs[-2]))),'next_step_px':float(np.linalg.norm(cab(nfs[1])-c1))})
(out/'raw-cab-seams.json').write_text(json.dumps(raw,indent=2));print(json.dumps(raw,indent=2))
rd=out/'rgba-frames';cd=out/'composite-frames';rd.mkdir(exist_ok=True);cd.mkdir(exist_ok=True)
hsv=cv2.cvtColor(base,cv2.COLOR_BGR2HSV);road=((hsv[:,:,0]>=90)&(hsv[:,:,0]<=115)&(hsv[:,:,1]>45)&(hsv[:,:,2]>120)).astype(np.uint8);road=cv2.morphologyEx(road,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8));distance=cv2.distanceTransform(road,cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
corrections=[];rows=[];boundaries=[];allcomps=[];alllayers=[]
for k,(name,fs) in enumerate(segments):
 offset=np.zeros(2)
 if name=='2a':offset=cab(segments[k-1][1][-1])-cab(fs[0])
 if name=='3':offset=cab(segments[k-1][1][-1])+np.polyfit(np.arange(7),np.array([cab(a) for a in fs[:7]]),1)[0]-cab(fs[0])
 ramp=24;corr=[];start=len(rows)
 for j,a in enumerate(fs):
  t=min(j/(ramp-1),1);shift=offset*(1-3*t*t+2*t*t*t);af=a.astype(np.float32);af[:,:,:3]*=af[:,:,3:4]/255
  if np.linalg.norm(shift)>1e-8:
   af=cv2.warpAffine(af,np.array([[1,0,shift[0]],[0,1,shift[1]]],np.float32),(1280,720));rgb=np.divide(af[:,:,:3],af[:,:,3:4]/255,out=np.zeros_like(af[:,:,:3]),where=af[:,:,3:4]>1e-6);a=np.dstack([rgb,af[:,:,3]]).clip(0,255).round().astype(np.uint8)
  idx=len(rows);alpha=a[:,:,3:4].astype(np.float32)/255;comp=(a[:,:,:3]*alpha+base*(1-alpha)).round().astype(np.uint8);cv2.imwrite(str(rd/f'{idx+1:04}.png'),a);cv2.imwrite(str(cd/f'{idx+1:04}.png'),comp)
  c=cab(a);rows.append({'frame':idx,'time':idx/24,'segment':name,'source_frame':j+(54 if name=='2a' else 0),'cab_roof_estimate':[float(c[0]/1280),float(c[1]/720)],'cab_px':c.tolist()});allcomps.append(comp);alllayers.append(a)
  body=a[:,:,3]>127;corr.append({'frame':j,'translation_px':shift.tolist(),'road_clearance_px':float(distance[body].min()),'projected_body_pixels_outside_blue_road':int((body&(road==0)).sum())})
 corrections.append({'segment':name,'start_translation_px':offset.tolist(),'ramp_frames':ramp if np.linalg.norm(offset)>0 else 0,'max_translation_px':float(np.linalg.norm(offset)),'minimum_projected_body_clearance_px':min(x['road_clearance_px'] for x in corr),'max_opaque_pixels_outside_road':max(x['projected_body_pixels_outside_blue_road'] for x in corr),'rows':corr});boundaries.append((name,start,len(rows)-1))
seams=[];panels=[];writer=cv2.VideoWriter(str(out/'seams-4x-review.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),24,(880,720))
for k,(name,start,end) in enumerate(boundaries):
 nxt,ns,ne=boundaries[(k+1)%5];c0=np.array(rows[end]['cab_px']);c1=np.array(rows[ns]['cab_px']);mask0=alllayers[end][:,:,3]>127;mask1=alllayers[ns][:,:,3]>127
 seams.append({'from':name,'to':nxt,'cab_step_px':float(np.linalg.norm(c1-c0)),'previous_step_px':float(np.linalg.norm(c0-rows[end-1]['cab_px'])),'next_step_px':float(np.linalg.norm(np.array(rows[ns+1]['cab_px'])-c1)),'alpha_iou':float((mask0&mask1).sum()/(mask0|mask1).sum())})
 ys,xs=np.where(mask0|mask1);x=int(np.clip(xs.mean()-110,0,1060));y=int(np.clip(ys.mean()-90,0,540));tiles=[]
 for frame,label in [(allcomps[end],name+' end'),(allcomps[ns],nxt+' start')]:
  tile=frame[y:y+180,x:x+220].copy();cv2.putText(tile,label,(5,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1);tiles.append(tile)
 panels.append(np.hstack(tiles))
 for off in range(-24,24):
  idx=(ns+off)%len(rows);tile=cv2.resize(allcomps[idx][y:y+180,x:x+220],(880,720),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{name} to {nxt}, frame {idx}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,0,0),2);writer.write(tile)
writer.release();cv2.imwrite(str(out/'seams-native.png'),np.vstack(panels))
(out/'green-tracking.json').write_text(json.dumps({'fps':24,'frames':546,'duration_seconds':22.75,'dimensions':[1280,720],'hotspot':'largest opaque green cab cluster centroid; normalized from upper left; observed image estimate, not native 3D anchor','rows':rows},indent=2))
(out/'seam-report.json').write_text(json.dumps({'fps':24,'frames':546,'duration_seconds':22.75,'trim':'2a source frames 54 through 119 inclusive; other four clips first 120 frames','seams':seams,'raw_seams':raw,'corrections':corrections,'deformation':False,'rotation':False,'crossfade':False,'retiming':False,'status':'visual review pending'},indent=2));print(json.dumps(seams,indent=2))
