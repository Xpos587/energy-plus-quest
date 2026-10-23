from pathlib import Path
import sys,json,cv2,numpy as np
cv2.setNumThreads(1)
r=Path(__file__).resolve().parent; seg=sys.argv[1]; out=r/f'segment-{seg}-layer'; out.mkdir(exist_ok=True)
cap=cv2.VideoCapture(str(r/f'segment-{seg}.mp4')); frames=[]
while True:
 ok,f=cap.read()
 if not ok:break
 frames.append(f)
assert len(frames)==121
empty=cv2.imread(str(r.parents[1]/'four-truck-loop-2026-10-04/v2b-empty-map.png'))
base=np.full((720,1280,3),255,np.uint8); base[:,121:1158]=cv2.resize(empty,(1037,720))
ref=np.full_like(base,255); ref[:,311:968]=cv2.resize(empty[100:560,700:1120],(657,720))
x0,y0,x1,y1=340,45,850,680
stack=np.stack([f[y0:y1,x0:x1] for f in frames]); bg=np.median(stack,axis=0).astype(np.uint8)
variation=np.max(np.percentile(stack,95,axis=0)-np.percentile(stack,5,axis=0),axis=2)>14
refroi=ref[y0:y1,x0:x1]; hsvbg=cv2.cvtColor(bg,cv2.COLOR_BGR2HSV); hsvref=cv2.cvtColor(refroi,cv2.COLOR_BGR2HSV)
# Slow trailer can occupy pixels for a majority of a half-corner. Restore such road pixels from the clean reference.
road=(hsvref[:,:,0]>85)&(hsvref[:,:,0]<120)&(hsvref[:,:,1]>40)
contam=road&((hsvbg[:,:,1]<70)|((hsvbg[:,:,0]>35)&(hsvbg[:,:,0]<85)))
bg[contam]=refroi[contam]
cv2.imwrite(str(out/'background.png'),bg)
allowed=np.zeros(bg.shape[:2],np.uint8)
for a,b,c,d in [(340,80,805,220),(370,130,590,680)]:cv2.rectangle(allowed,(a-x0,b-y0),(c-x0,d-y0),255,-1)
scale=460/1045; M=np.array([[scale,0,121+700*720/1045-311*scale],[0,scale,100*720/1045]],np.float32)
prev=np.array(([544,130] if seg=='2a' else [452,172]),np.float32)-[x0,y0]
rd=out/'rgba-frames';cd=out/'composite-frames';rd.mkdir(exist_ok=True);cd.mkdir(exist_ok=True);records=[];panels=[]
for i,f in enumerate(frames):
 crop=f[y0:y1,x0:x1]; hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV); delta=np.max(abs(crop.astype(np.int16)-bg.astype(np.int16)),axis=2)
 motion=((delta>10)&(allowed>0)).astype(np.uint8)*255
 green=((hsv[:,:,0]>=35)&(hsv[:,:,0]<=90)&(hsv[:,:,1]>65)&(hsv[:,:,2]>35)&(allowed>0)).astype(np.uint8)*255
 n,l,s,c=cv2.connectedComponentsWithStats(green); cand=[j for j in range(1,n) if s[j,4]>80];cab=min(cand,key=lambda j:np.linalg.norm(c[j]-prev)-min(s[j,4],1000)*.008);prev=c[cab];seed=(l==cab).astype(np.uint8)*255
 white=((hsv[:,:,1]<20)&(hsv[:,:,2]>170)&(motion>0)).astype(np.uint8)*255;white=cv2.morphologyEx(white,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
 white=cv2.erode(white,np.ones((5,5),np.uint8));n,l,s,c=cv2.connectedComponentsWithStats(white);cand=[j for j in range(1,n) if 800<s[j,4]<22000 and np.linalg.norm(c[j]-prev)<280];tr=max(cand,key=lambda j:s[j,4]/(np.linalg.norm(c[j]-prev)+50));w=(l==tr).astype(np.uint8)*255
 support=np.zeros_like(seed);cs=np.zeros_like(seed);ts=np.zeros_like(seed)
 cv2.fillConvexPoly(cs,cv2.convexHull(cv2.findNonZero(seed)),255);cv2.fillConvexPoly(ts,cv2.convexHull(cv2.findNonZero(w)),255)
 cabcore=cs.copy();cs=cv2.dilate(cs,np.ones((17,17),np.uint8));ts=cv2.dilate(ts,np.ones((13,13),np.uint8))
 # Trailer outline lines bound the rigid white body, preventing the slow-turn curb from joining its support.
 if seg=='2a':
  lines=cv2.HoughLinesP(cv2.Canny(crop,50,130),1,np.pi/180,40,minLineLength=100,maxLineGap=12)
  above=[];below=[];wc=c[tr]
  if lines is not None:
   for q in lines.reshape(-1,4):
    lx0,ly0,lx1,ly1=map(float,q)
    if lx1<lx0:lx0,ly0,lx1,ly1=lx1,ly1,lx0,ly0
    slope=(ly1-ly0)/max(lx1-lx0,1)
    if abs(slope)>.4 or not lx0<=wc[0]<=lx1 or not 110<lx1-lx0<245:continue
    yy=ly0+slope*(wc[0]-lx0)
    if 15<wc[1]-yy<70:above.append((wc[1]-yy,[lx0,ly0,lx1,ly1]))
    if 8<yy-wc[1]<60:below.append((yy-wc[1],[lx0,ly0,lx1,ly1]))
  if above and below:
   up=min(above)[1];down=min(below)[1];left=float(s[tr,0]-5);right=left+min(max(float(s[tr,2]+10),180),195);su=(up[3]-up[1])/(up[2]-up[0]);topline=lambda x:up[1]+su*(x-up[0]);bot=lambda x:topline(x)+62;up=[left,topline(left),right,topline(right)]
   polygon=np.array([[left-2,up[1]-2],[right+2,up[3]-2],[right+2,bot(right)+12],[left-2,bot(left)+12]],np.int32)
   ts=np.zeros_like(ts);cv2.fillConvexPoly(ts,polygon,255)
   roof=np.array([[left,up[1]],[right,up[3]],[right,bot(right)],[left,bot(left)]],np.int32);core=np.zeros_like(ts);cv2.fillConvexPoly(core,roof,255)
  else:core=np.zeros_like(ts)
 else:core=np.zeros_like(ts)
 support=((cs>0)|((ts>0)&((hsv[:,:,1]<20)|(hsv[:,:,2]<105)))).astype(np.uint8)*255
 body=cv2.bitwise_and(motion,support);body[seed>0]=255
 body[(core>0)&(hsv[:,:,1]<25)]=255
 # Drop support fragments disconnected from the actual cab or white trailer cores.
 n2,l2,s2,c2=cv2.connectedComponentsWithStats(body); keep=np.unique(l2[(seed>0)|(w>0)]);keep=keep[keep>0];body=np.isin(l2,keep).astype(np.uint8)*255
 contours,_=cv2.findContours(body,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(body,contours,-1,255,cv2.FILLED)
 body[(cs==0)&(hsv[:,:,1]>=20)&(hsv[:,:,2]>=105)]=0
 body[(cabcore==0)&(hsv[:,:,0]>=85)&(hsv[:,:,0]<=120)&(hsv[:,:,1]>40)&(hsv[:,:,2]>120)]=0
 edge=cv2.GaussianBlur(body,(3,3),.6).astype(np.float32)/255; broad=cv2.dilate(body,np.ones((31,31),np.uint8))>0
 shadow=np.clip((np.mean(bg.astype(float)-crop.astype(float),axis=2)-3)/np.maximum(np.mean(bg,axis=2),30),0,.45)*(broad&(body==0)&(allowed>0));shadow=cv2.GaussianBlur(shadow.astype(np.float32),(7,7),1.5)
 a=edge+(1-edge)*shadow;premul=crop.astype(np.float32)*edge[:,:,None]
 af=np.zeros((720,1280),np.float32);pf=np.zeros((720,1280,3),np.float32);af[y0:y1,x0:x1]=a;pf[y0:y1,x0:x1]=premul
 aa=cv2.warpAffine(af,M,(1280,720));pp=cv2.warpAffine(pf,M,(1280,720));rgb=np.divide(pp,aa[:,:,None],out=np.zeros_like(pp),where=aa[:,:,None]>1e-6)
 layer=np.dstack((np.clip(rgb,0,255).round().astype(np.uint8),(aa*255).round().astype(np.uint8))); comp=np.clip(pp+base*(1-aa[:,:,None]),0,255).round().astype(np.uint8)
 cv2.imwrite(str(rd/f'{i+1:04}.png'),layer);cv2.imwrite(str(cd/f'{i+1:04}.png'),comp)
 ys,xs=np.where(aa>.5); records.append({'frame':i+1,'centroid':[float(xs.mean()),float(ys.mean())],'bbox':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]})
 if i in [0,12,42,60,84,114,120]:
  checker=np.full_like(base,230);isolated=np.clip(pp+checker*(1-aa[:,:,None]),0,255).astype(np.uint8)
  detail=np.concatenate([f[30:680,330:860],isolated[65:400,600:880],comp[65:400,600:880]],axis=1) if False else np.concatenate([isolated[65:400,600:880],comp[65:400,600:880]],axis=1)
  cv2.imwrite(str(out/f'detail-{i+1:04}.png'),detail);panels.append(detail)
cv2.imwrite(str(out/'detail-contact.jpg'),np.concatenate(panels,axis=0));(out/'extraction-report.json').write_text(json.dumps({'segment':seg,'frames':121,'fps':24,'crop_to_full_affine':M.tolist(),'records':records,'visual_acceptance':'pending'},indent=2));print(seg,'extracted',flush=True)
