"""Build runtime art + checks from the isolated Blender renders. Everything writes beside this script."""
from pathlib import Path
import ctypes,json,math,cv2,numpy as np
from PIL import Image
from scipy import ndimage as nd
from patches import D,R,L,F,m,produce
cv2.setNumThreads(2); W=D/'work';assets=D/'assets';QA=D/'qa'; QA.mkdir(exist_ok=True)
axes=json.loads((W/'axes.json').read_text());cells=json.loads((W/'cells.json').read_text()); geo=np.load(W/'geometry.npz');seats=np.load(W/'seats.npz');lib=ctypes.CDLL(str(W/'depth.so'));ptr=np.ctypeslib.ndpointer(np.float32,flags='C_CONTIGUOUS');lib.raster.argtypes=[ptr,ctypes.c_int,ctypes.c_int,ptr,ctypes.c_int];lib.raster.restype=None

def project(f,v):
 a=axes[f];s=a['ppm'];p=np.asarray(v)@np.array(a['basis']).T;p[...,:2]=p[...,:2]*[s,-s]+a['origin'];return p

def render_depth(f,tri,xy,size):
 p=project(f,tri);p[...,:2]-=xy;z=np.full((size[1],size[0]),-1e10,np.float32);lib.raster(z,*size,np.ascontiguousarray(p,np.float32),len(p));return z

def calc_lut():
 # Same 32-bin normalized convolution as stylize.py; underlying reference is the matched 2x pair.
 B=32;sums=np.zeros((B,B,B,3));counts=np.zeros((B,B,B));
 for f in F:
  ref=cv2.imread(str(R/f/'plate.png'))[::5,::5].copy();paint=cv2.imread(str(L/f/'plate.png'))[::5,::5];
  for nm in ['barge','ivan','far','ladder']:
   p=cv2.imread(str(R/f/(nm+'.png')),-1)[::5,::5];a=p[...,3:4]/255;ref=(ref*(1-a)+p[...,:3]*a).round().astype('uint8')
  ix=tuple((ref.reshape(-1,3).astype(int)*B//256).T);np.add.at(counts,ix,1);np.add.at(sums,ix,paint.reshape(-1,3))
 n=nd.gaussian_filter(counts,1.2);lut=np.stack([nd.gaussian_filter(sums[...,i],1.2)/n.clip(1.e-5) for i in range(3)],-1);un=(np.indices((B,B,B)).transpose(1,2,3,0)+.5)*256/B;lut[n<.5]=un[n<.5];return lut

def recolour(im,lut):
 bgr=im[...,:3];a=im[...,3].astype('f')/255;idx=(bgr.reshape(-1,3).T.astype('f')/8-.5).clip(0,31)
 mapped=np.stack([nd.map_coordinates(lut[...,i],idx,order=1) for i in range(3)],-1).reshape(bgr.shape)
 # Hue-preserving blend: the global LUT has no skin training region & misclassifies hard hats as crane steel.
 # Keep art-directed orange/navy/skin pigments from the worker, use the quay LUT for ambient hue and value.
 out=.84*bgr+.16*mapped;ink=np.array([51,39,30]);inner=cv2.GaussianBlur(cv2.Canny(bgr,55,120).astype('f')/255,(0,0),.52)*a*.61
 out=out*(1-inner[...,None])+ink*inner[...,None];ring=np.maximum(cv2.GaussianBlur(cv2.dilate((a>.4).astype('f'),np.ones((3,3),np.uint8)),(0,0),.56),a)
 out=(out*a[...,None]+ink*(ring-a)[...,None])/ring.clip(1e-6)[...,None];return np.dstack([out,ring*255]).clip(0,255).round().astype('uint8')

def rgba(p):return cv2.imread(str(p),cv2.IMREAD_UNCHANGED)
def bounds(a,pad=2):
 x,y,w,h=cv2.boundingRect((a>1).astype('uint8'));assert w and h;return max(0,x-pad),max(0,y-pad),min(a.shape[1],x+w+pad),min(a.shape[0],y+h+pad)
def crop_box(im,b):x,y,r,t=b;return im[y:t,x:r]
def composite(base,im,x,y):
 roi=base[y:y+im.shape[0],x:x+im.shape[1]];a=im[...,3:]/255;roi[:]=(roi*(1-a)+im[...,:3]*a).round().astype('uint8')
def atop(fg,bg):
 a=fg[...,3:].astype('f')/255;b=bg[...,3:].astype('f')/255;sum_a=a+b*(1-a);v=(fg[...,:3]*a+bg[...,:3]*b*(1-a))/sum_a.clip(1.e-6);return np.dstack([v,sum_a*255]).round().astype('uint8')
def save(fname,im):
 im=im.copy();im[im[...,3]==0]=0;p=assets/f/(fname+'.webp');p.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGRA2RGBA)).save(p,lossless=True,method=5);return str(p.relative_to(D))
