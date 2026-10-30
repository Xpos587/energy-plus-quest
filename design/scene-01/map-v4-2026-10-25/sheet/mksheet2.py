"""Generic sheet: mksheet2.py plate rid name h1,h2,.. [parts]  parts default cab,trailer; 'express' uses part ''."""
import sys, json
from PIL import Image
import numpy as np
plate,rid,name=sys.argv[1],sys.argv[2],sys.argv[3]; H=[int(v) for v in sys.argv[4].split(',')]
parts=sys.argv[5].split(',') if len(sys.argv)>5 else ['cab','trailer']
S='../out-style/sprites/'
fn=lambda part,h: f'{S}{plate}-{rid}{"-"+part if part else ""}-{h:02d}.png'
bg=(150,156,166,255); pad=24
blocks=[]
for part in parts:
  ims=[Image.open(fn(part,h)).convert('RGBA') for h in H]
  a=np.zeros((360,360),bool)
  for im in ims: a|=np.asarray(im)[...,3]>8
  ys,xs=np.nonzero(a); b=tuple(int(v) for v in (xs.min()-8,ys.min()-8,xs.max()+9,ys.max()+9))
  w,h=b[2]-b[0],b[3]-b[1]
  cols=8 if w*8+pad*9<=1500 else 4
  blocks.append((part,ims,b,w,h,cols))
W=max(c*(w+pad) for *_,w,h,c in blocks)+pad
Hh=pad+sum(((len(H)+c-1)//c)*(h+pad) for *_,w,h,c in blocks)
sheet=Image.new('RGBA',(W,Hh),bg); cells=[]; y0=pad; boxes={}
for part,ims,b,w,h,cols in blocks:
  boxes[part]=b
  for i,im in enumerate(ims):
    x=pad+(i%cols)*(w+pad); y=y0+(i//cols)*(h+pad)
    sheet.alpha_composite(im.crop(b),(x,y)); cells.append([part,H[i],x,y])
  y0+=((len(H)+cols-1)//cols)*(h+pad)
sheet.convert('RGB').save(f'{name}.png')
json.dump({'plate':plate,'rid':rid,'boxes':boxes,'cells':cells,'size':list(sheet.size)},open(f'{name}.json','w'))
print(name,sheet.size)
