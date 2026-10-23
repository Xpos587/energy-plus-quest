from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np
P=Path(__file__).resolve().parent
bg=Image.open(P.parent/'fleet-road-v11-2026-10-07/backdrop-v11.png').convert('RGBA');mask=Image.open(P.parent/'fleet-lookdev-v10-2026-10-07/road-receiver-mask.png').convert('L');ma=np.array(mask,dtype=np.float32)/255
for f in (385,1):
 a=Image.open(P/f'physical-shadow-{f:04}.png').getchannel('A').resize(bg.size,Image.Resampling.LANCZOS)
 alpha=np.rint(np.array(a,dtype=np.float32)*ma*.55).astype(np.uint8);sh=Image.new('RGBA',bg.size,(77,88,96,0));sh.putalpha(Image.fromarray(alpha))
 veh=Image.open(P/f'vehicles-{f:04}.png').convert('RGBA');Image.alpha_composite(Image.alpha_composite(bg,sh),veh).convert('RGB').save(P/f'map-v14-{f:04}.png')
