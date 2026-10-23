from pathlib import Path
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent;OLD=P.parent/'fleet-native-v14-2026-10-07'
bg=Image.open(P.parent/'fleet-road-v11-2026-10-07/backdrop-v11.png').convert('RGBA');mask=np.array(Image.open(P.parent/'fleet-lookdev-v10-2026-10-07/road-receiver-mask.png').convert('L'),dtype=np.float32)/255
for f in (385,1):
 color=P/f'vehicles-{f:04}.png'
 if not color.exists():continue
 a=Image.open(P/f'physical-shadow-{f:04}.png').getchannel('A').resize(bg.size,Image.Resampling.LANCZOS);sh=Image.new('RGBA',bg.size,(77,88,96,0));sh.putalpha(Image.fromarray(np.rint(np.array(a,dtype=np.float32)*mask*.48).astype(np.uint8)));veh=Image.open(color).convert('RGBA');Image.alpha_composite(Image.alpha_composite(bg,sh),veh).convert('RGB').save(P/f'map-v15-{f:04}.png')
