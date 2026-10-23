from pathlib import Path
from PIL import Image
import json
P=Path(__file__).resolve().parent
F=P.parent/'painted-layer-2026-10-05/final-4k-frames'
B=P.parent/'four-truck-loop-2026-10-04/v2b-empty-map.png'
bg=Image.open(B).convert('RGBA');out=[]
for i in [1,97,385,577,769,961,1152]:
 fg=Image.open(F/f'{i:04}.png').convert('RGBA');canvas=bg.resize(fg.size,Image.Resampling.LANCZOS);canvas.alpha_composite(fg)
 path=P/f'map-{i:04}.png';canvas.convert('RGB').save(path);out.append({'frame':i,'seconds':(i-1)/24,'dimensions':list(canvas.size),'image':path.name})
(P/'receipt.json').write_text(json.dumps({'fleet_source':str(F),'background':str(B),'render_source':'../painted-layer-2026-10-05/painted-vehicles-driver-fixed-optimized.blend','motion_changed':False,'four_trucks':True,'frame_count':1152,'fps':24,'duration_seconds':48,'stills':out,'limitations':['Prior native vehicle geometry and driver appearance retained; isolated green v04 image is not an animated fleet asset.','Illustrated backdrop registration requires visual review; no pixel-exact geometry claim.']},indent=2))
print('Seven complete-map stills written')
