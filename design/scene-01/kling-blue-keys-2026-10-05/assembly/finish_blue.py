from pathlib import Path
import cv2,numpy as np,json,subprocess
cv2.setNumThreads(1);r=Path(__file__).resolve().parent;out=r/'candidate-corrected';out.mkdir(exist_ok=True);rd=out/'rgba-frames';rd.mkdir(exist_ok=True)
base=cv2.imread(str(r/'segment-0-strict/empty-map-padded.png'));source=[];cab=[]
for s in range(4):
 source.extend(sorted((r/f'segment-{s}-strict/rgba-frames').glob('*.png'))[:120]);cab.extend([x['cab_px'] for x in json.loads((r/f'segment-{s}-layer/cab-tracking.json').read_text())['rows'][:120]])
cab=np.array(cab);starts={};raw=[]
for s in range(4):
 end=s*120+119;n=((s+1)%4)*120;v=np.polyfit(np.arange(7),cab[n:n+7],1)[0];step=cab[n]-cab[end];raw.append({'from':s,'to':(s+1)%4,'cab_step_px':float(np.linalg.norm(step))})
 if s in [1,2]:starts[(s+1)%4]=cab[end]+v-cab[n]
v0=np.polyfit(np.arange(7),cab[:7],1)[0];vlast=np.polyfit(np.arange(7),cab[-7:],1)[0];end_delta=cab[0]-v0-cab[-1];vd=v0-vlast
hsv=cv2.cvtColor(base,cv2.COLOR_BGR2HSV);road=((hsv[:,:,0]>=90)&(hsv[:,:,0]<=115)&(hsv[:,:,1]>40)&(hsv[:,:,2]>120)).astype(np.uint8);road=cv2.morphologyEx(road,cv2.MORPH_CLOSE,np.ones((21,21),np.uint8));distance=cv2.distanceTransform(road,cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
cmd=lambda file:['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r','24','-i','pipe:0','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',str(file)]
p20=subprocess.Popen(cmd(out/'composite-20s.mp4'),stdin=subprocess.PIPE);p45=subprocess.Popen(cmd(out/'composite-45.5s.mp4'),stdin=subprocess.PIPE)
repeat=np.bincount(np.floor(np.arange(1092)*480/1092).astype(int),minlength=480);rows=[];slow=[];metrics=[];boundary={};seamframes={};bad=[]
for i,f in enumerate(source):
 s,j=divmod(i,120);a=cv2.imread(str(f),-1);shift=np.zeros(2)
 if s in starts:
  t=min(j/23,1);shift+=starts[s]*(1-3*t*t+2*t*t*t)
 if s==3:
  t=np.clip((j-96)/23,0,1);shift+=(-2*t**3+3*t*t)*end_delta+(t**3-t*t)*23*vd
 af=a.astype(np.float32);af[:,:,:3]*=af[:,:,3:4]/255
 if np.linalg.norm(shift)>1e-8:
  af=cv2.warpAffine(af,np.array([[1,0,shift[0]],[0,1,shift[1]]],np.float32),(1280,720));rgb=np.divide(af[:,:,:3],af[:,:,3:4]/255,out=np.zeros_like(af[:,:,:3]),where=af[:,:,3:4]>1e-6);a=np.dstack([rgb,af[:,:,3]]).clip(0,255).round().astype(np.uint8)
 alpha=a[:,:,3:4]/255;comp=(a[:,:,:3]*alpha+base*(1-alpha)).round().astype(np.uint8);cv2.imwrite(str(rd/f'{i+1:04}.png'),a);p20.stdin.write(comp.tobytes())
 c=cab[i]+shift;x,y=c.round().astype(int)
 if a[y,x,3]<128:bad.append(i)
 row={'frame':i,'time':i/24,'source_segment':s,'source_frame':j,'cab_px':c.tolist(),'cab_roof_estimate':[float(c[0]/1280),float(c[1]/720)]};rows.append(row);metrics.append({'frame':i,'translation_px':shift.tolist(),'translation_norm_px':float(np.linalg.norm(shift)),'cab_center_road_clearance_px':float(distance[y,x])})
 for z in range(repeat[i]):
  p45.stdin.write(comp.tobytes());sr=dict(row);sr.update(frame=len(slow),time=len(slow)/24,source_candidate_frame=i);slow.append(sr)
 if j in [0,119]:boundary[i]=(a,comp)
 if j<24 or j>=96:seamframes[i]=comp
p20.stdin.close();p45.stdin.close();assert p20.wait()==0 and p45.wait()==0
seams=[];panels=[];writer=cv2.VideoWriter(str(out/'seams-4x-source.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),24,(880,720))
for s in range(4):
 end=s*120+119;start=((s+1)%4)*120;a,im0=boundary[end];b,im1=boundary[start];ma=a[:,:,3]>127;mb=b[:,:,3]>127;c0=np.array(rows[end]['cab_px']);c1=np.array(rows[start]['cab_px']);ys,xs=np.where(ma|mb);x=int(np.clip(xs.mean()-110,0,1060));y=int(np.clip(ys.mean()-90,0,540));tiles=[]
 for im,label in [(im0,str(s)+' end'),(im1,str((s+1)%4)+' start')]:
  tile=im[y:y+180,x:x+220].copy();cv2.putText(tile,label,(5,18),0,.45,(0,0,0),1);tiles.append(tile)
 panels.append(np.hstack(tiles))
 for off in range(-24,24):
  idx=(start+off)%480;tile=cv2.resize(seamframes[idx][y:y+180,x:x+220],(880,720),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{s} to {(s+1)%4} / {idx}',(8,25),0,.65,(0,0,0),2);writer.write(tile)
 steps=np.linalg.norm(np.diff([row['cab_px'] for row in rows[s*120:(s+1)*120]],axis=0),axis=1);seams.append({'from':s,'to':(s+1)%4,'cab_step_px':float(np.linalg.norm(c1-c0)),'previous_step_px':float(steps[-1]),'next_step_px':float(np.linalg.norm(np.array(rows[start+1]['cab_px'])-c1)),'segment_typical_median_step_px':float(np.median(steps)),'alpha_iou':float((ma&mb).sum()/(ma|mb).sum())})
writer.release();cv2.imwrite(str(out/'seams-native.png'),np.vstack(panels))
for name,data,duration in [('blue-tracking-20s.json',rows,20),('blue-tracking-45.5s.json',slow,45.5)]:
 (out/name).write_text(json.dumps({'fps':24,'frames':len(data),'duration_seconds':duration,'dimensions':[1280,720],'hotspot':'Observed SOURCE blue cab pixels, saturation-weighted local centroid plus the exact rigid layer translation; normalized upper left; image estimate not3D anchor','retime':'Nearest held source frames, no opticalflow, ghostblend or generated poses' if duration==45.5 else None,'rows':data},indent=2))
report={'raw_seams':raw,'corrected_seams':seams,'ramp_frames':24,'start_translations':{str(k):v.tolist() for k,v in starts.items()},'last_segment_end_translation':end_delta.tolist(),'max_translation_norm_px':max(x['translation_norm_px'] for x in metrics),'corrected_end_cab_center_road_clearance_px':metrics[-1]['cab_center_road_clearance_px'],'whole_loop_cab_center_road_min_px':min(x['cab_center_road_clearance_px'] for x in metrics),'cab_opacity_failures':bad,'scale':1,'rotation':0,'deformation':False,'crossfade':False,'slow_factor':2.275,'slow_frames':1092,'slow_duration_seconds':45.5,'road_metric':'Cab image-center distance to blue asphalt mask after21px closing fills white lane/crosswalks; not world wheel clearance.','status':'PENDING native4x visual gate and output decoding','translation_rows':metrics};(out/'gate-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='translation_rows'},indent=2))
