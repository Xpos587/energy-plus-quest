"""Technical alpha candidate. Motion approval is deliberately pending independent review."""
from pathlib import Path
import sys,json,cv2,numpy as np
from roof_edges import roof_polygon
cv2.setNumThreads(1);root=Path(__file__).resolve().parent;color,seg=sys.argv[1:3]
configs={
'0-1':((690,65,1005,320),[(930,65,1004,319),(690,65,1004,175)],(977,210)),
'1-mid':((340,45,850,680),[(340,80,805,220),(370,130,590,680)],(571,126)),
'mid-2':((340,45,850,680),[(340,80,805,220),(370,130,590,680)],(459,158)),
'2-3':((605,220,940,620),[(620,220,720,620),(620,505,940,620)],(672,320)),
'3-0':((760,170,1020,620),[(760,515,1020,620),(925,170,1020,620)],(877,575))}
roi,roads,init=configs[seg];x0,y0,x1,y1=roi;local=seg in ['1-mid','mid-2'];q=1045/460 if local else 1
out=root/f'{color}-{seg}-layer';out.mkdir(exist_ok=True);rd=out/'rgba-frames';rd.mkdir(exist_ok=True)
cap=cv2.VideoCapture(str(root.parent/f'{color}-{seg}.mp4'));fps=cap.get(cv2.CAP_PROP_FPS);frames=[]
while True:
 ok,f=cap.read()
 if not ok:break
 frames.append(f)
