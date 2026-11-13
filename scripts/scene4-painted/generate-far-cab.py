import json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFilter
import sys
R=Path(__file__).resolve().parents[2];P=R/'design/scene-04/blender-v4/painted';F=P/'face-inputs'
W=Path(sys.argv[1]) if len(sys.argv)>1 else R/'.tmp-work/scene4-faces-rebuild'
for directory in ['inputs','candidates','reviews']:(W/directory).mkdir(parents=True,exist_ok=True)
rows=json.loads((F/'far-empty-layout.json').read_text());sheet=Image.open(P/'model-images/far-empty-a1.png').convert('RGBA')
proof=Image.new('RGB',(1000,540),'#ddd');receipt=[]
regions={'wide':[0,120,111,431],'desk':[0,120,204,430],'mid':[0,120,199,430],'tall':[0,120,241,405]}
for i,row in enumerate(rows):
 fmt=row['format'];base=Image.open(F/f'{fmt}/far.webp').convert('RGBA');a=np.array(base);rgb=a[:,:,:3].astype(float)
 hsv=cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2HSV);x0,y0,x1,y1=regions[fmt]
 region=np.zeros(a.shape[:2],bool);region[y0:y1,x0:x1]=True
 cx,cy,cx1,cy1=row['crop'];region[cy:,cx:]=False
 casing=region&(hsv[:,:,1]<110)&(rgb[:,:,0]>135)&(rgb[:,:,1]>120)&(rgb[:,:,0]>rgb[:,:,2]-8)
 if fmt=='tall':
  # The exposed counterweight top is warmer than the pale machinery panels.
  counter=np.zeros(a.shape[:2],bool);counter[174:219,54:108]=True
  casing|=counter&(hsv[:,:,1]<170)&(rgb[:,:,0]>160)&(rgb[:,:,1]>130)&(rgb[:,:,0]>rgb[:,:,2]+9)
 shade=rgb.mean(axis=2)/220
 a[casing,:3]=np.clip(shade[casing,None]*np.array([60,87,119]),0,255).round().astype('uint8')
 clean=Image.fromarray(a);clean.save(W/f'candidates/{fmt}-far.webp',lossless=True,exact=True)
 x,y,w,h=row['tile'];patch=sheet.crop((x,y,x+w,y+h)).resize((cx1-cx,cy1-cy),Image.Resampling.LANCZOS)
 full=Image.new('RGBA',base.size);full.paste(patch,(cx,cy))
 mask=Image.new('L',base.size);ImageDraw.Draw(mask).polygon(row['window'],fill=255)
 # One pixel feather, inside the opening, to retain the original orange frame.
 m=np.array(mask);m=cv2.erode(m,np.ones((3,3),np.uint8));mask=Image.fromarray(m).filter(ImageFilter.GaussianBlur(.5))
 empty=Image.composite(full,clean,mask);empty.putalpha(base.getchannel('A'))
 empty.save(W/f'candidates/{fmt}-far-empty.webp',lossless=True,exact=True)
 # Transparent geometry is byte-exact; the only changed RGB lies in local glazing/casing masks.
 assert np.array_equal(np.array(empty)[:,:,3],np.array(base)[:,:,3])
 changed=np.any(np.array(empty)[:,:,:3]!=np.array(base)[:,:,:3],axis=2)
 allowed=(np.array(mask)>0)|casing
 assert not np.any(changed&~allowed)
 receipt.append({'format':fmt,'size':base.size,'changedPixels':int(changed.sum()),'alphaExact':True,'outsideMasksExact':True})
 ImageDraw.Draw(proof).text((i*250+5,5),fmt+' BEFORE / AFTER',fill='black')
 crop=base.crop(row['crop']);proof.paste(crop,(i*250,25),crop)
 crop=empty.crop(row['crop']);proof.paste(crop,(i*250,280),crop)
proof.save(W/'reviews/far-empty-native-proof.png')
(W/'reviews/far-source-validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt)
