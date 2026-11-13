import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
import sys
R=Path(__file__).resolve().parents[2];P=R/'design/scene-04/blender-v4/painted';F=P/'face-inputs'
W=Path(sys.argv[1]) if len(sys.argv)>1 else R/'.tmp-work/scene4-faces-rebuild'
for directory in ['inputs','candidates','reviews']:(W/directory).mkdir(parents=True,exist_ok=True)
# Old head rectangle, new neck centre, cap top, neck bottom: native source coordinates.
layout=json.loads((F/'office-head-layouts.json').read_text())
master=Image.open(P/'model-images/expressions-a1.png').convert('RGBA');heads={}
for name,box in {'focus':(0,0,768,512),'wave':(768,0,1536,512),'cheer':(0,512,768,1024)}.items():
 im=master.crop(box);bb=im.getchannel('A').point(lambda a:255 if a>128 else 0).getbbox();im=im.crop(bb);a=np.array(im);a[:,:,3]=np.minimum(255,a[:,:,3].astype(float)*255/254).round().astype('uint8');heads[name]=Image.fromarray(a)
S=2;receipts=[]
for f,items in layout.items():
 sheet=Image.new('RGB',(1280,560),'#ddd');d=ImageDraw.Draw(sheet)
 for j,(name,(old,nx,top,bottom)) in enumerate(items.items()):
  original=Image.open(F/f'{f}/{name}.webp').convert('RGBA');base=original.resize((original.width*S,original.height*S),Image.Resampling.LANCZOS);a=np.array(base)
  mask=Image.new('L',base.size);md=ImageDraw.Draw(mask);x0,y0,x1,y1=[v*S for v in old];h=y1-y0;w=x1-x0
  md.ellipse((x0,y0,x1,y0+h*.84),fill=255)
  md.polygon([(x0+w*.27,y0+h*.5),(x1-w*.04,y0+h*.5),(x1-w*.12,y1),(x0+w*.4,y1)],fill=255)
  m=cv2.dilate(np.array(mask),np.ones((5,5),np.uint8))
  a[:,:,:3]=cv2.inpaint(a[:,:,:3],m,5,cv2.INPAINT_TELEA)
  im=Image.fromarray(a);head=heads['focus' if name=='office' else 'cheer' if name=='ivan-cheer' else 'wave']
  hh=round((bottom-top)*S);ww=round(hh*head.width/head.height);head=head.resize((ww,hh),Image.Resampling.LANCZOS)
  # Match the short neck to the unchanged collar, rather than guessing the head centre.
  px=round(nx*S-ww*.53);py=top*S
  im.alpha_composite(head,(px,py));out=np.array(im);reference=np.array(base)
  # Keep the existing shirt collar in front of the short replacement neck.
  yy,xx=np.indices(reference.shape[:2]);rgb=reference[:,:,:3].astype(float)
  collar=(yy>py+hh*.84)&(yy<py+hh+3)&(xx>px)&(xx<px+ww)&(rgb[:,:,2]>rgb[:,:,0]*1.12)&(rgb[:,:,2]>rgb[:,:,1]*1.02)
  out[collar]=reference[collar]
  out[:,:,3]=reference[:,:,3];im=Image.fromarray(out)
  allowed=m>0;hp=np.array(head)[:,:,3]>0;allowed[py:py+hh,px:px+ww]|=hp
  delta=np.any(out!=np.array(base),axis=2);assert not np.any(delta&~allowed)
  assert np.array_equal(out[:,:,3],np.array(base)[:,:,3])
  dest=W/f'candidates/{f}-{name}.webp';im.save(dest,lossless=True,exact=True)
  assert np.array_equal(np.array(Image.open(dest).convert('RGBA')),out)
  region=(min(old[0]-8,px/S-8),old[1]-8,max(old[2]+8,(px+ww)/S+8),bottom+25);region=tuple(round(v) for v in region)
  for k,src in enumerate((base,im)):
   cr=src.crop(tuple(v*S for v in region));bg=Image.new('RGBA',cr.size,'#ccc');bg.alpha_composite(cr);sheet.paste(bg.convert('RGB'),(j*320+10,35+k*260));d.text((j*320+8,10+k*260),f'{f}/{name} '+('BEFORE resampled 2x' if k==0 else 'AFTER new head native'),fill='black')
  receipts.append({'format':f,'name':name,'sourceSize':list(original.size),'size':list(im.size),'scale':S,'oldHead':old,'newHead':[px,py,ww,hh],'changedPixels':int(delta.sum()),'outsideHeadChanged':0,'alphaChanged':0})
 sheet.save(W/f'reviews/{f}-office-heads.png')
(W/'inputs/office-head-layouts.json').write_text(json.dumps(layout,indent=2)+'\n')
(W/'reviews/office-head-checks.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('PASS: 16 candidates, exact resampled alpha and unchanged pixels outside local head masks')