assert fps==24 and len(frames)==121 and frames[0].shape==(720,1280,3)
empty=cv2.imread(str(root.parents[1]/'four-truck-loop-2026-10-04/v2b-empty-map.png'));base=np.full((720,1280,3),255,np.uint8);base[:,121:1158]=cv2.resize(empty,(1037,720),interpolation=cv2.INTER_LANCZOS4)
ref=base.copy()
if local:ref[:]=255;ref[:,311:968]=cv2.resize(empty[100:560,700:1120],(657,720))
M=np.array([[460/1045,0,121+700*720/1045-311*460/1045],[0,460/1045,100*720/1045]],np.float32) if local else np.array([[1,0,0],[0,1,0]],np.float32)
stack=np.stack([f[y0:y1,x0:x1] for f in frames]);bg=np.median(stack,axis=0).astype(np.uint8);rr=ref[y0:y1,x0:x1];bh=cv2.cvtColor(bg,cv2.COLOR_BGR2HSV);rh=cv2.cvtColor(rr,cv2.COLOR_BGR2HSV);var=np.max(np.percentile(stack,95,axis=0)-np.percentile(stack,5,axis=0),axis=2)
cab_background=(((bh[:,:,0]<12)|(bh[:,:,0]>170)) if color=='red' else ((bh[:,:,0]>=15)&(bh[:,:,0]<=35)))&(bh[:,:,1]>100)
road_reference=((rh[:,:,0]>=85)&(rh[:,:,0]<=125)&(rh[:,:,1]>40)).astype(np.uint8)*255;road_reference=cv2.morphologyEx(road_reference,cv2.MORPH_CLOSE,np.ones((round(21*q)|1,round(21*q)|1),np.uint8));road_reference=cv2.dilate(road_reference,np.ones((round(3*q)|1,round(3*q)|1),np.uint8))
bg[cab_background&((rh[:,:,0]>=85)&(rh[:,:,0]<=125)&(rh[:,:,1]>40))]=rr[cab_background&((rh[:,:,0]>=85)&(rh[:,:,0]<=125)&(rh[:,:,1]>40))]
restore=(bh[:,:,1]<85)&(bh[:,:,2]>170)&(rh[:,:,0]>=85)&(rh[:,:,0]<=120)&(rh[:,:,1]>40)&(var>20);bg[restore]=rr[restore];mad=np.median(np.max(abs(stack.astype(np.int16)-bg.astype(np.int16)),axis=3),axis=0);threshold=np.maximum(25,mad*3+10);threshold[restore]=25
allowed=np.zeros(bg.shape[:2],np.uint8)
for a,b,c,d in roads:cv2.rectangle(allowed,(a-x0,b-y0),(c-x0,d-y0),255,-1)
cv2.imwrite(str(out/'background.png'),bg);cv2.imwrite(str(out/'empty-map-padded.png'),base)
tr_init={'0-1':(975,264),'1-mid':(695,127),'mid-2':(638,145),'2-3':(674,255),'3-0':(817,575)}
tr_prev=np.array(tr_init[seg],float)-[x0,y0];edge_failures=[]
prev=np.array(init,float)-[x0,y0];vel=np.zeros(2);yy,xx=np.indices(bg.shape[:2]);rows=[];metrics=[];panels=[]
for i,f in enumerate(frames):
 crop=f[y0:y1,x0:x1];h=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV);delta=np.max(abs(crop.astype(np.int16)-bg.astype(np.int16)),axis=2);motion=((delta>threshold)&(allowed>0)).astype(np.uint8)*255
 color_mask=(((h[:,:,0]<12)|(h[:,:,0]>170)) if color=='red' else ((h[:,:,0]>=15)&(h[:,:,0]<=35)))&(h[:,:,1]>100)&(h[:,:,2]>35)&(allowed>0)&(delta>12)&((rh[:,:,0]>=85)&(rh[:,:,0]<=125)&(rh[:,:,1]>40))
 pred=prev+vel*.5;near=(xx-pred[0])**2+(yy-pred[1])**2<(25*q)**2;weights=np.clip((h[:,:,1].astype(float)-100)/155,0,1)**3*(1+np.clip(delta,0,80))*(color_mask&near)
 assert weights.sum()>0,(color,seg,i,'cab seed');cab=np.array([(weights*xx).sum()/weights.sum(),(weights*yy).sum()/weights.sum()]);v=cab-prev;vel=v*min(1,7*q/max(np.linalg.norm(v),1e-6));prev=cab
 seed=(color_mask&((xx-cab[0])**2+(yy-cab[1])**2<(26*q)**2)).astype(np.uint8)*255
 white=((h[:,:,1]<85)&(h[:,:,2]>150)&(allowed>0)).astype(np.uint8)*255;white=cv2.morphologyEx(white,cv2.MORPH_CLOSE,np.ones((round(5*q)|1,round(5*q)|1),np.uint8));white_raw=white.copy();white=cv2.morphologyEx(white,cv2.MORPH_OPEN,np.ones((round(7*q)|1,round(7*q)|1),np.uint8));n,l,st,ct=cv2.connectedComponentsWithStats(white)
 edge_result=roof_polygon(crop,cab,tr_prev+v*.5,q)
 if edge_result is not None:
  poly,tr_prev=edge_result;tm=np.zeros_like(seed);cv2.fillConvexPoly(tm,poly,255)
 else:
  edge_failures.append(i);candidates=[j for j in range(1,n) if 150*q*q<st[j,4]<8000*q*q and np.linalg.norm(ct[j]-tr_prev)<28*q];assert candidates,(color,seg,i,'roof edge and trailer')
  tr=min(candidates,key=lambda j:np.linalg.norm(ct[j]-tr_prev));tm=(l==tr).astype(np.uint8)*255;tr_prev=ct[tr]
 cs=np.zeros_like(seed);ts=np.zeros_like(seed);cv2.fillConvexPoly(cs,cv2.convexHull(cv2.findNonZero(seed)),255);cv2.fillConvexPoly(ts,cv2.convexHull(cv2.findNonZero(tm)),255);core=cs.copy();cs=cv2.dilate(cs,np.ones((round(9*q)|1,round(9*q)|1),np.uint8));tc=ts.copy();ts=cv2.dilate(ts,np.ones((round(7*q)|1,round(7*q)|1),np.uint8))
 support=((cs>0)|((ts>0)&((h[:,:,1]<85)|(h[:,:,2]<105)))).astype(np.uint8)*255;body=cv2.bitwise_and(motion,support);body[(ts>0)&(h[:,:,2]<130)]=255;body[tc>0]=255;body[core>0]=255;body[tm>0]=255
 ws=cv2.dilate(tc,np.ones((round(19*q)|1,round(13*q)|1),np.uint8));body[(tc>0)&(h[:,:,1]<65)&(h[:,:,2]>130)]=255
 contours,_=cv2.findContours(body,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(body,contours,-1,255,cv2.FILLED);body[(cs==0)&(tc==0)&(h[:,:,1]>=85)&(h[:,:,2]>=105)]=0;body[(cs==0)&(h[:,:,0]>=85)&(h[:,:,0]<=125)&(h[:,:,1]>40)&(h[:,:,2]>120)]=0
 n,l,st,ct=cv2.connectedComponentsWithStats(body);keep=np.unique(l[(seed>0)|(tm>0)]);keep=keep[keep>0];body=np.isin(l,keep).astype(np.uint8)*255
 edge=cv2.GaussianBlur(body,(3,3),.6).astype(np.float32)/255;broad=cv2.dilate(body,np.ones((round(5*q)|1,round(5*q)|1),np.uint8))>0;dark=np.mean(bg.astype(float)-crop.astype(float),axis=2);shadow=np.clip((dark-3)/np.maximum(np.mean(bg,axis=2),30),0,.45)*(broad&(body==0)&(allowed>0));shadow=cv2.GaussianBlur(shadow.astype(np.float32),(5,5),1);a=edge+(1-edge)*shadow
 aa=np.zeros((720,1280),np.float32);pp=np.zeros((720,1280,3),np.float32);aa[y0:y1,x0:x1]=a;pp[y0:y1,x0:x1]=crop*edge[:,:,None]
 if local:aa=cv2.warpAffine(aa,M,(1280,720));pp=cv2.warpAffine(pp,M,(1280,720))
 rgb=np.divide(pp,aa[:,:,None],out=np.zeros_like(pp),where=aa[:,:,None]>1e-6);layer=np.dstack((rgb.clip(0,255).round().astype(np.uint8),(aa*255).round().astype(np.uint8)));cv2.imwrite(str(rd/f'{i+1:04}.png'),layer)
 observed=cab+[x0,y0];mapped=M@np.r_[observed,1];cx,cy=mapped.round().astype(int);rows.append({'frame':i,'source_cab_px':observed.tolist(),'cab_px':mapped.tolist(),'cab_roof_estimate':(mapped/[1280,720]).tolist()});metrics.append({'frame':i,'cab_alpha':int(layer[cy,cx,3]),'opaque_pixels':int((aa>.9).sum()),'white_pixels':int(((aa>.9)&(cv2.cvtColor(layer[:,:,:3],cv2.COLOR_BGR2HSV)[:,:,1]<20)).sum())})
 if i%6==0:
  iso=(pp+230*(1-aa[:,:,None])).clip(0,255).astype(np.uint8);ys,xs=np.where(aa>.5);x=int(np.clip((xs.min()+xs.max())/2-95,0,1090));y=int(np.clip((ys.min()+ys.max())/2-95,0,530));tile=cv2.resize(iso[y:y+190,x:x+190],(380,380),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{i/24:.2f}s',(8,23),0,.6,(0,0,0),1);panels.append(tile)
while len(panels)%7:panels.append(np.full((380,380,3),230,np.uint8))
cv2.imwrite(str(out/'quarter-alpha.jpg'),np.vstack([np.hstack(panels[j:j+7]) for j in range(0,len(panels),7)]))
(out/'cab-tracking.json').write_text(json.dumps({'fps':24,'frames':121,'dimensions':[1280,720],'crop_to_full_affine':M.tolist(),'hotspot':'Observed source cab-color image centroid, exact crop projection; not3D anchor','rows':rows},indent=2));report={'source':str(root.parent/f'{color}-{seg}.mp4'),'fps':24,'frames':121,'dimensions':[1280,720],'gate':'PENDING independent motion and alpha review','roof_edge_fallback_frames':edge_failures,'cab_alpha_failures':[r['frame'] for r in metrics if r['cab_alpha']<128],'metrics':metrics};(out/'extraction-report.json').write_text(json.dumps(report,indent=2));print(color,seg,'extracted121; cab_alpha_failures',report['cab_alpha_failures'],flush=True)