def sprite(key,im,origin,pad=2):
 b=bounds(im[...,3],pad);x,y,r,t=b;return {'src':save(key,crop_box(im,b)),'x':(origin[0]+x)/2,'y':(origin[1]+y)/2,'w':(r-x)/2,'h':(t-y)/2}
def rot(v,deg):
 a=np.deg2rad(deg);c=np.cos(a);s=np.sin(a);return np.asarray(v)@np.array([[c,s,0],[-s,c,0],[0,0,1]])

def build_people(f,formats,lut):
 fmt=formats[f];cells0=cells['items']; ppm=cells['ppm'];atlas=rgba(W/(('tall' if f=='tall' else 'desk')+'-atlas.png'));size=round(cells0[0]['box'][2]*axes[f]['ppm']/ppm);local=tuple(np.round(np.array(cells['anchor'])*size).astype(int));frames={};cab_depth={}
 for c in cells0:
  x,y,w,h=c['box']; p=atlas[y:y+h,x:x+w].copy();act=c['action'];who=c['who'];idx=c['i'];p=recolour(cv2.resize(p,(size,size),interpolation=cv2.INTER_AREA),lut); key=act.lower()+who if act in ['Cab','Climb'] else 'walk'+who+act
  world=m['scene']['routes']['rush' if who=='Ivan' else 'petr'][0]; foot=np.rint(project(f,world)[:2]).astype(int); corner=foot-local
  if act=='Climb':foot=np.rint(project(f,[60.2,3.9,0])[:2]).astype(int);corner=foot-local
  elif act=='Cab':
   pivot=m['scene']['pivot'];angle=c['angle'];seat=rot([4.38,-3.17,1.06],angle)+pivot; pos=project(f,seat)[:2];corner=np.rint(pos-local).astype(int)
   near=rot(geo['near_top']-pivot,angle)+pivot;person=rot(seats[who]*1.84,angle)+seat
   z=render_depth(f,person,corner,(size,size));z=nd.maximum_filter(z,3);occ=render_depth(f,near,corner,(size,size));hide=((occ>z)|(z<-1e9)).astype('f');hide=cv2.GaussianBlur(cv2.dilate(hide,np.ones((3,3),np.uint8)),(0,0),.68)
   p[...,3]=np.rint(p[...,3]*(1-hide)).astype('uint8');p[...,:3]=(p[...,:3]*np.array([.81,.79,.76])+np.array([17,12,8])).clip(0,255)
  else:
   # Occlusion footprint softens outwards; independent from the opaque shoe silhouettes.
   y,x=np.indices(p.shape[:2]);fx,fy=local;shadow=np.exp(-.5*(((x-fx)/(.53*axes[f]['ppm']))**2+((y-fy)/(.14*axes[f]['ppm']))**2));bg=np.full_like(p,(93,72,65,0));bg[...,3]=(shadow*74).astype('uint8');p=atop(p,bg)
  if act=='Cab':
   b=bounds(p[...,3],2);l,t,r,h=b;cab_depth.setdefault(key,[]).append((crop_box(p,b),corner+np.array([l,t])))
  else:frames.setdefault(key,[]).append((p,corner))
 for key,entries in frames.items():
  imgs,coords=zip(*entries);b=bounds(np.maximum.reduce([p[...,3] for p in imgs]),3);l,t,r,h=b;sheet=np.hstack([crop_box(im,b) for im in imgs]);cx,cy=coords[0];fmt['sprites'][key]=dict(src=save(key,sheet),x=(cx+l)/2,y=(cy+t)/2,w=(r-l)/2,h=(h-t)/2,anchorX=(local[0]-l)/2,anchorY=(local[1]-t)/2,cols=len(imgs),rows=1,frames=list(range(len(imgs))))
 for k,items in cab_depth.items():
  # Same shared-cell atlas contract as the app's 4x4 crane-top slew. Grids must be
  # advanced by the SAME frame; the cab does not move with an independent CSS tween.
  origin=np.min([xy for _,xy in items],axis=0);end=np.max([xy+np.array([im.shape[1],im.shape[0]]) for im,xy in items],axis=0);w,h=end-origin
  sheet=np.zeros((4*h,4*w,4),np.uint8);rects=[]
  for i,(im,xy) in enumerate(items):
   x,y=xy-origin+np.array([(i%4)*w,(i//4)*h]);sh,sw=im.shape[:2];sheet[y:y+sh,x:x+sw]=im
   rects.append(dict(x=xy[0]/2,y=xy[1]/2,w=sw/2,h=sh/2))
  fmt['sprites'][k]=dict(src=save(k,sheet),x=origin[0]/2,y=origin[1]/2,w=w/2,h=h/2,cols=4,rows=4,frames=list(range(16)),frameBoxes=rects,restFrame=15)

def curtain(segment):
 a,b=np.float32(segment);d=b-a;d=d/max(.001,np.linalg.norm(d));a=a-d*2.6;b=b+d*2.6;lo=np.array([0,0,-.75]);up=np.array([0,0,6.45]);return np.array([[a+lo,b+lo,b+up],[a+lo,b+up,a+up]])

def occlusion(f,fmt,patches):
 plate=cv2.imread(str(L/f/'plate.png'));wh=(plate.shape[1],plate.shape[0]);base=np.concatenate([geo[k] for k in geo if k not in ['near_top','gift']]);depth=render_depth(f,base,(0,0),wh)
 # Plate geometry only: the moving top/gift are not painted here and must be drawn above the walk separately.
 for who,route in [('Ivan',m['scene']['routes']['rush']),('Petr',m['scene']['routes']['petr'])]:
  clean=plate.copy();p,xy=patches[f]['porch' if who=='Ivan' else 'post'];composite(clean,p,*xy)
  # Divide the walk at the last bend. Two different depth orderings can coincide on the same screen ray.
  for j,(parts,key) in enumerate([(list(zip(route[:-2],route[1:-1])),'walkOccluder' if who=='Ivan' else 'walkOccluderPetr'),([(route[-2],route[-1])],'turnOccluder'+who)]):
   a=np.zeros(depth.shape,np.uint8)
   for segment in parts:
    front=render_depth(f,curtain(segment),(0,0),wh);a|=((depth>front+.035)&(front>-1e9)).astype('uint8')
   # A route in front of everything has no visible holdout. Don't manufacture a dummy texture.
   if not a.any():fmt['sprites'][key]=None;continue
   a=cv2.GaussianBlur(cv2.dilate(a,np.ones((3,3),np.uint8)).astype('f'),(0,0),.75);s=sprite(key,np.dstack([clean,(a*255).round().astype('uint8')]),(0,0));fmt['sprites'][key]=s
 # Climber in front of the ladder (on the outside of its cage); a short vertical curtain across its width.
 c=np.array([60.2,3.9,0]);right=np.asarray(axes[f]['basis'][0]);a=c-right*1.6;b=c+right*1.6;up=np.array([0,0,17.8]);tri=np.array([[a,b,b+up],[a,b+up,a+up]]);front=render_depth(f,tri,(0,0),wh);alpha=((depth>front+.035)&(front>-1e9)).astype('f');
 if alpha.any():
  a=(cv2.GaussianBlur(alpha,(0,0),.72)*255).round().astype('uint8');fmt['sprites']['climbOccluder']=sprite('climbOccluder',np.dstack([plate,a]),(0,0))
 else:fmt['sprites']['climbOccluder']=None

if __name__=='__main__':
 formats={};out={'scale':2,'units':'plate CSS pixels','walkCycleMetres':3.648,'formats':formats};lut=calc_lut();patches=produce()
 for f in F:
  fmt=formats[f]={'width':m[f]['width'],'height':m[f]['height'],'sprites':{}};build_people(f,formats,lut)
  for nm,(im,xy) in patches[f].items():fmt['sprites'][nm]=sprite(nm,im,xy)
  occlusion(f,fmt,patches);print('Exported',f,flush=True)
 (D/'manifest.json').write_text(json.dumps(out,indent=1,default=lambda v:v.item())+'\n')
