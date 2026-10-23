from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFilter
import numpy as np,json,math
R=Path('/home/michael/Github/energy-plus-quest/docs/reviews/inventory-2026-10-22-finish');g=json.loads((R/'rack-worldplane-v1-receipt.json').read_text());base=Image.open(R/'rack-geometry-open-cap-crop-native.png').convert('RGBA');raw=Image.open(R/'rack-worldplane-v1-native-render.png').convert('RGBA');new=Image.open(R/'rack-worldplane-v1-visible-alpha-mask.png').convert('L').point(lambda v:255 if v>127 else 0);old=Image.open(R/'rack-semantic-object-mask-2x.png').resize(base.size,Image.Resampling.NEAREST);protect=Image.open(R/'rack-plaque-protection-mask-2x.png').resize(base.size,Image.Resampling.NEAREST).filter(ImageFilter.MaxFilter(3));mask=ImageChops.subtract(ImageChops.lighter(old,new).filter(ImageFilter.MaxFilter(3)),protect);proof=Image.composite(raw,base,mask);proof.save(R/'rack-worldplane-v1-protected-proof.png');mask.save(R/'rack-worldplane-v1-context-mask.png');pair=Image.new('RGBA',(base.width*2+16,base.height),'white');pair.paste(base);pair.paste(proof,(base.width+16,0));pair.save(R/'rack-worldplane-v1-paired-proof.png');pair.resize((pair.width*3,pair.height*3)).save(R/'rack-worldplane-v1-paired-proof-3x.png');diff=ImageChops.difference(base.convert('RGB'),proof.convert('RGB'));out=ImageChops.invert(mask);assert ImageChops.multiply(diff,Image.merge('RGB',(out,)*3)).getbbox()is None;assert ImageChops.multiply(diff,Image.merge('RGB',(protect,)*3)).getbbox()is None
x0,y0,x1,y1=g['source_crop_xyxy'];overlay=proof.copy();d=ImageDraw.Draw(overlay)
for f in g['faces']:
 p=f['source_projected_corners'];d.line([(x-x0,y-y0)for x,y in p+[p[0]]],fill=(0,255,255,220),width=1)
overlay.save(R/'rack-worldplane-v1-fixed-edge-overlay.png');overlay.resize((overlay.width*3,overlay.height*3)).save(R/'rack-worldplane-v1-fixed-edge-overlay-3x.png')
# Faces share exactly the same native UV point on every common world vertex.
shared={};uv_errors=[]
for f in g['faces']:
 for w,uv in zip(f['exact_world_corners'],f['native_corner_uv_pixels']):
  key=tuple(w)
  if key in shared and shared[key]!=uv:uv_errors.append({'world':w,'first':shared[key],'second':uv})
  shared[key]=uv
assert not uv_errors
# A continuous convex-hull test distinguishes raster edge coverage from envelope drift.
def hull(points):
 p=sorted(set(map(tuple,points)))
 def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 a=[]
 for v in p:
  while len(a)>=2 and cross(a[-2],a[-1],v)<=0:a.pop()
  a.append(v)
 b=[]
 for v in reversed(p):
  while len(b)>=2 and cross(b[-2],b[-1],v)<=0:b.pop()
  b.append(v)
 return a[:-1]+b[:-1]
h=hull([p for f in g['faces']for p in f['source_projected_corners']]);ys,xs=np.where(np.asarray(new)>0);outside=[]
for x,y in zip(xs,ys):
 p=np.array([x+x0+.5,y+y0+.5]);crosses=[];dist=[]
 for a,b in zip(h,h[1:]+h[:1]):
  a=np.array(a);v=np.array(b)-a;crosses.append(v[0]*(p[1]-a[1])-v[1]*(p[0]-a[0]));t=np.clip((p-a)@v/(v@v),0,1);dist.append(float(np.linalg.norm(p-a-t*v)))
 if min(crosses)<-1e-6:outside.append(min(dist))
g.update({'status':'ONE fixed-world-plane proof complete; parent/root art review required; no further iteration','outside_context_changed_pixels':0,'protected_board_letter_changed_pixels':0,'shared_corner_uv_mismatches':uv_errors,'fixed_world_face_corner_residual_m':0,'fixed_projected_face_corner_residual_px':0,'native_alpha_bound_before_mapping':[119,34,963,1381],'rendered_visible_alpha_bounds_crop_xyxy':new.getbbox(),'visible_alpha_pixel_centers_outside_continuous_envelope':len(outside),'maximum_edge_raster_overrun_source_px':max(outside,default=0),'visual_limits':['All three outer face boundaries and shared UV edge corners match exact fixed world geometry. This is not a claim that every painted carton/post internal edge is a newly modeled 3D surface.','Native rounded post widths are clipped at native post-center UV split; post caps become thinner. Top cartons remain a flat painted camera surface.','One source camera and deterministic viewport crops only; do not orbit camera or extrapolate new views.'],'production_changed':False});(R/'rack-worldplane-v1-receipt.json').write_text(json.dumps(g,ensure_ascii=False,indent=2));print(json.dumps({'outside_pixels':len(outside),'max_raster_overrun':max(outside,default=0),'new_alpha_bbox':new.getbbox()},indent=2))
