from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
P=Path(__file__).resolve().parent
bg=Image.open(P.parents[1]/'fleet-road-v11-2026-10-07/backdrop-v11.png').convert('RGBA')
records=[]
for f in (129,134,150,154,158,184):
 if not (P/'before'/f'{f:04}.png').exists() or not (P/'after'/f'{f:04}.png').exists():continue
 a=Image.open(P/'before'/f'{f:04}.png').convert('RGBA');b=Image.open(P/'after'/f'{f:04}.png').convert('RGBA')
 before=Image.alpha_composite(bg,a);after=Image.alpha_composite(bg,b)
 before.save(P/f'before-map-{f:04}.png');after.save(P/f'after-map-{f:04}.png')
 delta=np.asarray(a)[:,:,3].astype(int)-np.asarray(b)[:,:,3].astype(int);ys,xs=np.where(delta>32)
 rec={'frame':f,'pixels_alpha_reduced_gt32':len(xs)}
 if len(xs):
  box=(max(0,int(xs.min())-40),max(0,int(ys.min())-40),min(bg.width,int(xs.max())+40),min(bg.height,int(ys.max())+40));rec['bounds']=box
  pair=Image.new('RGB',((box[2]-box[0])*2,box[3]-box[1]));pair.paste(before.crop(box),(0,0));pair.paste(after.crop(box),(box[2]-box[0],0));pair.save(P/f'comparison-{f:04}.png')
 records.append(rec)
(P/'pilot-validation.json').write_text(json.dumps(records,indent=2));print(records)
