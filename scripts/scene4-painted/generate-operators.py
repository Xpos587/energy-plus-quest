import json, math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
import sys
R=Path(__file__).resolve().parents[2];P=R/'design/scene-04/blender-v4/painted';F=P/'face-inputs'
W=Path(sys.argv[1]) if len(sys.argv)>1 else R/'.tmp-work/scene4-faces-rebuild'
for directory in ['inputs','candidates','reviews']:(W/directory).mkdir(parents=True,exist_ok=True)
g=json.loads((F/'geometry.json').read_text())
S=4
layouts={}
visibility=[]

def isolated(image):
 a=np.array(image.convert('RGBA')); white=(np.min(a[:,:,:3],axis=2)>225).astype('uint8')
 _,labels,_,_=cv2.connectedComponentsWithStats(white,8)
 border=set(np.concatenate((labels[0],labels[-1],labels[:,0],labels[:,-1])).tolist())-{0}
 a[:,:,3][np.isin(labels,list(border))]=0
 # Remove the white-matte antialias fringe, without touching interior uniform stripes.
 a[:,:,3]=cv2.GaussianBlur(cv2.erode(a[:,:,3],np.ones((11,11),np.uint8)),(3,3),0.45)
 out=Image.fromarray(a);return out.crop(out.getbbox())
master=Image.open(P/'model-images/operators-a1.png')
actors={name:isolated(master.crop((i*768,0,(i+1)*768,1024))) for i,name in enumerate(('ivan','petr'))}
for actor,im in actors.items():
 actors[actor]=im.crop((0,0,im.width,round(im.height*.65)))
 actors[actor].save(W/f'inputs/operator-{actor}.png')

