from pathlib import Path
from PIL import Image,ImageChops,ImageFilter,ImageDraw
import numpy as np,json,math
R=Path('/home/michael/Github/energy-plus-quest/docs/reviews/inventory-2026-10-22-finish');g=json.loads((R/'rack-billboard-v1.json').read_text());r=json.loads((R/'rack-registration-v1.json').read_text());crop=g['source_crop_xyxy'];base=Image.open(R/'rack-geometry-open-cap-crop-native.png').convert('RGBA');raw=Image.open(R/'rack-billboard-v1-native-render.png').convert('RGBA');assert base.size==raw.size
A=np.array(r['affine_native_to_source']);inv=np.linalg.inv(A);coeff=(inv[0,0],inv[0,1],inv[0,2]+inv[0,0]*crop[0]+inv[0,1]*crop[1],inv[1,0],inv[1,1],inv[1,2]+inv[1,0]*crop[0]+inv[1,1]*crop[1]);native=Image.open(R/'rack-sprite-v1-native.png').convert('RGBA');alpha=native.getchannel('A').point(lambda v:255 if v>192 else 0).transform(base.size,Image.Transform.AFFINE,coeff,Image.Resampling.NEAREST);alpha.save(R/'rack-billboard-v1-mapped-alpha.png');old=Image.open(R/'rack-semantic-object-mask-2x.png').resize(base.size,Image.Resampling.NEAREST);protect=Image.open(R/'rack-plaque-protection-mask-2x.png').resize(base.size,Image.Resampling.NEAREST).filter(ImageFilter.MaxFilter(3));mask=ImageChops.subtract(ImageChops.lighter(old,alpha).filter(ImageFilter.MaxFilter(5)),protect);proof=Image.composite(raw,base,mask);proof.save(R/'rack-billboard-v1-protected-proof.png');mask.save(R/'rack-billboard-v1-context-mask.png');diff=ImageChops.difference(base.convert('RGB'),proof.convert('RGB'));outside=ImageChops.invert(mask);d=ImageChops.multiply(diff,Image.merge('RGB',(outside,)*3));assert d.getbbox()is None
pair=Image.new('RGBA',(base.width*2+16,base.height),'white');pair.paste(base);pair.paste(proof,(base.width+16,0));pair.save(R/'rack-v1-paired-proof.png');pair.resize((pair.width*3,pair.height*3)).save(R/'rack-v1-paired-proof-3x.png')
# Fixed geometry axes overlay is evidence only; it never warps the comparison.
targets=r['anchor_residuals'];T={x['name']:x for x in targets};segments=[('X-front','front-left-top','front-right-top'),('X-back','back-left-top','back-right-top'),('Y-left','front-left-top','back-left-top'),('Y-right','front-right-top','back-right-top'),('Z-front-left','front-left-foot','front-left-top'),('Z-front-right','front-right-foot','front-right-top'),('Z-back-right','back-right-foot','back-right-top')];angles=[];overlay=proof.copy();draw=ImageDraw.Draw(overlay)
def angle(a,b):
 v=np.array(a);w=np.array(b);return math.degrees(math.acos(float(np.clip(v@w/np.linalg.norm(v)/np.linalg.norm(w),-1,1))))
for label,n0,n1 in segments:
 t0=np.array(T[n0]['source_xy']);t1=np.array(T[n1]['source_xy']);p0=np.array(T[n0]['registered_source_xy']);p1=np.array(T[n1]['registered_source_xy']);angles.append({'axis':label,'direction_error_degrees':angle(t1-t0,p1-p0),'target_vector':(t1-t0).tolist(),'registered_vector':(p1-p0).tolist()});draw.line([(t0[0]-crop[0],t0[1]-crop[1]),(t1[0]-crop[0],t1[1]-crop[1])],fill=(0,255,255,220),width=1)
for row in targets:
 x,y=row['source_xy'];draw.ellipse((x-crop[0]-2,y-crop[1]-2,x-crop[0]+2,y-crop[1]+2),outline=(255,0,255,255));px,py=row['registered_source_xy'];draw.line([(x-crop[0],y-crop[1]),(px-crop[0],py-crop[1])],fill=(255,0,255,255),width=1)
overlay.save(R/'rack-v1-fixed-edge-overlay.png');overlay.resize((overlay.width*3,overlay.height*3)).save(R/'rack-v1-fixed-edge-overlay-3x.png')
def hull(points):
 p=sorted(set(map(tuple,points)))
 def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lower=[]
 for x in p:
  while len(lower)>=2 and cross(lower[-2],lower[-1],x)<=0:lower.pop()
  lower.append(x)
 upper=[]
 for x in reversed(p):
  while len(upper)>=2 and cross(upper[-2],upper[-1],x)<=0:upper.pop()
  upper.append(x)
 return lower[:-1]+upper[:-1]
h=hull(g['projected_physical_envelope_corners']);env=Image.new('L',base.size);ImageDraw.Draw(env).polygon([(x-crop[0],y-crop[1])for x,y in h],fill=255);env.save(R/'rack-v1-fixed-physical-envelope.png');over=ImageChops.subtract(alpha,env);over.save(R/'rack-v1-alpha-outside-envelope.png');oy,ox=np.where(np.asarray(over)>0);maxdist=0
for x,y in zip(ox,oy):
 p=np.array([x+crop[0],y+crop[1]]);dist=[]
 for a,b in zip(h,h[1:]+h[:1]):
  a=np.array(a);v=np.array(b)-a;t=np.clip((p-a)@v/(v@v),0,1);dist.append(np.linalg.norm(p-a-t*v))
 maxdist=max(maxdist,min(dist))
r['axis_direction_residuals']=angles;r['mapped_alpha_bounds_crop_xyxy']=alpha.getbbox();r['alpha_pixels_outside_projected_physical_envelope']=len(ox);r['maximum_alpha_overrun_source_px']=float(maxdist);r['verdict']='REJECT for strict geometry promotion; retain as final bounded stylistic alternative only. One affine cannot make native opposite Y depth directions parallel, and mapped silhouette overruns fixed projected physical envelope. No further generation/iteration authorized in this lane.';r['outside_context_changed_pixels']=0;r['plaque_protected_changed_pixels']=0;r['mask_policy']='Union original rack silhouette and transformed native alpha, dilated2px, minus original board+letter protection dilated1px. All original board/text and all outside pixels copied exactly from original native crop.';r['native_modified']=False;r['production_changed']=False;(R/'rack-registration-v1.json').write_text(json.dumps(r,indent=2));print(json.dumps({'rms':r['rms_source_px'],'max':r['max_source_px'],'axes':angles,'outside_envelope_pixels':len(ox),'maximum_overrun_px':maxdist,'verdict':r['verdict']},indent=2))
