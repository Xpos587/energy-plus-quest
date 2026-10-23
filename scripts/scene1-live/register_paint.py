"""Register four painted views to their exact Blender camera guides.
Usage: COMFY_PYTHON register_paint.py FAMILY SHEET.png GUIDES_DIR OUTPUT_DIR
"""
import sys
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

family, sheet_path, guide_dir, out_dir = sys.argv[1:]
guide_dir, out = Path(guide_dir), Path(out_dir)
out.mkdir(parents=True,exist_ok=True)
sheet = Image.open(sheet_path).convert('RGB')
cell = sheet.width//2
metrics = []
for index in range(4):
    guide = Image.open(guide_dir/f'{family}-guide-{index}.png').convert('RGBA')
    paint = sheet.crop(((index%2)*cell,(index//2)*cell,(index%2+1)*cell,(index//2+1)*cell)).resize(guide.size,Image.Resampling.LANCZOS)
    a, b = np.array(guide), np.array(paint)
    target = (a[:,:,3]>100).astype('uint8')*255
    mask = (b.min(axis=2)<210).astype('uint8')*255
    mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    correlation, transform = cv2.findTransformECC(target,mask,np.eye(2,3,dtype=np.float32),cv2.MOTION_AFFINE,
        (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,300,1e-6),inputMask=None,gaussFiltSize=7)
    assert correlation > .88, f'{family} view {index}: geometry drift {correlation}'
    b = cv2.warpAffine(b,transform,guide.size,flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderValue=(255,255,255))
    mask = cv2.warpAffine(mask,transform,guide.size,flags=cv2.INTER_NEAREST|cv2.WARP_INVERSE_MAP)
    # Edge colour dilation avoids white halos on slightly differently shaped curved panels.
    _,indices = distance_transform_edt(mask==0,return_indices=True)
    b[mask==0] = b[indices[0][mask==0],indices[1][mask==0]]
    if family == 'old-cab':
        enamel = (b[:,:,0] > 60) & (b[:,:,2] > b[:,:,0]*1.04) & (b[:,:,1] > b[:,:,0]*1.015)
        b[enamel] = np.uint8(b[enamel].astype(float)*.8)
    Image.fromarray(b).save(out/f'{family}-paint-{index}.png')
    metrics.append({'view':index,'silhouetteCorrelation':correlation,'transform':transform.tolist()})
(out/f'{family}-registration.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(metrics)
