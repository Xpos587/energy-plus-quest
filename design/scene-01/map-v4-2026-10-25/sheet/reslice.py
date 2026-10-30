"""Map a codex-repainted sheet back onto the original sprite frames.
usage: reslice.py NAME  (NAME.json + g-NAME.png -> re/{plate}-{rid}-{part}-{hh}.png)"""
import sys, json, os
from PIL import Image
import numpy as np
from scipy import ndimage
name=sys.argv[1]
J=json.load(open(f'{name}.json')); W,H=J['size']; plate=J.get('plate','wide'); rid=J.get('rid','near')
gp=os.path.join(os.path.dirname(name),'g-'+os.path.basename(name)+'.png'); g=Image.open(gp).convert('RGB'); sx=g.width/W; sy=g.height/H
gs=np.asarray(g).astype(float)
bgc=np.median(np.concatenate([gs[:6].reshape(-1,3),gs[-6:].reshape(-1,3),gs[:,:6].reshape(-1,3)]),0)
fg=np.abs(gs-bgc).sum(-1)>40
fg=ndimage.binary_fill_holes(ndimage.binary_closing(ndimage.binary_opening(fg,iterations=2),iterations=3))
lab,n=ndimage.label(fg)
comps=[]
for i in range(1,n+1):
  ys,xs=np.nonzero(lab==i)
  if len(xs)<1500: continue
  comps.append(dict(cx=xs.mean()/sx,cy=ys.mean()/sy,box=(xs.min()/sx,ys.min()/sy,(xs.max()+1)/sx,(ys.max()+1)/sy)))
S='../out-style/sprites/'; os.makedirs('re',exist_ok=True)
used=set(); bad=[]
for p,h,x,y in J['cells']:
  b=J['boxes'][p]
  al=np.asarray(Image.open(f'{S}{plate}-{rid}{"-"+p if p else ""}-{h:02d}.png').convert('RGBA'))[...,3]
  ys,xs=np.nonzero(al>8)
  ob=(xs.min()-b[0]+x,ys.min()-b[1]+y,xs.max()+1-b[0]+x,ys.max()+1-b[1]+y)
  ocx=(ob[0]+ob[2])/2; ocy=(ob[1]+ob[3])/2
  k=min(range(len(comps)),key=lambda k:(comps[k]['cx']-ocx)**2+(comps[k]['cy']-ocy)**2)
  used.add(k); gb=comps[k]['box']
  gx=(round(gb[0]*sx),round(gb[1]*sy),round(gb[2]*sx),round(gb[3]*sy))
  G=g.crop(gx); Gm=Image.fromarray((fg[gx[1]:gx[3],gx[0]:gx[2]]*255).astype(np.uint8))
  tb=(xs.min(),ys.min(),xs.max()+1,ys.max()+1); tw,th=tb[2]-tb[0],tb[3]-tb[1]
  rgb=np.asarray(G.resize((tw,th),Image.LANCZOS)); Gmw=np.asarray(Gm.resize((tw,th),Image.BILINEAR))>127
  om=al[tb[1]:tb[3],tb[0]:tb[2]]>128
  iou=(om&Gmw).sum()/max(1,(om|Gmw).sum())
  if Gmw.any():
    idx=ndimage.distance_transform_edt(~Gmw,return_distances=False,return_indices=True); rgb=rgb[idx[0],idx[1]]
  out=np.zeros((360,360,4),np.uint8); out[tb[1]:tb[3],tb[0]:tb[2],:3]=rgb; out[...,3]=al
  Image.fromarray(out,'RGBA').save(f're/{plate}-{rid}{"-"+p if p else ""}-{h:02d}.png')
  if iou<0.8: bad.append((p,h,round(iou,2)))
print(name,'cells',len(J['cells']),'comps',len(comps),'low IoU',bad)
