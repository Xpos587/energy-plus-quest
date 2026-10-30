"""Compose scene-wide recipient edits without reusing cutout character sprites.
Usage: python compose.py WORKDIR. Requires Pillow, numpy, OpenCV.
Register the generated destination crop to the unchanged source background, then
feather its perimeter. Vehicles and port stay byte-identical across recipients.
"""
import json, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

root = Path(sys.argv[1])
report = {}
sift = cv2.SIFT_create(nfeatures=6000)
for fmt, box in [('wide',(1100,0,1720,600)), ('tall',(340,230,948,830))]:
    base = Image.open(root / f'base-{fmt}.png').convert('RGB')
    base.save(root / f'final-{fmt}-arseniy.png')
    target = np.asarray(base.crop(box))
    h,w = target.shape[:2]
    kp0,d0 = sift.detectAndCompute(cv2.cvtColor(target,cv2.COLOR_RGB2GRAY),None)
    for who in ['alva','khor']:
        variant = 'tall-c' if fmt == 'tall' else fmt
        path = root / f'destination-{variant}-{who}.png'
        if not path.exists(): continue
        patch = np.asarray(Image.open(path).convert('RGB').resize((w,h),Image.Resampling.LANCZOS))
        kp1,d1 = sift.detectAndCompute(cv2.cvtColor(patch,cv2.COLOR_RGB2GRAY),None)
        matches = [m for m,n in cv2.BFMatcher().knnMatch(d1,d0,k=2) if m.distance < .7*n.distance]
        assert len(matches)>20, (fmt,who,'insufficient unchanged background')
        a = np.float32([kp1[m.queryIdx].pt for m in matches])
        b = np.float32([kp0[m.trainIdx].pt for m in matches])
        matrix,inliers = cv2.findHomography(a,b,cv2.RANSAC,3)
        assert inliers.sum()>20, (fmt,who,'registration failed')
        aligned = cv2.warpPerspective(patch,matrix,(w,h))
        mask = cv2.warpPerspective(np.full((h,w),255,np.uint8),matrix,(w,h))
        mask[[0,-1],:] = 0; mask[:,[0,-1]] = 0
        alpha = np.clip(cv2.distanceTransform(mask,cv2.DIST_L2,5)/24,0,1)[:,:,None]
        merged = np.round(aligned*alpha+target*(1-alpha)).astype(np.uint8)
        final = base.copy(); final.paste(Image.fromarray(merged),box[:2])
        final.save(root / f'final-{fmt}-{who}.png')
        report[f'{fmt}-{who}'] = {'matches':len(matches),'inliers':int(inliers.sum()),'transform':matrix.tolist()}
        # No edits may reach the transport staging / barge area below this crop.
        assert np.array_equal(np.asarray(final)[box[3]:],np.asarray(base)[box[3]:])
(root / 'composition.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
