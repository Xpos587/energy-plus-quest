# /// script
# dependencies = ["pillow", "numpy", "opencv-python-headless"]
# ///
"""Register garments onto v15, export selected A as v16, leave B as a local proposal."""
from pathlib import Path
import importlib.util
import json
import sys
import cv2
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.tmp-work/r23-warehouse-ppe'
spec=importlib.util.spec_from_file_location('v15',ROOT/'scripts/finish-warehouse-v15.py')
v15=importlib.util.module_from_spec(spec);spec.loader.exec_module(v15)
CELL=(480,720)
TOP={'wide':[52,52,53,57,62],'tall':[73,52,49,65,61]}
BOOT={'wide':[129,140,139,134,152],'tall':[140,127,123,143,145]}
HEADS={
 'wide':[(38,31,64,53),(36,30,68,54),(36,32,79,59),(52,30,78,61),(34,35,84,64)],
 'tall':[(34,55,57,74),(25,35,51,54),(51,33,75,53),(59,40,81,67),(42,39,71,63)],
}
# Original hands/tools, manually reviewed against the native-coordinate grids.
PROTECT={
 'wide': [
  [[(43,86),(51,86),(52,96),(44,96)]],
  [[(30,68),(40,68),(40,80),(30,80)],[(36,85),(46,85),(46,98),(36,98)]],
  [[(80,70),(91,70),(91,85),(80,85)]],
  [[(33,65),(62,71),(72,86),(63,90),(42,81)],[(39,72),(48,72),(48,84),(39,84)]],
  [[(27,54),(43,54),(43,68),(27,68)],[(29,86),(43,86),(43,99),(29,99)]],
 ],
 'tall': [
  [],
  [[(20,73),(28,73),(28,83),(20,83)],[(25,81),(35,81),(35,91),(25,91)]],
  [[(69,58),(78,58),(78,66),(69,66)],[(65,66),(77,66),(77,77),(65,77)]],
  [[(32,68),(44,68),(44,78),(32,78)],[(38,70),(56,73),(66,83),(65,90),(56,87),(45,81)]],
  [[(32,84),(40,84),(40,95),(32,95)]],
 ]
}

def coloured(a):
    h=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
    return (((h[:,:,0]>92)&(h[:,:,0]<137)&(h[:,:,1]>65))|((h[:,:,0]>5)&(h[:,:,0]<32)&(h[:,:,1]>155))).astype('uint8')*255

for variant in sys.argv[1:]:
    generated=Image.open(ROOT/f'design/scene-03/ppe-variants/{variant}-atlas.png').convert('RGB').resize((2400,1440),Image.Resampling.LANCZOS)
    target=Image.open(OUT/'people-target.png').convert('RGB')
    sheet=Image.new('RGB',(2400,1440),'white')
    metrics=[]
    for row,(form,boxes) in enumerate(v15.BOXES.items()):
        suffix='-tall' if form=='tall' else ''
        base=Image.open(ROOT/f'public/scene-art/inventory-master-v15{suffix}.webp').convert('RGB')
        baseline=np.asarray(base).copy()
        changed_mask=np.zeros(baseline.shape[:2],bool)
        for col,(box,parts) in enumerate(zip(boxes,v15.PARTS[form])):
            atlas=(col*480,row*720,(col+1)*480,(row+1)*720)
            ref=np.asarray(target.crop(atlas));gen=np.asarray(generated.crop(atlas))
            # Shape-only registration: do not warp the new pocket/tape design back into old stripes.
            r=cv2.GaussianBlur(coloured(ref).astype('float32')/255,(0,0),6)
            g=cv2.GaussianBlur(coloured(gen).astype('float32')/255,(0,0),6)
            warp=np.eye(2,3,dtype='float32')
            score,warp=cv2.findTransformECC(r,g,warp,cv2.MOTION_TRANSLATION,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,120,1e-6))
            assert np.max(np.abs(warp[:,2]))<40,(form,col,warp)
            gen=cv2.warpAffine(gen,warp,CELL,flags=cv2.INTER_LANCZOS4|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)
            gen=np.asarray(Image.fromarray(gen).resize((120,180),Image.Resampling.LANCZOS))
            src=np.asarray(base.crop(box)).copy()
            body=v15.mask((120,180),parts[0])>0.5
            cloth=coloured(src)
            cloth[:TOP[form][col]]=0;cloth[BOOT[form][col]:]=0
            # Close only the narrow existing reflective tape gaps; preserve skin, tools and clipboard.
            cloth=cv2.morphologyEx(cloth,cv2.MORPH_CLOSE,np.ones((5,3),np.uint8))
            # One continuous sewn garment, not holes caused by old orange/skin-like antialias colours.
            contours,_=cv2.findContours(cloth,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(cloth,contours,-1,255,cv2.FILLED)
            cloth[:TOP[form][col]]=0;cloth[BOOT[form][col]:]=0
            cloth=(cloth>0)&body
            for polygon in PROTECT[form][col]:
                cloth&=v15.mask((120,180),polygon)<0.05
            hx,hy,hr,hb=HEADS[form][col]
            cloth[hy:hb,hx:hr]=False
            result=src.copy();result[cloth]=gen[cloth]
            base.paste(Image.fromarray(result),box[:2])
            x,y,_,_=box;changed_mask[y:y+180,x:x+120]|=cloth
            metrics.append({'form':form,'person':col,'registrationCorrelation':float(score),'translationNativePx':(warp[:,2]/4).tolist(),'garmentPixels':int(cloth.sum())})
        arr=np.asarray(base)
        assert np.array_equal(arr[~changed_mask],baseline[~changed_mask])
        for box,head in zip(boxes,HEADS[form]):
            x,y,_,_=box;hx,hy,hr,hb=head
            assert np.array_equal(arr[y+hy:y+hb,x+hx:x+hr],baseline[y+hy:y+hb,x+hx:x+hr])
        base.save(OUT/f'{variant}-{form}.png')
        if variant=='a':  # Selected by the delegated reviewer; B stays a proposal only.
            runtime=ROOT/f'public/scene-art/inventory-master-v16{suffix}.webp'
            base.save(runtime,lossless=True,method=6)
            assert np.array_equal(np.asarray(Image.open(runtime).convert('RGB')),arr)
        Image.fromarray((changed_mask*255).astype('uint8')).save(OUT/f'{variant}-{form}-garment-mask.png')
        for col,box in enumerate(boxes):sheet.paste(base.crop(box).resize(CELL,Image.Resampling.LANCZOS),(col*480,row*720))
        metrics.append({'form':form,'outsideGarmentChangedPixels':int(np.any(arr!=baseline,axis=2)[~changed_mask].sum()),'changedPixels':int(np.any(arr!=baseline,axis=2).sum()),'protectedHeadChangedPixels':0,'dimensions':base.size})
    sheet.save(OUT/f'{variant}-people-composited.png')
    (OUT/f'{variant}-composite-check.json').write_text(json.dumps(metrics,indent=2))
    print(f'{variant}: original geometry/background/faces/hands protected; outside-garment pixel invariance passed')
