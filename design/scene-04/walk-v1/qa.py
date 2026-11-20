"""Exercise manifest destinations and inspect decoded WebP on the painted 2× grid (not the source renders)."""
from pathlib import Path
import json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from export_art import D,L,m,F,project
M=json.loads((D/'manifest.json').read_text());O=D/'qa';O.mkdir(exist_ok=True); font=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',14) if Path('/usr/share/fonts/TTF/DejaVuSans.ttf').exists() else ImageFont.load_default();assets_checked=set()
def load(s):
 p=D/s['src'];assets_checked.add(str(p));im=Image.open(p).convert('RGBA');w,h=round(s['w']*2),round(s['h']*2);assert im.size==(w*s.get('cols',1),h*s.get('rows',1));assert im.getbbox();return im

def frame(s,i):
 im=load(s);w,h=round(s['w']*2),round(s['h']*2);x=(i%s['cols'])*w;y=(i//s['cols'])*h;return im.crop((x,y,x+w,y+h))
def apply(base,s):
 if s:base.alpha_composite(load(s),(round(s['x']*2),round(s['y']*2)))
def label(im,txt):
 out=Image.new('RGB',(im.width,im.height+22),'#263343');out.paste(im,(0,22));ImageDraw.Draw(out).text((4,3),txt,font=font,fill='white');return out
def grid(rows):
 widths=[sum(x.width for x in r) for r in rows];out=Image.new('RGB',(max(widths),sum(max(x.height for x in r) for r in rows)),'#263343');y=0
 for row in rows:
  x=0
  for tile in row:out.paste(tile,(x,y));x+=tile.width
  y+=max(c.height for c in row)
 return out
def zoom(im,n=3):return im.resize((im.width*n,im.height*n),Image.Resampling.NEAREST)
def box(x,y,r=120,up=152,down=35):return (x-r,y-up,x+r,y+down)
def save(im,name):im.save(O/(name+'.png'),optimize=True)
summaries={};
for f in F:
 ss=M['formats'][f]['sprites']; base=Image.open(L/f/'plate.png').convert('RGBA');top=Image.open(L/f/'top-15.png').convert('RGBA');
 assert base.size==(2*m[f]['width'],2*m[f]['height']);patches=[];cycles=[];paths=[];climbs=[]; cabs=[[],[],[],[]];
 for who,tag,routekey in [('Ivan','porch','rush'),('Petr','post','petr')]:
  clean=base.copy();apply(clean,ss[tag]);pos=[round(v*2) for v in m[f]['anchors'][who.lower()]]
  bx=(pos[0]-90,pos[1]-102,pos[0]+115,pos[1]+111);patches.append([label(zoom(base.crop(bx)),f'{f} | {tag} before | 300% of 2x source'),label(zoom(clean.crop(bx)),f'{tag} after | delivered WebP')]);route=m['scene']['routes'][routekey];oc={'Ivan':'walkOccluder','Petr':'walkOccluderPetr'}[who];s=ss['walk'+who+'East'];row=[]
  # Eight distinct phases on their actual route. Keep camera and foot centred identically to see leg alternation.
  for i in range(8):
   t=.015+i*.135;p=((np.float64(route[-3])*(1-t)+np.float64(route[-2])*t));x,y=np.rint(project(f,p)[:2]).astype(int);fr=frame(s,i);bx=box(x,y,61,max(152,round(s['anchorY']*2)+10),25);view=clean.crop(bx);view.alpha_composite(fr,(x-round(s['anchorX']*2)-bx[0],y-round(s['anchorY']*2)-bx[1]));
   if ss[oc]:v=ss[oc];view.alpha_composite(load(v),(round(v['x']*2)-bx[0],round(v['y']*2)-bx[1]))
   view.alpha_composite(top.crop(bx));row.append(label(view,f'{who} phase {i}'))
  cycles.append(row)
  # Per-route before/after using the pose with the greatest actual geometry intersection.
  best=None;allw=np.zeros((base.height,base.width),np.uint8);v=ss.get(oc)
  if v:mask=load(v).getchannel('A');xm,ym=round(v['x']*2),round(v['y']*2);allw[ym:ym+mask.height,xm:xm+mask.width]=np.asarray(mask)
  for seg,(a,b) in enumerate(zip(route[:-2],route[1:-1])):
   for t in np.linspace(.02,.98,55):
    s0=ss['walk'+who+('Inland' if who=='Ivan' and seg<2 else 'East')];u,v1=np.rint(project(f,np.float64(a)*(1-t)+np.float64(b)*t)[:2]).astype(int);fr=frame(s0,1);x=u-round(s0['anchorX']*2);y=v1-round(s0['anchorY']*2);fa=np.asarray(fr)[...,3]>150;ov=allw[y:y+fr.height,x:x+fr.width];score=((ov>80)&fa).sum()/fa.sum();rank=abs(score-.52)
    if best is None or rank<best[0]:best=(rank,score,u,v1,x,y,fr)
  _,score,u,v1,x,y,fr=best;bx=box(u,v1,96,157,36);no=clean.crop(bx);no.alpha_composite(fr,(x-bx[0],y-bx[1]));yes=no.copy()
  if v:yes.alpha_composite(load(v),(xm-bx[0],ym-bx[1]));
  paths.append([label(no,f'{who} | no holdout'),label(yes,f'with holdout | {score:.0%} occluded')]);
  # Climb and seated endpoint over actual moving crane.
  row=[]
  for i,z in enumerate([1.,4.6,9.6]):
   x,y=np.rint(project(f,[60.2,3.9,z])[:2]).astype(int);bx=box(x,y,95,166,27);view=clean.crop(bx);cl=ss['climb'+who];view.alpha_composite(frame(cl,i%2),(x-bx[0]-round(cl['anchorX']*2),y-bx[1]-round(cl['anchorY']*2)));v=ss.get('climbOccluder');
   if v:view.alpha_composite(load(v),(round(v['x']*2)-bx[0],round(v['y']*2)-bx[1]));
   view.alpha_composite(top.crop(bx));row.append(label(view,f'{who} climb z={z}'))
  climbs.append(row)
  cabSheet=ss['cab'+who]
  for i,sp in enumerate(cabSheet['frameBoxes']):
   center=[sp['x']*2+sp['w'],sp['y']*2+sp['h']]
   if who=='Petr' and i!=15:continue
   u,v=map(round,center);bx=(u-94,v-95,u+94,v+90);cab=clean.crop(bx);cab.alpha_composite(Image.open(L/f/f'top-{i:02}.png').convert('RGBA').crop(bx));
   cab.alpha_composite(frame(cabSheet,i),(round(cabSheet['x']*2)-bx[0],round(cabSheet['y']*2)-bx[1]));
   if who=='Petr':climbs[-1].append(label(cab,f'{who} seated | rest'))
   else:cabs[i//4].append(label(cab,f'{who} | slew {i:02}')); 
   if who=='Ivan' and i==15:climbs[0].append(label(cab,f'{who} seated | rest'))
 save(grid(patches),f+'-patches-300pct');save(grid(cycles),f+'-walk-cycle');save(grid(paths),f+'-depth');save(grid(climbs),f+'-arrival');save(grid(cabs),f+'-cab-slew')
 # Validate ALL shipped boxes (including unpictured orientations).
 for key,s in ss.items():
  if not s:continue
  if 'src' in s:
   strip=load(s)
   if key.startswith('cab'):
    assert (s['rows'],s['cols'],s['frames'],s['restFrame'])==(4,4,list(range(16)),15)
    for i in s['frames']:assert frame(s,i).getbbox()
   elif 'cols' in s:
    assert s['frames']==list(range(s['cols'])) and s['rows']==1
    seen=set()
    for i in s['frames']:
     im=frame(s,i);seen.add(im.tobytes());solid=np.asarray(im)[...,3]>164
     cc=cv2.connectedComponentsWithStats(solid.astype('uint8'))[2][1:]
     assert cc[:,4].max()/np.count_nonzero(solid)>.965,(f,key,i,'disconnected worker')
     assert not (solid[0].any() or solid[-1].any() or solid[:,0].any() or solid[:,-1].any()),(f,key,i,'clipped')
    assert len(seen)==s['cols'],(f,key,'repeated pose')
   else:assert 0<=s['x']<m[f]['width'] and 0<=s['y']<m[f]['height']

  else:
   assert len(s['frames'])==16
   for framebox in s['frames']:
    if framebox:load(framebox)
 print(f,'checked',flush=True)
assert set(str(p) for p in (D/'assets').rglob('*.webp'))==assets_checked, 'unreferenced/missing exported files';print(len(assets_checked),'manifest textures checked,',len(F)*5,'QA sheets')
