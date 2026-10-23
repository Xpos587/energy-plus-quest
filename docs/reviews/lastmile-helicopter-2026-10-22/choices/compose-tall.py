from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import cv2,numpy as np,json
P=Path(__file__).resolve().parent;D=P.parent
ref=cv2.imread(str(D/'choice-tall-candidate.png'));target=cv2.imread(str(D/'choice-tall-helicopter-target.png'))
ma=np.full(ref.shape[:2],255,np.uint8);mb=np.full(target.shape[:2],255,np.uint8);cv2.rectangle(ma,(240,60),(1430,710),0,-1);cv2.rectangle(mb,(220,20),(1110,650),0,-1)
s=cv2.SIFT_create(nfeatures=10000);ka,da=s.detectAndCompute(ref,ma);kb,db=s.detectAndCompute(target,mb);g=[m for m,n in cv2.BFMatcher().knnMatch(da,db,k=2) if m.distance<.72*n.distance];x=np.float32([ka[m.queryIdx].pt for m in g]);y=np.float32([kb[m.trainIdx].pt for m in g]);M,ok=cv2.estimateAffinePartial2D(x,y,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=10000);err=np.linalg.norm(cv2.transform(x[None],M)[0]-y,axis=1);keep=ok.ravel().astype(bool);r={'matrix':M.tolist(),'matches':len(g),'inliers':int(keep.sum()),'p95TargetPx':float(np.percentile(err[keep],95)),'basis':'background only broad aircraft exclusion, similarity transform only'};print(json.dumps(r));(P/'tall-registration.json').write_text(json.dumps(r,indent=2));aligned=cv2.warpAffine(ref,M,(target.shape[1],target.shape[0]),flags=cv2.INTER_LANCZOS4);Image.fromarray(cv2.cvtColor(aligned,cv2.COLOR_BGR2RGB)).save(P/'tall-aligned.png')
# Build new-aircraft envelope in candidate coordinates, old aircraft+shadow in target coordinates.
n=Image.new('L',(ref.shape[1],ref.shape[0]));d=ImageDraw.Draw(n);d.polygon([(275,445),(285,405),(570,310),(295,280),(290,245),(620,275),(580,150),(625,130),(745,270),(1100,175),(1130,215),(820,300),(1090,255),(1290,235),(1300,70),(1330,55),(1365,150),(1425,170),(1435,210),(1360,230),(1370,280),(1325,300),(1280,360),(1160,415),(1140,475),(1090,470),(960,420),(955,520),(900,610),(840,640),(800,680),(530,710),(390,650),(380,540)],fill=255)
mask=cv2.warpAffine(np.array(n),M,(target.shape[1],target.shape[0]));m=Image.fromarray(mask);d=ImageDraw.Draw(m)
d.polygon([(235,400),(235,365),(580,255),(340,200),(340,165),(610,220),(890,120),(940,130),(950,165),(725,255),(1045,350),(1045,390),(850,350),(850,450),(820,530),(745,570),(650,640),(470,655),(380,610),(370,530)],fill=255)
d.polygon([(745,300),(900,200),(950,50),(995,20),(1045,35),(1040,95),(1100,105),(1100,150),(1050,160),(1100,180),(1090,205),(1040,200),(1030,250),(1080,275),(1070,300),(970,310)],fill=255)
d.polygon([(415,575),(510,560),(725,450),(975,320),(1170,340),(1170,410),(1060,465),(1020,535),(890,550),(735,650),(535,675),(405,635)],fill=255)
# Explicit original cone and windsock protection, all four cones excluded.
for box in [(20,475,120,630),(185,170,275,310),(1325,325,1435,480),(850,680,965,825),(1360,90,1580,340)]: d.rectangle(box,fill=0)
m=m.filter(ImageFilter.GaussianBlur(1.2));m.save(P/'tall-aircraft-shadow-union-target-mask.png')
rows=[]
for name in ['alva','khor','arseniy']:
 src=Path('public/scene-art/lastmile-family-v1/revision-4')/f'choice-tall-{name}.webp';im=Image.open(src).convert('RGB')
 if name=='alva':base=Image.open('.tmp-work/flowers-all-2026-10-20/F0111/pass2-master.png').convert('RGB');basis='accepted P2 F0111'
 else:base=im.resize((round(im.width*5250/im.height),5250),Image.Resampling.LANCZOS);basis='ordinary Lanczos interpolation; not Flowers'
 sx=base.width/4681;sy=base.height/8192;box=[round(1383*sx),round(2074*sy),round(2963*sx),round(3012*sy)];sz=(box[2]-box[0],box[3]-box[1]);base.paste(Image.fromarray(cv2.cvtColor(aligned,cv2.COLOR_BGR2RGB)).resize(sz,Image.Resampling.LANCZOS),tuple(box[:2]),m.resize(sz,Image.Resampling.LANCZOS));out=P/f'choice-tall-{name}-helicopter-corrected.png';base.save(out);base.save(out.with_suffix('.webp'),lossless=True,method=4);base.crop((box[0]-20,box[1]-20,box[2]+20,box[3]+20)).save(P/f'choice-tall-{name}-heli-seam-100pct.png');thumb=base.copy();thumb.thumbnail((1000,1659));thumb.save(P/f'choice-tall-{name}-full-review.png');rows.append({'source':str(src),'output':str(out),'dimensions':list(base.size),'basis':basis,'patchBox':box})
(P/'tall-composition-receipt.json').write_text(json.dumps({'registration':r,'outputs':rows,'mask':'tall-aircraft-shadow-union-target-mask.png','limits':'Only masked aircraft/shadow area changes; cones/windsock protected. Ordinary resized bases do not recover details.'},indent=2))
