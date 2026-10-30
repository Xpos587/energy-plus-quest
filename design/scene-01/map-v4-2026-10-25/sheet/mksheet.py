import sys, json
from PIL import Image
import numpy as np
plate,rid,name=sys.argv[1],sys.argv[2],sys.argv[3]; H=[int(v) for v in sys.argv[4].split(',')]
S='../out-style/sprites/'
meta={}; rows=[]
for part in ['cab','trailer']:
  ims=[Image.open(f'{S}{plate}-{rid}-{part}-{h:02d}.png').convert('RGBA') for h in H]
  a=np.zeros((360,360),bool)
  for im in ims: a|=np.asarray(im)[...,3]>8
  ys,xs=np.nonzero(a); b=tuple(int(v) for v in (xs.min()-8,ys.min()-8,xs.max()+9,ys.max()+9))
  meta[part]=b; rows.append((part,ims,b))
bg=(150,156,166,255)
cab_w,cab_h=rows[0][2][2]-rows[0][2][0],rows[0][2][3]-rows[0][2][1]
tr_w,tr_h=rows[1][2][2]-rows[1][2][0],rows[1][2][3]-rows[1][2][1]
pad=24
W=max(8*(cab_w+pad),4*(tr_w+pad))+pad; Hh=pad+cab_h+pad+2*(tr_h+pad)
sheet=Image.new('RGBA',(W,Hh),bg); cells=[]
for i,im in enumerate(rows[0][1]):
  x=pad+i*(cab_w+pad); y=pad; sheet.alpha_composite(im.crop(rows[0][2]),(x,y)); cells.append(['cab',H[i],x,y])
for i,im in enumerate(rows[1][1]):
  x=pad+(i%4)*(tr_w+pad); y=pad+cab_h+pad+(i//4)*(tr_h+pad); sheet.alpha_composite(im.crop(rows[1][2]),(x,y)); cells.append(['trailer',H[i],x,y])
sheet.convert('RGB').save(f'{name}.png')
json.dump({'plate':plate,'rid':rid,'boxes':meta,'cells':cells,'size':list(sheet.size)},open(f'{name}.json','w'))
print(sheet.size)
