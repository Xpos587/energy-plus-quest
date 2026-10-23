from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageFilter
import json
P=Path('/home/michael/Github/energy-plus-quest');R=P/'docs/reviews/inventory-2026-10-22-finish';p=R/'rack-worldplane-v1-full-receipt.json';m=json.loads(p.read_text());raw=Image.open(R/'rack-worldplane-v1-full-raw-source.png').convert('RGB');before=Image.open(R/'forklift-combined-v3-source.png').convert('RGB');mask=Image.new('L',raw.size);draw=ImageDraw.Draw(mask)
def hull(points):
 points=sorted(set(map(tuple,points)))
 def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 a=[]
 for q in points:
  while len(a)>=2 and cross(a[-2],a[-1],q)<=0:a.pop()
  a.append(q)
 b=[]
 for q in reversed(points):
  while len(b)>=2 and cross(b[-2],b[-1],q)<=0:b.pop()
  b.append(q)
 return a[:-1]+b[:-1]
for b in m['boards']:draw.polygon(hull(b['projected_board_bbox_corners_small']),fill=255)
mask=mask.filter(ImageFilter.MaxFilter(3));protected=Image.composite(before,raw,mask);protected.save(R/'rack-worldplane-v1-full-source.png');mask.save(R/'rack-worldplane-v1-full-original-board-protection-mask.png');assert ImageChops.multiply(ImageChops.difference(before,protected),Image.merge('RGB',(mask,)*3)).getbbox()is None
manifest=json.loads((P/'design/warehouse-blockout-2026-10-21/manifest-v4.json').read_text());c=manifest['runtime_source_contract'];scale=960/1440;off=(667-1000*scale)/2
rect=c['portrait_initial_viewport_source_xyxy'];width=rect[2]-rect[0];right=[1440-width,rect[1],1440,rect[3]]
def scaled(b):return[b[0]*scale,b[1]*scale+off,b[2]*scale,b[3]*scale+off]
for name,box,size in [('desktop',c['desktop_viewport_source_xyxy'],(960,600)),('portrait',rect,(390,590)),('pan-right',right,(390,590))]:
 protected.transform(size,Image.Transform.EXTENT,scaled(box),Image.Resampling.BICUBIC).save(R/f'rack-worldplane-v1-full-{name}.png');before.transform(size,Image.Transform.EXTENT,scaled(box),Image.Resampling.BICUBIC).save(R/f'rack-worldplane-v1-full-before-{name}.png')
pair=Image.new('RGB',(1936,707),'white');d=ImageDraw.Draw(pair);pair.paste(before,(0,40));pair.paste(protected,(976,40));d.text((12,12),'BEFORE — V3, NOT ART ACCEPTED',fill='black');d.text((988,12),'ONE BOUNDED 2.5D SURFACE ALTERNATIVE — REVIEW ONLY',fill='black');pair.save(R/'rack-worldplane-v1-full-marked-comparison.png')
for view in ['portrait','pan-right']:
 a=Image.open(R/f'rack-worldplane-v1-full-before-{view}.png');b=Image.open(R/f'rack-worldplane-v1-full-{view}.png');pair=Image.new('RGB',(796,622),'white');pair.paste(a,(0,32));pair.paste(b,(406,32));d=ImageDraw.Draw(pair);d.text((10,10),'BEFORE',fill='black');d.text((416,10),'2.5D ALTERNATIVE / REVIEW ONLY',fill='black');pair.save(R/f'rack-worldplane-v1-full-{view}-comparison.png')
m['all_six_boards_protected_decoded_difference']=0;m['board_protection_policy']='Reuse exact decoded V3 original six board/text pixels within projected board silhouette +1px. Raw small render retained separately. No native sprite edits.';m['canonical_source_plane']=[1440,1000];m['crop_contract']={'desktop':c['desktop_viewport_source_xyxy'],'portrait':rect,'pan_right':right,'small_source_scale':scale,'small_source_y_offset':off};p.write_text(json.dumps(m,ensure_ascii=False,indent=2))
