"""Reversible technical assembly; independent review remains a required external gate."""
from pathlib import Path
import cv2,numpy as np,json,subprocess,sys
cv2.setNumThreads(1);r=Path(__file__).resolve().parent;color=sys.argv[1];out=r/f'{color}-candidate-22.75s';out.mkdir(exist_ok=True);rd=out/'rgba-frames';rd.mkdir(exist_ok=True)
segments=['0-1','1-mid','mid-2','2-3','3-0'];source=[];cab=[];ids=[];starts=[];ends=[]
for s in segments:
 rows=json.loads((r/f'{color}-{s}-layer/cab-tracking.json').read_text())['rows'];begin=54 if s=='1-mid' else 0;starts.append(len(source))
 for j in range(begin,120):source.append(r/f'{color}-{s}-layer/rgba-frames/{j+1:04}.png');cab.append(rows[j]['cab_px']);ids.append([s,j])
 ends.append(len(source)-1)
assert len(source)==546;cab=np.array(cab);offset={};raw=[]
for k in range(5):
 end=ends[k];n=starts[(k+1)%5];v=np.polyfit(np.arange(7),cab[n:n+7],1)[0];raw.append(float(np.linalg.norm(cab[n]-cab[end])))
 if k<4:offset[k+1]=cab[end]+v-cab[n]
v0=np.polyfit(np.arange(7),cab[:7],1)[0];vl=np.polyfit(np.arange(7),cab[-7:],1)[0];ed=cab[0]-v0-cab[-1];dv=v0-vl
max_proposed=max([np.linalg.norm(ed)]+[np.linalg.norm(v) for v in offset.values()]);assert max_proposed<16,('Unbounded seam translation requires review',color,max_proposed)
base=cv2.imread(str(r/f'{color}-0-1-layer/empty-map-padded.png'));cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r','24','-i','pipe:0','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',str(out/'composite.mp4')];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);rows=[];norms=[];boundary={};seamframes={};bad=[]
for i,p in enumerate(source):
 k=next(k for k in range(5) if starts[k]<=i<=ends[k]);j=i-starts[k];length=ends[k]-starts[k]+1;shift=np.zeros(2)
 if k in offset:
  t=min(j/23,1);shift+=offset[k]*(1-3*t*t+2*t*t*t)
 if k==4:
  t=np.clip((j-(length-24))/23,0,1);shift+=(-2*t**3+3*t*t)*ed+(t**3-t*t)*23*dv
 a=cv2.imread(str(p),-1).astype(np.float32);a[:,:,:3]*=a[:,:,3:4]/255
 if np.linalg.norm(shift)>1e-8:a=cv2.warpAffine(a,np.array([[1,0,shift[0]],[0,1,shift[1]]],np.float32),(1280,720))
 alpha=a[:,:,3]/255;rgb=np.divide(a[:,:,:3],alpha[:,:,None],out=np.zeros_like(a[:,:,:3]),where=alpha[:,:,None]>1e-6);layer=np.dstack([rgb,a[:,:,3]]).clip(0,255).round().astype(np.uint8);comp=(a[:,:,:3]+base*(1-alpha[:,:,None])).clip(0,255).round().astype(np.uint8);cv2.imwrite(str(rd/f'{i+1:04}.png'),layer);proc.stdin.write(comp.tobytes());c=cab[i]+shift;x,y=c.round().astype(int)
 if layer[y,x,3]<128:bad.append(i)
 rows.append({'frame':i,'time':i/24,'source_segment':ids[i][0],'source_frame':ids[i][1],'cab_px':c.tolist(),'cab_roof_estimate':(c/[1280,720]).tolist(),'translation_px':shift.tolist()});norms.append(float(np.linalg.norm(shift)))
 if i in starts+ends:boundary[i]=(layer,comp)
 if j<24 or j>=length-24:seamframes[i]=comp
proc.stdin.close();assert proc.wait()==0;panels=[];seams=[];writer=cv2.VideoWriter(str(out/'seams-4x-source.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),24,(880,720))
for k in range(5):
 end=ends[k];start=starts[(k+1)%5];a,im0=boundary[end];b,im1=boundary[start];mask=(a[:,:,3]>127)|(b[:,:,3]>127);ys,xs=np.where(mask);x=int(np.clip(xs.mean()-110,0,1060));y=int(np.clip(ys.mean()-90,0,540));tiles=[]
 for im,label in [(im0,segments[k]+' end'),(im1,segments[(k+1)%5]+' start')]:
  tile=im[y:y+180,x:x+220].copy();cv2.putText(tile,label,(4,18),0,.4,(0,0,0),1);tiles.append(tile)
 panels.append(np.hstack(tiles))
 for off in range(-24,24):
  idx=(start+off)%546;tile=cv2.resize(seamframes[idx][y:y+180,x:x+220],(880,720),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{color} seam{k} frame{idx}',(8,24),0,.6,(0,0,0),1);writer.write(tile)
 steps=np.linalg.norm(np.diff([row['cab_px'] for row in rows[starts[k]:ends[k]+1]],axis=0),axis=1);seams.append({'from':segments[k],'to':segments[(k+1)%5],'raw_step_px':raw[k],'corrected_step_px':float(np.linalg.norm(np.array(rows[start]['cab_px'])-rows[end]['cab_px'])),'previous_step_px':float(steps[-1]),'next_step_px':float(np.linalg.norm(np.array(rows[start+1]['cab_px'])-rows[start]['cab_px'])),'ordinary_median_step_px':float(np.median(steps))})
writer.release();cv2.imwrite(str(out/'seams-native.png'),np.vstack(panels));subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(out/'seams-4x-source.mp4'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-threads','2',str(out/'seams-4x-review.mp4')],check=True)
(out/'cab-tracking.json').write_text(json.dumps({'fps':24,'frames':546,'duration_seconds':22.75,'dimensions':[1280,720],'hotspot':'Observed source colored cab pixels plus exact rigid translations; normalized top-left image estimate','rows':rows},indent=2));report={'color':color,'gate':'PENDING independent motion review and native alpha/seam acceptance','frames':546,'fps':24,'duration_seconds':22.75,'dimensions':[1280,720],'trim':{'1-mid':'Retain source54..119; remove2.25s initial hold'},'seams':seams,'max_translation_px':max(norms),'ramp_frames':24,'scale':1,'rotation':0,'deformation':False,'crossfade':False,'cab_opacity_failures':bad};(out/'gate-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
