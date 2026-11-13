import json, math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
import sys
R=Path(__file__).resolve().parents[2];P=R/'design/scene-04/blender-v4/painted';F=P/'face-inputs'
W=Path(sys.argv[1]) if len(sys.argv)>1 else R/'.tmp-work/scene4-faces-rebuild'
for directory in ['inputs','candidates','reviews']:(W/directory).mkdir(parents=True,exist_ok=True)
g=json.loads((F/'geometry.json').read_text());rows=[]
for f,geo in g['craneLayers'].items():
 old=Image.open(F/f'{f}/top.webp').convert('RGBA');new=Image.open(W/f'candidates/{f}-top.webp').convert('RGBA')
 a,b=np.array(old),np.array(new);assert old.size==new.size;assert np.array_equal(a[:,:,3],b[:,:,3])
 cw,ch=old.width//4,old.height//4;top=geo['top'];S=4
 sheet=Image.new('RGB',(3600,1800),'#ddd');d=ImageDraw.Draw(sheet)
 for n,deg in enumerate(g['craneWorld']['slews']):
  c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg))
  def pos(x,y,z):
   v=[14+x*c-y*s,7.25+x*s+y*c,11.05+z,1]
   return tuple((sum(k*l for k,l in zip(row,v))-top[key])*S for row,key in zip(geo['affine'],('x','y')))
  hull=cv2.convexHull(np.array([pos(x,y,z) for x in (-5.2,1.6) for y in (-2.2,2.2) for z in (.7,4.6)],np.float32)).reshape(-1,2)
  mask=Image.new('L',(round(top['w']*S),round(top['h']*S)));ImageDraw.Draw(mask).polygon([tuple(p) for p in hull],fill=255)
  counter=cv2.convexHull(np.array([pos(x,y,z) for x in (-6.4,-5.2) for y in (-1.9,1.9) for z in (.9,3.6)],np.float32)).reshape(-1,2)
  ImageDraw.Draw(mask).polygon([tuple(p) for p in counter],fill=255)
  mask=Image.fromarray(cv2.dilate(np.array(mask),np.ones((13,13),np.uint8)));mask=np.array(mask.resize((cw,ch),Image.Resampling.NEAREST))>0
  box=(n%4*cw,n//4*ch,(n%4+1)*cw,(n//4+1)*ch);aa=np.array(old.crop(box));bb=np.array(new.crop(box));diff=np.any(aa!=bb,axis=2)
  assert not np.any(diff&~mask),f'{f} {n} edits outside housing'
  ys,xs=np.where(mask);crop=(int(xs.min())-15,int(ys.min())-25,int(xs.max())+16,int(ys.max())+20)
  x=n%4*900;y=n//4*450;d.text((x+5,y+5),f'{f} {n:02} BEFORE / AFTER native 2x',fill='black')
  for j,im in enumerate((old,new)):
   cr=im.crop(box).crop(crop);assert cr.width<=440 and cr.height<=415, (f,n,cr.size)
   sheet.paste(cr,(x+5+j*450,y+25),cr)
  rows.append({'format':f,'frame':n,'changedPixels':int(diff.sum()),'outsideHousingChanged':0,'alphaChanged':0})
 sheet.save(W/f'reviews/{f}-machinery.png')
 # Full latest office bodies and surroundings, native target density, no new head-only crops.
 names=['office','ivan-joy','ivan-wave','ivan-cheer'];ims=[Image.open(W/f'candidates/{f}-{name}.webp').convert('RGBA') for name in names]
 sh=Image.new('RGB',(sum(im.width for im in ims)+50,max(im.height for im in ims)+40),'#ddd');dr=ImageDraw.Draw(sh);x=0
 for name,im in zip(names,ims):sh.paste(im,(x,30),im);dr.text((x+5,5),f'{f}/{name}',fill='black');x+=im.width+10
 sh.save(W/f'reviews/{f}-office-full.png')
(W/'reviews/machinery-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS: 64 casing frames exact dimensions/alpha; all RGB edits inside projected machinery housing')