for fmt,geo in g['craneLayers'].items():
 top=geo['top']; atlas=Image.open(F/f'{fmt}/top.webp').convert('RGBA'); cw,ch=atlas.width//4,atlas.height//4
 clean_atlas=atlas.copy()
 framew,frameh=round(top['w']*S),round(top['h']*S)
 def project(v):return tuple((sum(a*b for a,b in zip(row,[*v,1]))-top[k])*S for row,k in zip(geo['affine'],('x','y')))
 normal=-np.cross(geo['affine'][0][:3],geo['affine'][1][:3])
 sheets={who:Image.new('RGB',(960,1040),'#eee') for who in actors}
 all_layers={who:[] for who in actors}
 union=None
 for frame,deg in enumerate(g['craneWorld']['slews']):
  a=math.radians(deg);c,s=math.cos(a),math.sin(a)
  def world(x,y,z):return (14+x*c-y*s,7.25+x*s+y*c,11.05+z)
  def pos(x,y,z):return project(world(x,y,z))
  # Visible glazed openings, derived from the unchanged cabin in quay.py.
  windows=[]
  if np.dot((c,s,0),normal)>0:
   windows.append([pos(5.25,y,z) for y,z in [(-4.05,2.5),(-1.15,2.5),(-1.15,5.3),(-4.05,5.3)]])
  for side in (-1,1):
   if np.dot((-s*side,c*side,0),normal)>0:
    y=-4.2 if side==-1 else -1.0
    windows.append([pos(x,y,z) for x,z in [(2.3,2.5),(5.15,2.5),(5.15,5.3),(2.3,5.3)]])
  native_base=atlas.crop((frame%4*cw,frame//4*ch,frame%4*cw+cw,frame//4*ch+ch))
  # Restore navy only on the machinery housing, not the cab/geometry or its glazing.
  housing=np.array([pos(x,y,z) for x in (-5.2,1.6) for y in (-2.2,2.2) for z in (.7,4.6)],np.float32)
  hull=cv2.convexHull(housing).reshape(-1,2)
  housing_mask=Image.new('L',(framew,frameh));ImageDraw.Draw(housing_mask).polygon([tuple(p) for p in hull],fill=255)
  counter=cv2.convexHull(np.array([pos(x,y,z) for x in (-6.4,-5.2) for y in (-1.9,1.9) for z in (.9,3.6)],np.float32)).reshape(-1,2)
  ImageDraw.Draw(housing_mask).polygon([tuple(p) for p in counter],fill=255)
  # Three native pixels cover the authored paint edge beyond the projected solid.
  housing_mask=Image.fromarray(cv2.dilate(np.array(housing_mask),np.ones((13,13),np.uint8)))
  for poly in windows:ImageDraw.Draw(housing_mask).polygon(poly,fill=0)
  hm=np.array(housing_mask.resize(native_base.size,Image.Resampling.NEAREST))>0
  na=np.array(native_base);nrgb=na[:,:,:3].astype(float);nhsv=cv2.cvtColor(na[:,:,:3],cv2.COLOR_RGB2HSV)
  mix=hm*(na[:,:,3]>0)*np.clip((110-nhsv[:,:,1].astype(float))/40,0,1)*np.clip((nrgb[:,:,0]-120)/40,0,1)*np.clip((nrgb[:,:,0]-nrgb[:,:,2]+30)/20,0,1)
  shade=nrgb.mean(axis=2)/220;navy=shade[:,:,None]*np.array([60,87,119])
  na[:,:,:3]=np.clip(nrgb*(1-mix[:,:,None])+navy*mix[:,:,None],0,255).round().astype('uint8')
  native_base=Image.fromarray(na);clean_atlas.paste(native_base,(frame%4*cw,frame//4*ch))
  base=native_base.resize((framew,frameh),Image.Resampling.LANCZOS)
  mask=Image.new('L',base.size);d=ImageDraw.Draw(mask)
  for poly in windows:d.polygon(poly,fill=255)
  rgb=np.asarray(base).astype(float);r,green,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
  # Saturated orange frame paint stays in front, including its darker/beige edges.
  # Warm, low-saturation glass is not frame paint.
  hsv=cv2.cvtColor(np.asarray(base)[:,:,:3],cv2.COLOR_RGB2HSV)
  paint=((rgb[:,:,3]>128)&(hsv[:,:,0]>=4)&(hsv[:,:,0]<=25)&(hsv[:,:,1]>160)&(hsv[:,:,2]>50)).astype('uint8')
  paint=cv2.dilate(paint,np.ones((9,9),np.uint8))
  m=cv2.erode(np.array(mask),np.ones((3,3),np.uint8));m[paint>0]=0
  mask=Image.fromarray(m)
  # Ease from the side pane into the front; never jump between panes at equal area.
  pane=windows[-1]
  front=np.dot((c,s,0),normal);side=abs(np.dot((-s,c,0),normal))
  weight=np.clip((front/max(side,1e-6)-.2)/.6,0,1);weight=weight*weight*(3-2*weight)
  if fmt=='tall' and frame>=13:
   # Cross behind the post between frames, never bisect the face on the post itself.
   weight=0
  pane=np.array(pane)*(1-weight)+np.array(windows[0])*weight
  pane_height=abs(geo['affine'][1][2])*2.8*S
  center=(sum(p[0] for p in pane)/4,(pane[2][1]+pane[3][1])/2+pane_height*.06)
  for who,actor in actors.items():
   h=round(pane_height*1.14);w=round(h*actor.width/actor.height)
   sprite=actor.resize((w,h),Image.Resampling.LANCZOS)
   layer=Image.new('RGBA',base.size);layer.alpha_composite(sprite,(round(center[0]-w*.5),round(center[1])))
   ar=np.array(layer);before_alpha=ar[:,:,3].copy()
   glass=np.where((rgb[:,:,3]>32)[:,:,None],rgb[:,:,:3],np.array([90,120,142]))
   ar[:,:,:3]=np.clip(ar[:,:,:3]*.84+glass*.16,0,255).round().astype('uint8')
   ar[:,:,3]=(ar[:,:,3].astype(float)*np.array(mask)/255).round().astype('uint8')
   # A crane strut can fully hide the seated operator; never expose disconnected face fragments.
   y0=round(center[1]);y1=y0+round(h*.6)
   original_head=before_alpha[y0:y1];visible_head=ar[y0:y1,:,3]
   retained=float(visible_head.sum())/max(1,float(original_head.sum()))
   _,_,parts,_=cv2.connectedComponentsWithStats((visible_head>32).astype('uint8'),8)
   areas=parts[1:,4];connected=float(areas.max())/max(1,int(areas.sum())) if len(areas) else 0
   shown=retained>=.9 and connected>=.88
   if not shown:ar[:,:,3]=0
   visibility.append({'format':fmt,'actor':who,'frame':frame,'headRetained':round(retained,4),'headConnected':round(connected,4),'shown':shown})
   layer=Image.fromarray(ar)
   bb=layer.getbbox()
   if bb:union=bb if union is None else (min(union[0],bb[0]),min(union[1],bb[1]),max(union[2],bb[2]),max(union[3],bb[3]))
   all_layers[who].append(layer)
   merged=Image.alpha_composite(base,layer)
   px,py=pos(3.2,-2.6,3.4)
   crop=(round(px)-220,round(py)-200,round(px)+220,round(py)+280)
   detail=merged.crop(crop).resize((220,240),Image.Resampling.LANCZOS)
   sx=frame%4*240;sy=frame//4*260
   sheets[who].paste(detail,(sx,sy+20));ImageDraw.Draw(sheets[who]).text((sx+2,sy+3),f'{fmt} {who} {frame:02} / 2x logical',fill='black')
   native=merged.crop(crop)
   if frame==15:
    native.save(W/f'candidates/{fmt}-{who}-rest-4x.png')
  # Keep only compact transparent overlays, not full high-res crane atlases.
 clean_atlas.save(W/f'candidates/{fmt}-top.webp',lossless=True,exact=True)
 for who,ims in all_layers.items():
  sheets[who].save(W/f'candidates/{fmt}-{who}-operator-proof.png')
  width,height=union[2]-union[0],union[3]-union[1]
  out=Image.new('RGBA',(width*4,height*4))
  for n,im in enumerate(ims):out.paste(im.crop(union),(n%4*width,n//4*height))
  out.save(W/f'candidates/{fmt}-top-{who}.webp',lossless=True)
 layouts[fmt]={'x':top['x']+union[0]/S,'y':top['y']+union[1]/S,'w':width/S,'h':height/S}
 print(fmt,'operator logical box',layouts[fmt])
(W/'reviews/operator-visibility.json').write_text(json.dumps(visibility,indent=2)+'\n')
(W/'inputs/operator-layouts.json').write_text(json.dumps({'scale':S,'boxes':layouts,'note':'Compact operator overlays use 4x logical pixels; the approved 2x crane background is resampled only in review sheets.'},indent=2)+'\n')
