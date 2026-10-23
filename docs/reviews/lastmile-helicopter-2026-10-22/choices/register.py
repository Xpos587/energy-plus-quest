import cv2,numpy as np,json
from pathlib import Path
P=Path(__file__).resolve().parent; D=P.parent
ref=cv2.imread(str(D/'choice-wide-refined.png'));target=cv2.imread(str(D/'choice-wide-helicopter-target.png'))
def reg(a,b,ma=None,mb=None):
 s=cv2.SIFT_create(nfeatures=10000);ka,da=s.detectAndCompute(a,ma);kb,db=s.detectAndCompute(b,mb);pairs=cv2.BFMatcher().knnMatch(da,db,k=2);g=[m for m,n in pairs if m.distance<.72*n.distance];x=np.float32([ka[m.queryIdx].pt for m in g]);y=np.float32([kb[m.trainIdx].pt for m in g]);M,ok=cv2.estimateAffinePartial2D(x,y,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=10000);r=np.linalg.norm(cv2.transform(x[None],M)[0]-y,axis=1);keep=ok.ravel().astype(bool);return M,{'matches':len(g),'inliers':int(keep.sum()),'p95':float(np.percentile(r[keep],95)),'matrix':M.tolist()}
ma=np.full(ref.shape[:2],255,np.uint8);mb=np.full(target.shape[:2],255,np.uint8)
# Broad exclusions contain old/new aircraft and shadow; only trees, pad border, paving, cones and windsock participate.
cv2.rectangle(ma,(230,85),(1260,680),0,-1);cv2.rectangle(mb,(270,75),(1390,760),0,-1)
M,r=reg(ref,target,ma,mb);r['basis']='background only; broad aircraft/shadow rectangles excluded';cv2.imwrite(str(P/'refined-background-mask.png'),ma);cv2.imwrite(str(P/'target-background-mask.png'),mb)
wide=cv2.imread('public/scene-art/lastmile-family-v1/revision-4/choice-wide-alva.webp');tall=cv2.imread('public/scene-art/lastmile-family-v1/revision-4/choice-tall-alva.webp');a=wide[15:260,850:1300];b=tall[405:615,235:610];am=np.full(a.shape[:2],255,np.uint8);bm=np.full(b.shape[:2],255,np.uint8);cv2.rectangle(am,(65,20),(340,192),0,-1);cv2.rectangle(bm,(85,20),(275,160),0,-1)
N,q=reg(a,b,am,bm);r={'refinedToTarget':r,'wideCropToTallCrop':q};(P/'registration.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));cv2.imwrite(str(P/'tall-registration-target.png'),b);cv2.imwrite(str(P/'wide-registration-target.png'),a)
