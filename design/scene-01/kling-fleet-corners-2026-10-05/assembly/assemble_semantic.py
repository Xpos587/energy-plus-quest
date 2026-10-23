"""Assemble source-RGB semantic layers with reversible whole-layer translations and explicit source mapping."""
from pathlib import Path
import sys,json,cv2,numpy as np,subprocess,os
cv2.setNumThreads(1);r=Path(__file__).resolve().parent;color=sys.argv[1];out=r/f'{color}-semantic-candidate';out.mkdir(exist_ok=True);rawdir=out/'raw-rgba-frames';rawdir.mkdir(exist_ok=True);rd=out/'rgba-frames';rd.mkdir(exist_ok=True)
segs=['0-1','1-mid','mid-2','2-3','3-0'];sources=[];cab=[];ids=[];starts=[];ends=[]
for seg in segs:
 gate=json.loads((r/'semantic-layers'/f'{color}-{seg}'/'gate-report.json').read_text());assert not gate['cab_roof_alpha_failures'];assert gate['source_rgb_exact_all121'];assert gate.get('visual_body_sampled'),('View all21 source/layer quarter samples first',seg)
 rows=json.loads((r/'source-roof-tracking'/f'{color}-{seg}.json').read_text())['rows'];begin=54 if color=='red' and seg=='1-mid' else 0;starts.append(len(sources))
 for j in range(begin,120):sources.append(r/'semantic-layers'/f'{color}-{seg}'/'rgba-frames'/f'{j:04d}.png');cab.append(rows[j]['cab_px']);ids.append((seg,j))
 ends.append(len(sources)-1)
N=len(sources);assert N==(546 if color=='red' else 600);cab=np.array(cab);offset={};rawsteps=[]
for k in range(5):
 e,n=ends[k],starts[(k+1)%5];v=np.polyfit(np.arange(7),cab[n:n+7],1)[0];rawsteps.append(float(np.linalg.norm(cab[n]-cab[e])))
 if k<4:offset[k+1]=cab[e]+v-cab[n]
