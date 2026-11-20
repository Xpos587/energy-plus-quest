"""Structural retouch on registered 2x paint: clone planar strips, not inpaint or optical flow."""
from pathlib import Path
import json,cv2,numpy as np
D=Path(__file__).resolve().parent; R=D/'../crane-r10/render'; L=D/'../crane-r11/layers'; m=json.loads((R/'manifest.json').read_text()); F=['wide','desk','mid','tall']
N=280; Y,X=np.indices((N,N),dtype=np.float32)
def crop(f,key):
 x,y=[round(a*2)-140 for a in m[f]['anchors'][key]]; whole=cv2.imread(str(L/f/'plate.png'));return whole[y:y+N,x:x+N].copy(),(x,y)
def poly(pts):
 a=np.zeros((N,N),np.uint8);cv2.fillPoly(a,[np.int32(np.array(pts)*16)],255,cv2.LINE_AA,shift=4);return a.astype(np.float32)/255

def build(f,k):
 im,where=crop(f,k); buf=im.copy();one=np.ones_like(X)
 def set(mask,v):
  nonlocal buf
  mask=np.clip(mask,0,1)[...,None];buf=(buf*(1-mask)+v*mask).round().astype(np.uint8)
 def stamp(mask,dx,dy,src=None):
  v=cv2.remap(im if src is None else src,(X+dx).astype('f'),(Y+dy).astype('f'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT);set(mask,v)
 def lattice(mask,dx,dy):
  full=cv2.imread(str(L/f/'plate.png'))
  v=cv2.remap(full,(X+where[0]+dx).astype('f'),(Y+where[1]+dy).astype('f'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT);set(mask,v)
 def bridge(mask,slope,along='x'):
  # Continue lines from BOTH ends of the interrupted beam/rail, using colour samples
  # just outside its silhouette. Fixed affine shear only, then undo it.
  src=im if along=='x' else im.transpose(1,0,2);alpha=mask if along=='x' else mask.T
  A=np.float32([[1,0,0],[-slope,1,95]])
  tmp=cv2.warpAffine(src,A,(N,N+200),borderMode=cv2.BORDER_REPLICATE);mm=cv2.warpAffine(alpha,A,(N,N+200));out=tmp.copy()
  for j,r in enumerate(mm):
   ii=np.flatnonzero(r>.01)
   if not ii.size:continue
   l=max(0,ii[0]-1);h=min(N-1,ii[-1]+1);ii=np.arange(l,h+1);tt=((ii-l)/max(1,h-l))[:,None]
   xl=(l-1-np.minimum(6,ii-l)*.65).astype(int).clip(0,N-1);xr=(h+1+np.minimum(6,h-ii)*.65).astype(int).clip(0,N-1)
   out[j,ii]=tmp[j,xl]*(1-tt)+tmp[j,xr]*tt
  v=cv2.warpAffine(out,A,(N,N),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP)
  set(one,v if along=='x' else v.transpose(1,0,2))
 def line(points,rgb,w):
  cv2.polylines(buf,[np.int32(np.array(points)*16)],False,tuple(bytes.fromhex(rgb)[::-1]),round(w),cv2.LINE_AA,4)
 def solid(pts,rgb):set(poly(pts),np.array(tuple(bytes.fromhex(rgb)[::-1])))
 def mask(pts,feather=1):return cv2.GaussianBlur(cv2.dilate(poly(pts),np.ones((5,5),np.uint8)),(0,0),feather)
 if f=='desk' and k=='petr':
  # Three parallel painted strips (portal crossbar, crane rail, coping). The helmet
  # interrupts the bottom edge of the crossbar. Fit end-to-end, not to the old rendered silhouette.
  a=mask([(121,78),(140,76),(155,88),(155,106),(148,111),(159,137),(161,170),(150,180),(154,199),(186,200),(222,196),(224,202),(188,215),(135,225),(115,222),(111,212),(119,188),(112,167),(107,157),(108,129),(114,116),(123,108)],1.25)
  # Rotate/shear neither individual beams nor tiles: trace the contact points of each
  # straight run and take one affine donor along that run. Keep the unoccluded bogie paint.
  bridge(a,-.34)
  # Match the measured coordinates of a line at both surviving ends. The RGB profiles
  # are read from the original upper/lower faces, NOT from either person's cutout.
  def profile(mask,xl,xr,slope):
   k=((X-xl)/(xr-xl)).clip(0,1)[...,None]
   def read(col):
    sx=col+.06*(X-col);return cv2.remap(im,sx,(Y+slope*(sx-X)).astype('f'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
   set(mask,read(xl)*(1-k)+read(xr)*k)
  q=Y+.36*X
  # The blue crossbar and its black underside (ink just clips the white hat).
  profile((q<134.8).astype('f'),115,153,-.337)
  # One wide cast shadow below the beam, with a lighter slit and a fine tile joint.
  # Trace the ink along its own plane; do not stretch the trolley's yellow end over the arm.
  profile(np.clip((q-134)/1.6,0,1),106,164,-.231)
  # Lit paving under the crossbar. In shade the source is an adjacent part of the same
  # cast shadow; in sun take clean paint from the patch between the bogies.
  sunny=np.zeros_like(im);sunny[:]=[156,179,247];tex=np.clip((X-125)*.077+(Y-143)*.065,-5,5);sunny=(sunny+tex[...,None]).clip(0,255)
  shadeEnd=182+.014*(X-125);set(np.clip((q-shadeEnd)/1.3,0,1),sunny)
  shadowMask=np.clip((q-(184+.99*(X-85)))/1.8,0,1)*np.clip((210+.99*(X-85)-q)/2,0,1)*np.clip((q-181)/2,0,1)
  dx=98-X;stamp(shadowMask,dx,.65*dx)
  # Curved edges in the *painted* steel have different endpoint slopes than Blender.
  # Reconstruct the rail at its surviving edges, not by copying its neighbours' sills.
  qs=Y+.31*X
  profile(np.clip((qs-214.6)/1.2,0,1),106,163,-.306)
  # Bright coping is one continuous strip. Donor is a clear section left of the boot.
  dx=96+.1*(X-130)-X;stamp(np.clip((Y+.331*X-246.7)/1.2,0,1),dx,-.331*dx)
  a*=1-poly([(157.7,136),(170,128),(184,132),(181,168),(177,168),(157.7,151)])
 elif f=='desk':
  a=mask([(118,66),(132,61),(145,63),(155,78),(157,91),(153,97),(157,106),(162,120),(165,158),(159,184),(158,200),(182,201),(199,205),(213,207),(237,210),(228,216),(198,228),(177,225),(164,221),(124,228),(117,222),(117,199),(117,175),(105,161),(109,127),(113,108),(123,99)],1)
  # The two diagonal slab joints define the tile translation. Source the next empty slab
  # downhill, bypassing the person's shadow on the edge that abuts the stairs.
  lattice(one,85,87.5)
  # Cast building shadow ends on this straight run by the stairs.
  a=np.maximum(a,mask([(151,141),(179,134),(185,137),(183,165),(169,186),(154,192)],2))
  edge=204.0-(X-114)*.35
  # Use a clean swatch wholly inside the curved building shadow. The nearby diagonal
  # joint runs beyond the repair; do not import a phantom joint from the next slab.
  set(np.clip((edge-Y)/1.5,0,1),cv2.remap(im,(185+.12*(X-140)).astype('f'),(139+.16*(Y-145)).astype('f'),cv2.INTER_LINEAR))
  # Curved plinth behind door and outside jamb.
  solid([(93,100),(158,67),(166,84),(162,120),(152,131),(130,145),(98,159)],'235598');
  solid([(75,112),(139,87),(139,146),(76,171)],'164888');solid([(81,124),(133,104),(133,147),(81,166)],'718cac');
  solid([(81,124),(133,104),(133,142),(108,148)],'225ea3');line([(81,124),(133,104),(133,146)],'182d4a',1);line([(81,124),(107,147)],'233e58',1)
  line([(81,124),(133,104)],'162d4f',1)
  # Door head and glazing reveal: sample the intact door head on the same plane.
  dx=94-X;stamp(poly([(78,101),(139,78),(139,101),(79,124)]),dx,-dx*.396)
  line([(139.2,84),(139.2,146.2)],'233d62',1);line([(132.7,104),(132.7,147.4)],'132e4a',1)
  # Steps: affine copy from the uninterrupted left half along the treads. Right ends from the painted stair width.
  stair=[(71,169),(135,146),(143,152),(143,158),(151,165),(151,172),(162,180),(162,189),(95,218),(70,194)]
  # Compress x on the source so each long face samples only intact treads, no source figure/smear.
  dx=(103+(X-133)*.10)-X;stamp(poly(stair),dx,-dx*.379)
  line([(135,146),(143,152),(143,159),(151,165),(151,172),(162,180),(162,189)],'69667a',1)
  # Restore the lower curved edge of the orange canopy using an affine tangent clone;
  # one hand-traced cubic contour is the known painted outer rim, not a warped building.
  pts=np.array([[96,94],[123,84.2],[148,71.5],[161,62.4]]);curve=np.poly1d(np.polyfit(pts[:,0],pts[:,1],2));yy=curve(X); roof=(yy-Y).clip(0,1);top=(yy-Y-18).clip(0,1)
  # Only the last ~10 pixels of paint below the unobscured upper roof are occluded.
  srcx=103+(X-130)*.2;stamp(roof,srcx-X,-.398*(srcx-X)-2.8)
  set(roof*np.clip(Y-yy+2,0,1),np.array([10,48,151]));set(roof*np.clip(Y-yy+.95,0,1),np.array([16,31,74]));set(top,im)
 elif k=='ivan':
  a=mask([(113,60),(128,55),(146,56),(159,73),(164,85),(160,103),(161,118),(167,145),(171,162),(162,177),(160,203),(172,213),(174,226),(157,232),(131,237),(118,235),(105,225),(105,185),(110,174),(105,163),(104,124),(114,104),(121,99),(115,88)],1)
  # Tile to the right along the cross joint (the longitudinal seam is restored separately).
  lattice(one,186.05,25.25)
  # Broad blend only on bare paving, bounded at stairs. The donor and receiving tile
  # differ in brush texture, so do not leave a matte shaped like Ivan's coat.
  openFloor=np.clip((X-71)/4,0,1)*np.maximum(np.clip((138-Y)/5,0,1),np.clip((X-(121.1-.194*(Y-147)))/5,0,1));
  a=np.maximum(a,cv2.GaussianBlur(cv2.dilate(a,np.ones((35,35),np.uint8)),(0,0),9)*openFloor)
  # The registered tiles nearly coincide, but preserve the cross joint at the
  # intersection. Source both lines from a SINGLE clean adjacent tile, no gap.

  # Continue the known long joint between the two intersections. Its source is bare tile above the helmet.
  # Invisible part of the rightmost tread: straight edges connect the surviving
  # nose at the foot of the stair to the top end visible beside Ivan's sleeve.
  tread=poly([(93.9,149.2),(98.0,150.7),(98.2,151.8),(107.5,154.4),(107.6,155.9),(116.7,158.1),(104.5,230.5),(82.6,223.9)])
  stamp(tread, -.192*(215-Y),215-Y)
  line([(93.9,149.2),(98.0,150.7),(98.2,151.8),(107.5,154.4),(107.6,155.9),(116.7,158.1),(104.5,230.5)],'9091a3',1)
  line([(107.4,154.5),(92.8,225.8)],'74758d',1)
 else:
  a=mask([(118,76),(132,68),(148,67),(161,78),(166,87),(159,101),(158,119),(169,145),(170,171),(165,180),(162,204),(172,218),(172,231),(157,235),(135,242),(121,241),(114,231),(103,225),(99,215),(103,200),(117,209),(121,188),(117,172),(113,153),(115,123),(125,108)],1)
  # Bare rail and coping below the shoe; keep both longitudinal ink edges at the
  # observed slope. Texture on the pavement comes from the open stretch of the berth.
  a=np.maximum(a,mask([(149,112),(164,111),(168,141),(150,145)],1))
  a=np.maximum(a,mask([(97,194),(110,198),(133,213),(150,224),(145,235),(109,223),(92,215)],1))
  dy=18+.1*(Y-140)-Y;stamp(one,-.231*dy,dy)
  curb=200.6-.231*Y
  dy=304+.3*(Y-140)-Y;lattice(np.clip(X-(164.1-.231*Y)-3,0,1),-.231*dy,dy)
  # The bogie's outer edge tapers from its visible top right corner to the end cap;
  # rebuild by cloning a narrow planar strip from the still-visible inside face.
  edge=153.5-.23*Y
  side=poly([(120,48),(142.5,50),(141,69),(125,132),(119,144),(102,142),(107,120)]);
  solid([(119,48),(142.5,50),(142.8,66),(126,134),(118.5,144),(109,144),(103,136)],'233d5d');
  solid([(117,59),(142,53),(138,72),(123,130),(116,138),(105,127)],'204779');solid([(102,126),(121,129),(118,143),(99,141)],'f3ab1a');line([(121,129),(118,143),(99,141)],'293849',1)
  # Source the unoccluded topping and affine dark side, not the head in the clone donor.
  solid([(142,51),(143,66),(128,131),(119,143),(122,129)],'213954');line([(142,51),(143,66),(127,132),(119,143)],'243044',1)
 return np.dstack((buf,(a*255).round().astype('uint8'))),im,where

def produce():
 out={}
 for f in F:
  out[f]={}
  for k,asset in [('ivan','porch'),('petr','post')]:
   base='tall' if f=='tall' else 'desk'; patch,orig,_=build(base,k);target,(x,y)=crop(f,k)
   if base!=f:
    # Fit canonical desk art to the matching crop in the independently registered, scaled plate.
    scale=m[base]['affine'][0][0]/m[f]['affine'][0][0];A=np.float32([[scale,0,140*(1-scale)],[0,scale,140*(1-scale)]])
    gray=lambda v:cv2.cvtColor(v,cv2.COLOR_BGR2GRAY).astype(np.float32)/255
    score,A=cv2.findTransformECC(gray(target),gray(orig),A,cv2.MOTION_AFFINE,(3,150,1.e-7),None,3);assert score>.96,(f,k,score)
    patch=cv2.warpAffine(patch,A,(N,N),flags=cv2.INTER_CUBIC|cv2.WARP_INVERSE_MAP)
   out[f][asset]=(patch,(x,y));
 return out
if __name__=='__main__':
 from PIL import Image
 patches=produce()
 for f in F:
  aa=[]
  for k,asset in [('ivan','porch'),('petr','post')]:
   im,_=crop(f,k);p,_=patches[f][asset];a=p[...,3:]/255; aa.append(np.hstack((im,(im*(1-a)+p[...,:3]*a).astype('uint8'))))
  cv2.imwrite(str(D/'work'/f'patch-{f}.png'),np.vstack(aa))
