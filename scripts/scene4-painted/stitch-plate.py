"""Register and feather background tiles; keep native canvas and save measured drift."""
from pathlib import Path
import cv2, json, sys
import numpy as np
p=Path('.tmp-work/scene4-final-render/gpt')
format=sys.argv[1]
m=json.loads((p/f'v4-plate-{format}-tiles.json').read_text())
H,W=m['height'],m['width']
total=np.zeros((H,W,3),np.float32); weights=np.zeros((H,W),np.float32); receipts=[]
for tile in m['tiles']:
 name=tile['name'];w,h=tile['width'],tile['height'];x,y=tile['left'],tile['top']
 source=cv2.imread(str(p/f'{name}-input.png'))
 result=json.loads((p/f"{tile.get('resultPrefix',name)}.result.json").read_text())['image']
 raw=cv2.imread(result); candidate=cv2.resize(raw,(w,h),interpolation=cv2.INTER_CUBIC)
 sift=cv2.SIFT_create(nfeatures=8000)
 a,ad=sift.detectAndCompute(cv2.cvtColor(candidate,cv2.COLOR_BGR2GRAY),None)
 b,bd=sift.detectAndCompute(cv2.cvtColor(source,cv2.COLOR_BGR2GRAY),None)
 matches=[pair[0] for pair in cv2.BFMatcher().knnMatch(ad,bd,k=2) if len(pair)==2 and pair[0].distance<.82*pair[1].distance]
 aa=np.float32([a[v.queryIdx].pt for v in matches]);bb=np.float32([b[v.trainIdx].pt for v in matches])
 # Same locked canvas: distant repeated windows are not correspondences.
 nearby=np.linalg.norm(aa-bb,axis=1)<8
 if tile.get('identityReview'):
  # Explicitly reviewed unchanged canvas; do not fit an unreliable transform.
  shift=np.zeros(2,np.float32);mask=nearby
 else:
  assert nearby.sum()>=8,(name,'insufficient local evidence',int(nearby.sum()))
  shift=np.median(bb[nearby]-aa[nearby],axis=0)
  mask=nearby&(np.linalg.norm(bb-aa-shift,axis=1)<3)
  assert mask.sum()>=8,(name,'insufficient translation consensus',int(mask.sum()))
  shift=np.median(bb[mask]-aa[mask],axis=0)
 limit=tile.get('reviewedTranslationLimitPx',4)
 assert np.linalg.norm(shift)<limit,(name,'geometry drift requires review',shift)
 assert limit==4 or tile.get('translationReview'),(name,'missing bounded correction review')
 affine=np.array([[1,0,shift[0]],[0,1,shift[1]]],dtype=np.float32)
 drift=np.linalg.norm(aa[mask]-bb[mask],axis=1);residual=np.linalg.norm(aa[mask]+shift-bb[mask],axis=1)
 candidate=cv2.warpAffine(candidate,affine,(w,h),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
 wx=np.ones(w,np.float32);wy=np.ones(h,np.float32)
 # Use half of each actual neighbouring overlap as the feather width.
 for other in m['tiles']:
  if other is tile:continue
  ox,oy,ow,oh=other['left'],other['top'],other['width'],other['height']
  if oy==y:
   if ox<x and ox+ow>x:
    n=min(w,(ox+ow-x)//2);wx[:n]*=np.linspace(.001,1,n)
   if ox>x and ox<x+w:
    n=min(w,(x+w-ox)//2);wx[-n:]*=np.linspace(1,.001,n)
  if ox==x:
   if oy<y and oy+oh>y:
    n=min(h,(oy+oh-y)//2);wy[:n]*=np.linspace(.001,1,n)
   if oy>y and oy<y+h:
    n=min(h,(y+h-oy)//2);wy[-n:]*=np.linspace(1,.001,n)
 weight=wy[:,None]*wx[None,:]
 total[y:y+h,x:x+w]+=candidate*weight[:,:,None];weights[y:y+h,x:x+w]+=weight
 receipts.append(dict(name=name,rawSize=[raw.shape[1],raw.shape[0]],nativeSize=[w,h],matches=len(matches),inliers=int(mask.sum()),rawMedianPx=float(np.median(drift)) if len(drift) else None,rawMaxPx=float(drift.max()) if len(drift) else None,registeredMedianPx=float(np.median(residual)) if len(residual) else None,candidateToSourceAffine=affine.tolist(),translationReview=tile.get('translationReview'),identityReview=tile.get('identityReview')))
assert weights.min()>0
output=np.uint8(np.clip(total/weights[:,:,None],0,255))
cv2.imwrite(str(p/f'v4-plate-{format}.png'),output)
cv2.imwrite(str(p/f'v4-plate-{format}-review.jpg'),cv2.resize(output,(min(W,1600),round(H*min(W,1600)/W))))
(p/f'v4-plate-{format}-checks.json').write_text(json.dumps(dict(canvas=[W,H],tiles=receipts,limitation='Sparse feature registration and visual review, not full per-pixel structural equivalence.'),indent=2)+'\n')
print(json.dumps(receipts,indent=2))