v0=np.polyfit(np.arange(7),cab[:7],1)[0];vl=np.polyfit(np.arange(7),cab[-7:],1)[0];enddelta=cab[0]-v0-cab[-1];derivative=v0-vl
assert max([np.linalg.norm(enddelta)]+[np.linalg.norm(a) for a in offset.values()])<20,('Large seam shift requires road/pose check',color)
base=cv2.imread(str(r/'semantic-layers'/f'{color}-0-1'/'empty-map-padded.png'));h=cv2.cvtColor(base,cv2.COLOR_BGR2HSV);road=((h[:,:,0]>=85)&(h[:,:,0]<=125)&(h[:,:,1]>40)).astype(np.uint8);road=cv2.morphologyEx(road,cv2.MORPH_CLOSE,np.ones((21,21),np.uint8));clearance=cv2.distanceTransform(road,cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
def writer(path):return subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r','24','-i','pipe:0','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-threads','2','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
rawmovie=writer(out/f'composite-raw-{N/24:g}s.mp4');rows=[];norms=[];boundary={};seamframes={};bad=[];roadmetrics=[]
for i,path in enumerate(sources):
 k=next(k for k in range(5) if starts[k]<=i<=ends[k]);j=i-starts[k];length=ends[k]-starts[k]+1;shift=np.zeros(2)
 if k in offset:
  t=min(j/23,1);shift+=offset[k]*(1-3*t*t+2*t*t*t)
 if k==4:
  t=np.clip((j-(length-24))/23,0,1);shift+=(-2*t**3+3*t*t)*enddelta+(t**3-t*t)*23*derivative
 a=cv2.imread(str(path),-1).astype(np.float32);a[:,:,:3]*=a[:,:,3:4]/255
 if np.linalg.norm(shift)>1e-8:a=cv2.warpAffine(a,np.array([[1,0,shift[0]],[0,1,shift[1]]],np.float32),(1280,720))
 alpha=a[:,:,3]/255;rgb=np.divide(a[:,:,:3],alpha[:,:,None],out=np.zeros_like(a[:,:,:3]),where=alpha[:,:,None]>1e-6);layer=np.dstack((rgb,a[:,:,3])).clip(0,255).round().astype(np.uint8);comp=(a[:,:,:3]+base*(1-alpha[:,:,None])).clip(0,255).round().astype(np.uint8);cv2.imwrite(str(rawdir/f'{i:04d}.png'),layer);rawmovie.stdin.write(comp.tobytes());c=cab[i]+shift;x,y=c.round().astype(int);norms.append(float(np.linalg.norm(shift)))
 if layer[y,x,3]<128:bad.append(i)
 rows.append({'frame':i,'time':i/24,'source_segment':ids[i][0],'source_frame':ids[i][1],'cab_px':c.tolist(),'cab_roof_estimate':(c/[1280,720]).tolist(),'city_crop_roof_estimate':[(c[0]-121)/1037,c[1]/720],'translation_px':shift.tolist()});roadmetrics.append({'frame':i,'cab_roof_image_road_clearance_px':float(clearance[y,x]),'body_over_blue_road_fraction':float(road[layer[:,:,3]>127].mean())})
 if i in starts+ends:boundary[i]=(layer,comp)
 if j<24 or j>=length-24:seamframes[i]=comp
rawmovie.stdin.close();assert rawmovie.wait()==0
mapping=np.rint(np.arange(546)*(N-1)/545).astype(int);movie=writer(out/'composite-22.75s.mp4');common=[]
for i,raw_index in enumerate(mapping):
 f=rawdir/f'{raw_index:04d}.png';dst=rd/f'{i:04d}.png'
 if dst.exists():dst.unlink()
 os.link(f,dst);a=cv2.imread(str(f),-1);alpha=a[:,:,3:4]/255;comp=(a[:,:,:3]*alpha+base*(1-alpha)).clip(0,255).round().astype(np.uint8);movie.stdin.write(comp.tobytes());row=dict(rows[raw_index]);row.update(frame=i,time=i/24,raw_candidate_frame=int(raw_index));common.append(row)
movie.stdin.close();assert movie.wait()==0
panels=[];seams=[];review=cv2.VideoWriter(str(out/'seams-4x-source.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),24,(880,720))
for k in range(5):
 e,n=ends[k],starts[(k+1)%5];a,im0=boundary[e];b,im1=boundary[n];ys,xs=np.where((a[:,:,3]>127)|(b[:,:,3]>127));x=int(np.clip(xs.mean()-110,0,1060));y=int(np.clip(ys.mean()-90,0,540));tiles=[]
 for im,label in [(im0,segs[k]+' end'),(im1,segs[(k+1)%5]+' start')]:
  tile=im[y:y+180,x:x+220].copy();cv2.putText(tile,label,(4,18),0,.4,(0,0,0),1);tiles.append(tile)
 panels.append(np.hstack(tiles))
 for off in range(-24,24):
  idx=(n+off)%N;tile=cv2.resize(seamframes[idx][y:y+180,x:x+220],(880,720),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{color} seam{k} rawframe{idx}',(8,24),0,.6,(0,0,0),1);review.write(tile)
 steps=np.linalg.norm(np.diff([a['cab_px'] for a in rows[starts[k]:e+1]],axis=0),axis=1);seams.append({'from':segs[k],'to':segs[(k+1)%5],'raw_roof_step_px':rawsteps[k],'corrected_roof_step_px':float(np.linalg.norm(np.array(rows[n]['cab_px'])-rows[e]['cab_px'])),'previous_step_px':float(steps[-1]),'next_step_px':float(np.linalg.norm(np.array(rows[n+1]['cab_px'])-rows[n]['cab_px'])),'ordinary_median_step_px':float(np.median(steps)),'alpha_iou':float(((a[:,:,3]>127)&(b[:,:,3]>127)).sum()/((a[:,:,3]>127)|(b[:,:,3]>127)).sum())})
review.release();cv2.imwrite(str(out/'seams-native.png'),np.vstack(panels));subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(out/'seams-4x-source.mp4'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-threads','2',str(out/'seams-4x-review.mp4')],check=True)
for name,data in [('roof-tracking-raw.json',rows),('roof-tracking-22.75s.json',common)]:
 (out/name).write_text(json.dumps({'fps':24,'frames':len(data),'duration_seconds':len(data)/24,'dimensions':[1280,720],'hotspot':'Observed source upper-cab color centroid plus exact inverse local projection and rigid layer translation; image roof estimate','source_mapping':'Endpoint-inclusive nearest observed raw source poses; no opticalflow or generated poses','rows':data},indent=2))
report={'color':color,'gate':'PENDING decoded-output/native seam and actual fleet phase review','raw_frames':N,'raw_duration_seconds':N/24,'common_frames':546,'common_duration_seconds':22.75,'fps':24,'dimensions':[1280,720],'trim':{'red1-mid':'54..119 retained'} if color=='red' else {'yellow1-mid':'all120preserved; entire600pose route maps explicitly into546common frames'},'mapping':mapping.tolist(),'seams':seams,'ramp_frames':24,'max_translation_px':max(norms),'start_translations':{str(k):v.tolist() for k,v in offset.items()},'end_translation':enddelta.tolist(),'scale':1,'rotation':0,'deformation':False,'crossfade':False,'opticalflow':False,'added_shadow':False,'cab_roof_alpha_failures':bad,'min_roof_image_road_clearance_px':min(x['cab_roof_image_road_clearance_px'] for x in roadmetrics),'end_roof_image_road_clearance_px':roadmetrics[-1]['cab_roof_image_road_clearance_px'],'road_metric_limit':'Distance at projected ROOF image point to blue road with21px closing. Not wheel/world clearance; body coverage excludes curbs/crosswalk mask uncertainty.','road_metrics':roadmetrics,'driver_count':'UNCERTAIN'};(out/'gate-report.json').write_text(json.dumps(report,indent=2));print(color,'rendered',N,'raw /546common frames; max translation',max(norms),'cab failures',bad,flush=True)
