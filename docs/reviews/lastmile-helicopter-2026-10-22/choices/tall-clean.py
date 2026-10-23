from pathlib import Path
import cv2,numpy as np,json
from PIL import Image
P=Path(__file__).resolve().parent;D=P.parent
old=cv2.imread(str(D/'choice-tall-helicopter-target.png'));new=cv2.imread(str(P/'tall-aligned.png'))
quad=np.float32([[563,211],[1272,415],[826,765],[111,541]]);dst=np.float32([[0,0],[1000,0],[1000,500],[0,500]]);H=cv2.getPerspectiveTransform(quad,dst);rect=cv2.warpPerspective(old,H,(1000,500));cv2.imwrite(str(P/'tall-pad-rectified.png'),rect)
# Aircraft classifier only inside explicitly drawn plausible envelope; no candidate pad transfer.
env=cv2.imread(str(P/'tall-aircraft-shadow-union-target-mask.png'),0)>128
hsv=cv2.cvtColor(new,cv2.COLOR_BGR2HSV);h,s,v=cv2.split(hsv)
fg=(((v<155)&((s<160)|(h>90)))|((h<23)&(s>185)&(v>100)))&env
# Exclude unmodified forest zone above aircraft rotor/left/top.
fg[:60,:]=False;fg[:190,:550]=False;fg[:210,1050:1280]=False
mask=np.zeros(old.shape[:2],np.uint8)
for c in cv2.findContours((fg*255).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]:
 if cv2.contourArea(c)>8:cv2.drawContours(mask,[c],-1,255,-1)
cv2.imwrite(str(P/'tall-aircraft-only-alpha.png'),mask);rgba=cv2.cvtColor(new,cv2.COLOR_BGR2BGRA);rgba[:,:,3]=mask;cv2.imwrite(str(P/'tall-aircraft-only.png'),rgba)
# Manually bounded aircraft envelope excludes all forest/paving; classifier only refines its edges.
e=np.zeros(old.shape[:2],np.uint8)
cv2.fillPoly(e,[np.array([(380,575),(395,520),(430,465),(525,420),(555,365),(650,330),(770,340),(925,370),(945,435),(915,495),(855,545),(805,575),(565,630),(440,605)])],255)
cv2.fillPoly(e,[np.array([(820,335),(1105,270),(1240,235),(1285,170),(1310,170),(1290,270),(1230,315),(890,395)])],255)
for a,b,w in [((700,295),(300,250),29),((700,295),(595,145),39),((700,295),(1080,200),31),((700,295),(1100,435),33),((700,295),(285,425),34),((1295,170),(1275,80),30),((1295,170),(1375,190),30),((1295,170),(1320,255),30),((1225,300),(1230,345),12),((1210,305),(1230,345),10)]:cv2.line(e,a,b,255,w)
cv2.ellipse(e,(545,610),(31,38),0,0,360,255,-1);cv2.ellipse(e,(820,560),(31,38),0,0,360,255,-1)
fg=(((v<155)&((s<160)|(h>90)))|((h<23)&(s>185)&(v>100)))&(e>0)
mask=np.zeros(old.shape[:2],np.uint8)
for c in cv2.findContours((fg*255).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0]:
 if cv2.contourArea(c)>5:cv2.drawContours(mask,[c],-1,255,-1)
cv2.imwrite(str(P/'tall-aircraft-only-alpha.png'),mask)
# Clean original projected pad using its known corners and rectified visible H arms.
yy,xx=np.indices(rect.shape[:2]);hv=cv2.cvtColor(rect,cv2.COLOR_BGR2HSV);sel=(hv[:,:,1]<75)&(hv[:,:,2]>145)&(hv[:,:,2]<218)&((xx<170)|(xx>800)|(yy>420));A=np.stack([np.ones(sel.sum()),xx[sel]/1000,yy[sel]/500],axis=1);plane=np.empty_like(rect)
for ch in range(3):
 vals=rect[:,:,ch][sel];coef=np.linalg.lstsq(A,vals,rcond=None)[0];pred=coef[0]+coef[1]*xx/1000+coef[2]*yy/500;plane[:,:,ch]=np.clip(pred,0,255)
