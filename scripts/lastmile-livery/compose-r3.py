"""Compose R3 map candidates from ORIGINAL maps and approved local donor crops.
Prerequisites and the final glass pass: design/scene-05/LIVERY-ROLLOUT.md.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, json, cv2, sys
from geometry import S


def main(workspace, donor_workspace, originals):
    R = Path(workspace)
    R2 = Path(donor_workspace)
    B = Path(originals)
    checks=[]
    for fmt,s in S.items():
     orig=Image.open(B/f'scene-art/lastmile-family-v1/revision-18/choice-{fmt}-alva.webp').convert('RGB');r2=Image.open(R2/f'candidates/choice-{fmt}.webp').convert('RGB')
     assert orig.size==r2.size
     k=orig.width/s['width'];out=orig.copy();allowed=np.zeros((orig.height,orig.width),bool)
     def rect(b):return tuple(round(v*k) for v in b)
     def poly(p,feather=0):
      m=Image.new('L',orig.size);ImageDraw.Draw(m).polygon([(round(x*k),round(y*k)) for x,y in p],fill=255)
      return m.filter(ImageFilter.GaussianBlur(feather*k)) if feather else m
     # Register the tent-only cleanup crop, then use it solely under the original tents.
     cropbox=(2400,1050,3800,2100) if fmt=='wide' else (1450,600,2850,1650)
     clean=Image.open(R/f'candidates/dorm-clean-{fmt}.png').convert('RGB')
     reference=orig.crop(cropbox);scale=1000/reference.width;cs=1000/clean.width
     ref=np.array(reference.resize((1000,round(reference.height*scale))));small=np.array(clean.resize((1000,round(clean.height*cs))))
     sift=cv2.SIFT_create();p1,d1=sift.detectAndCompute(cv2.cvtColor(small,cv2.COLOR_RGB2GRAY),None);p2,d2=sift.detectAndCompute(cv2.cvtColor(ref,cv2.COLOR_RGB2GRAY),None)
     pairs=cv2.BFMatcher().knnMatch(d1,d2,k=2);good=[m for m,n in pairs if m.distance<.7*n.distance]
     H,inliers=cv2.findHomography(np.float32([p1[m.queryIdx].pt for m in good]),np.float32([p2[m.trainIdx].pt for m in good]),cv2.RANSAC,2)
     assert H is not None and inliers.sum()>30,(fmt,'cleanup registration')
     H=np.diag([1/scale,1/scale,1])@H@np.diag([cs,cs,1])
     aligned=Image.fromarray(cv2.warpPerspective(np.array(clean),H,reference.size));plate=orig.copy();plate.paste(aligned,cropbox[:2])
     for i,points in enumerate(s['patches']):
      mask=poly(points,1 if i==3 or (fmt=='tall' and i==1) else 3.5);donor=plate if i==3 else r2
      if i==(2 if fmt=='wide' else 1):
       # The R2 rig patch overlaps its raised roof; neither roof fragment belongs in this transfer.
       m=np.array(mask);rows=np.arange(orig.height)[:,None]/k
       if fmt=='tall':m[np.broadcast_to(rows>=220,m.shape)]=0
       else:
        for image in (r2,orig):
         v=np.array(image).astype('int16');m[(rows>350)&(v[:,:,2]>v[:,:,0]+20)&(v[:,:,1]>v[:,:,0]+10)]=0
       mask=Image.fromarray(m)
      out.paste(donor,(0,0),mask);allowed|=np.array(mask)>0
     print(fmt,'cleanup registration inliers',int(inliers.sum()))
     # Original deer are retained, including the mobile-frame placement.
     box=rect(s['deer']);out.paste(orig.crop(box),box)
     # Keep original building geometry; normalize only its yellow/orange trim.
     arr=np.array(out);h=np.array(poly(s['house']))>0;r,g,b=arr[:,:,0].astype(int),arr[:,:,1].astype(int),arr[:,:,2].astype(int)
     trim=h&(r>180)&(g>100)&(g<235)&(b<90)&(r-g>10)
     arr[trim,1]=np.minimum(arr[trim,1],120);arr[trim,2]=np.minimum(arr[trim,2],25);allowed|=trim
     out=Image.fromarray(arr)
     if fmt=='wide':
      local=Image.open(R/'candidates/choice-wide-livery.webp').convert('RGB');roi=(780,1690,870,1805);out.paste(local.crop(roi),roi);allowed[1690:1805,780:870]=True
     a=np.array(out);o=np.array(orig);different=np.any(a!=o,axis=2)
     assert not different[~allowed].any(),'nonlocal change'
     for name,box in s['protected'].items():
      assert np.array_equal(np.array(out.crop(rect(box))),np.array(orig.crop(rect(box)))),(fmt,name,'changed')
     # Lossless review candidate also preserves the unchanged decoded pixels after encoding.
     dest=R/f'candidates/choice-{fmt}.webp';out.save(dest,lossless=True,method=4)
     assert np.array_equal(np.array(Image.open(dest).convert('RGB')),a)
     checks.append({'format':fmt,'dimensions':orig.size,'original_pixels_unchanged_percent':round(float((~different).mean()*100),3),'outside_local_masks_identical':True,'protected_original_regions':s['protected']})
     out.thumbnail((s['width'],1400));out.save(R/f'sheets/map-{fmt}.jpg',quality=95)
     print(fmt,checks[-1])
    (R/'placement-check.json').write_text(json.dumps(checks,indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('usage: compose-r3.py R3_WORKSPACE R2_WORKSPACE ORIGINAL_MEDIA_ROOT')
    main(*sys.argv[1:])
