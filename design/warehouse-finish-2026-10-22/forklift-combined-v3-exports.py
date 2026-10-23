from PIL import Image
from pathlib import Path
import json
ROOT=Path('/home/michael/Github/energy-plus-quest');R=ROOT/'docs/reviews/inventory-2026-10-22-finish';m=json.loads((ROOT/'design/warehouse-blockout-2026-10-21/manifest-v4.json').read_text());c=m['runtime_source_contract'];s=Image.open(R/'forklift-combined-v3-source.png');scale=960/1440;off=(667-1000*scale)/2
def scaled(b):return [b[0]*scale,b[1]*scale+off,b[2]*scale,b[3]*scale+off]
rect=c['portrait_initial_viewport_source_xyxy'];width=rect[2]-rect[0];right=[1440-width,rect[1],1440,rect[3]]
for name,box,size in [('desktop',c['desktop_viewport_source_xyxy'],(960,600)),('portrait',rect,(390,590)),('pan-right',right,(390,590))]:s.transform(size,Image.Transform.EXTENT,scaled(box),Image.Resampling.BICUBIC).save(R/f'forklift-combined-v3-{name}.png')
b=Image.open(R/'source-v3-clean.png');before=b.transform((960,667),Image.Transform.EXTENT,[0,-.25,1440,1000.25],Image.Resampling.BICUBIC);before.save(R/'forklift-combined-v3-before.png');pair=Image.new('RGB',(1936,667),'white');pair.paste(before,(0,0));pair.paste(s,(976,0));pair.save(R/'forklift-combined-v3-pair.png')
(R/'forklift-combined-v3-views.json').write_text(json.dumps({'status':'comparison only, not promotion','render_dimensions':list(s.size),'canonical_plane':[1440,1000],'source_coordinate_mapping':{'scale_xy':scale,'offset_y_px':off},'desktop_canonical_crop':c['desktop_viewport_source_xyxy'],'portrait_canonical_crop':rect,'right_pan_canonical_crop':right,'frame_policy':'All crops from one small full-source render. No new scene or geometry. Output surface iteration stops pending combined verdict.'},indent=2))