cv2.rectangle(plane,(190,140),(280,380),(245,246,251),-1);cv2.rectangle(plane,(680,140),(775,380),(245,246,251),-1);cv2.rectangle(plane,(280,235),(680,285),(245,246,251),-1)
plate=cv2.warpPerspective(plane,np.linalg.inv(H),(old.shape[1],old.shape[0]));padmask=np.zeros(old.shape[:2],np.uint8);cv2.fillPoly(padmask,[quad.astype(int)],255)
rem=cv2.imread(str(P/'tall-aircraft-shadow-union-target-mask.png'),0);rem=(rem>20).astype('uint8')*255
# Mask is bounded to obsolete aircraft/shadow; original surrounding pixels remain intact.
clean=cv2.inpaint(old,rem,5,cv2.INPAINT_TELEA);clean[(rem>0)&(padmask>0)]=plate[(rem>0)&(padmask>0)]
# Preserve original visible white H / border wherever no obsolete aircraft exists.
cv2.imwrite(str(P/'tall-cleanplate.png'),clean);cv2.imwrite(str(P/'tall-old-removal-mask.png'),rem)
a=cv2.GaussianBlur(mask,(0,0),.45)/255;shadow=cv2.GaussianBlur(mask,(0,0),12);shadow=np.roll(np.roll(shadow,20,axis=0),12,axis=1)/255*.24;comp=clean.astype(float)*(1-shadow[:,:,None]);comp=comp*(1-a[:,:,None])+new*a[:,:,None];cv2.imwrite(str(P/'tall-representative-v2.png'),np.clip(comp,0,255).astype('uint8'))
# v3: explicit enclosed tail/body silhouette and narrowly stroked obsolete silhouette.
newmask=mask.copy();cv2.fillPoly(newmask,[np.array([(850,330),(1115,260),(1240,235),(1280,180),(1305,170),(1285,265),(1230,300),(910,395)])],255)
# Preserve whole white bands inside enclosed tail, not hue-selected holes.
cv2.fillPoly(newmask,[np.array([(1010,285),(1160,250),(1175,325),(1030,365)])],255)
# Eliminate colored fringe by eroding classifier edges only at tail rotor and blades.
newmask=cv2.erode(newmask,np.ones((2,2),np.uint8));
rem=np.zeros(old.shape[:2],np.uint8)
cv2.fillPoly(rem,[np.array([(385,555),(390,470),(440,400),(510,345),(600,300),(730,310),(820,340),(855,420),(820,490),(780,530),(715,565),(660,600),(615,635),(475,615)])],255)
cv2.fillPoly(rem,[np.array([(765,325),(915,225),(960,135),(980,40),(1020,25),(1040,45),(1025,205),(1060,230),(1010,270),(860,350)])],255)
for a,b,w in [((640,260),(255,380),38),((640,260),(360,185),33),((640,260),(920,135),40),((640,260),(1030,370),38),((1020,120),(960,90),35),((1020,120),(1080,116),35),((1020,120),(1080,180),35)]:cv2.line(rem,a,b,255,w)
cv2.fillPoly(rem,[np.array([(410,570),(520,550),(690,450),(875,380),(1075,355),(1175,390),(1080,420),(1040,470),(950,475),(850,525),(700,590),(560,635),(430,620)])],255)
# Reconstruct only hidden pad interior; exact authored border and surrounding paving preserved.
inner=cv2.erode(padmask,np.ones((12,12),np.uint8));inside=(rem>0)&(inner>0);outside=(rem>0)&(padmask==0)
# Narrow old tail/rotor inpainting only; no forest envelope.
inp=cv2.inpaint(old,(outside*255).astype('uint8'),9,cv2.INPAINT_TELEA);clean=old.copy();clean[outside]=inp[outside]
blend=cv2.GaussianBlur((inside*255).astype('uint8'),(0,0),10)/255;blend[padmask==0]=0;clean=clean*(1-blend[:,:,None])+plate*blend[:,:,None]
# Pad gradient harmonized at restoration boundary, then enclosed silhouette pasted.
a=cv2.GaussianBlur(newmask,(0,0),.4)/255;shadow=cv2.GaussianBlur(newmask,(0,0),14);shadow=np.roll(np.roll(shadow,18,axis=0),10,axis=1)/255*.2;shadow[inner==0]=0;comp=clean*(1-shadow[:,:,None]);comp=comp*(1-a[:,:,None])+new*a[:,:,None];cv2.imwrite(str(P/'tall-representative-v3.png'),np.clip(comp,0,255).astype('uint8'));cv2.imwrite(str(P/'tall-aircraft-only-alpha-v3.png'),newmask);cv2.imwrite(str(P/'tall-removal-mask-v3.png'),rem)
