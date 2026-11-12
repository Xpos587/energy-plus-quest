"""Recover original asset sizes/alpha; align only painted RGB to the source matte."""
import cv2,json,sys
import numpy as np
from pathlib import Path
def load(path):
 image=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
 assert image is not None,path
 return cv2.cvtColor(image,cv2.COLOR_BGR2BGRA) if image.shape[2]==3 else image
p=Path('.tmp-work/scene4-final-render/gpt');kind,format=sys.argv[1:3]
src=p.parent/'blender-assets'/format;out=p.parent/'painted-assets'/format;out.mkdir(parents=True,exist_ok=True)
receipts=[]
def extract(raw,rect,original,label):
 x,y,w,h=[rect[k] for k in ['left','top','width','height']]
 rgba=raw[y:y+h,x:x+w].copy()
 target=original;assert target.shape==rgba.shape
 sourceMask=target[:,:,3].astype(np.float32)/255;paintMask=rgba[:,:,3].astype(np.float32)/255
 M=np.eye(2,3,dtype=np.float32);score=None;method='identity'
 if paintMask.min()<.1:
  try:
   score,M=cv2.findTransformECC(sourceMask,paintMask,M,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,150,1e-6),None,5)
   assert abs(M[0,0]-1)<.05 and abs(M[1,1]-1)<.05 and abs(M[0,1])<.03 and abs(M[1,0])<.03 and abs(M[:,2]).max()<max(w,h)*.04,(label,M)
   method='alpha-ECC affine; RGB only'
  except cv2.error:
   M=np.eye(2,3,dtype=np.float32);method='identity; ECC unavailable'
  invalid=(rgba[:,:,3]<8).astype(np.uint8)
  distances,labels=cv2.distanceTransformWithLabels(invalid,cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
  colors=rgba[:,:,:3][invalid==0]
  assert len(colors)>0
  filled=colors[np.maximum(labels-1,0)]
  rgb=np.where(invalid[:,:,None]>0,filled,rgba[:,:,:3])
 else:rgb=rgba[:,:,:3]
 rgb=cv2.warpAffine(rgb,M,(w,h),flags=cv2.INTER_CUBIC|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REFLECT_101)
 rgb[target[:,:,3]==0]=0
 result=np.dstack((rgb,target[:,:,3]));assert np.array_equal(result[:,:,3],target[:,:,3])
 receipts.append(dict(name=label,width=w,height=h,alignment=method,ecc=score,sourceToCandidate=M.tolist(),alphaChangedPixels=0))
 return result
if kind=='sprites':
 name=f'v4-sprites-{format}';manifest=json.loads((p/f'{name}.json').read_text());result=json.loads((p/f'{name}.result.json').read_text())['image'];raw=cv2.resize(load(result),(manifest['width'],manifest['height']),interpolation=cv2.INTER_CUBIC)
 for rect in manifest['sprites']:
  image=extract(raw,rect,load(src/f"{rect['name']}.webp"),rect['name']);cv2.imwrite(str(out/f"{rect['name']}.png"),image)
else:
 assert kind=='top'
 original=load(src/'top.webp');fh,fw=original.shape[0]//4,original.shape[1]//4;atlas=np.zeros_like(original)
 for group in range(4):
  name=f'v4-top-{format}-{group}';manifest=json.loads((p/f'{name}.json').read_text());result=json.loads((p/f'{name}.result.json').read_text())['image'];raw=cv2.resize(load(result),(manifest['width'],manifest['height']),interpolation=cv2.INTER_CUBIC)
  for rect in manifest['frames']:
   f=rect['frame'];x,y=(f%4)*fw,(f//4)*fh;image=extract(raw,rect,original[y:y+fh,x:x+fw],f'top-{f}');atlas[y:y+fh,x:x+fw]=image
 assert np.array_equal(atlas[:,:,3],original[:,:,3]);cv2.imwrite(str(out/'top.png'),atlas)
(p/f'v4-{kind}-{format}-checks.json').write_text(json.dumps(receipts,indent=2)+'\n');print(json.dumps(receipts,indent=2))
