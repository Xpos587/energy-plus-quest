from PIL import Image
from pathlib import Path
import json
root=Path('/home/michael/Github/energy-plus-quest');r=root/'docs/reviews/inventory-2026-10-22-finish';m=json.loads((root/'design/warehouse-blockout-2026-10-21/manifest-v4.json').read_text());c=m['runtime_source_contract'];s=Image.open(r/'source-v2-clean.png')
s.transform((1440,900),Image.Transform.EXTENT,c['desktop_viewport_source_xyxy'],Image.Resampling.BICUBIC).save(r/'desktop-v2-clean.png')
s.transform((780,1180),Image.Transform.EXTENT,c['portrait_initial_viewport_source_xyxy'],Image.Resampling.BICUBIC).save(r/'portrait-v2-clean.png')
(r/'viewport-provenance-v2.json').write_text(json.dumps({'source':'source-v2-clean.png','source_dimensions':list(s.size),'desktop_source_xyxy':c['desktop_viewport_source_xyxy'],'portrait_source_xyxy':c['portrait_initial_viewport_source_xyxy'],'policy':'Both camera views are deterministic exact source-plane EXTENT samples. No independent generation. Pan uses full 1440x1000 source.'},indent=2))
