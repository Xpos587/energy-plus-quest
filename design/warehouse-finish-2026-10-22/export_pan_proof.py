from PIL import Image
from pathlib import Path
import json
ROOT=Path('/home/michael/Github/energy-plus-quest');R=ROOT/'docs/reviews/inventory-2026-10-22-finish';m=json.loads((ROOT/'design/warehouse-blockout-2026-10-21/manifest-v4.json').read_text());c=m['runtime_source_contract'];s=Image.open(R/'source-v3-clean.png');a,b,e,d=c['portrait_initial_viewport_source_xyxy'];w=e-a;right=[1440-w,b,1440,d];s.transform((780,1180),Image.Transform.EXTENT,right,Image.Resampling.BICUBIC).save(R/'portrait-v3-pan-right.png');(R/'pan-right-proof-v3.json').write_text(json.dumps({'source':'source-v3-clean.png','viewport_source_xyxy':right,'all_source_targets':c['all_four_anchor_px'],'policy':'Same source plane, rightmost horizontal pan. Keeper/WMS remain in raster; no new scene or camera.'},indent=2))
