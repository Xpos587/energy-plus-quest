from PIL import Image
import numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
for f in [1,385,769]:
 a=np.array(Image.open(P/f'shadow-raw-{f:04}.png').convert('RGBA'));a[:,:,:3]=(83,91,96);a[:,:,3]=np.rint(a[:,:,3].astype(float)*.60).astype(np.uint8);Image.fromarray(a).save(P/f'shadows-{f:04}.png')
 print(f,'pixels',int(np.count_nonzero(a[:,:,3])),'maxalpha',int(a[:,:,3].max()))
