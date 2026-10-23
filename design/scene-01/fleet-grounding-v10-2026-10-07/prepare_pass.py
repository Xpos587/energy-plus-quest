from PIL import Image
import numpy as np
from pathlib import Path
import sys,json,shutil
P=Path(__file__).resolve().parent
for frame in [int(v) for v in sys.argv[1:]] or [1]:
 raw=Image.open(P/f'shadow-raw-{frame:04}.png').convert('RGBA');a=np.array(raw)
 alpha=a[:,:,3].astype(float)/255
 # Cycles transparent catcher alpha is physically rendered shadow coverage.
 # Neutral black combined RGB is unnecessary: retain coverage and tint blue-grey.
 tint=np.empty_like(a);tint[:,:,:3]=(64,101,129);tint[:,:,3]=np.rint(a[:,:,3].astype(float)*.60).astype(np.uint8)
 Image.fromarray(tint).save(P/f'shadows-{frame:04}.png')
 src=P.parent/'fleet-style-v08-2026-10-07/projected/clean'/f'vehicles-{frame:04}.png'
 shutil.copyfile(src,P/f'vehicles-{frame:04}.png')
 bg=Image.open(P.parent/'whole-map-v06-2026-10-06/backdrop/city-v06.png').convert('RGBA').resize(raw.size,Image.Resampling.LANCZOS)
 bg=Image.alpha_composite(bg,Image.fromarray(tint));bg=Image.alpha_composite(bg,Image.open(src).convert('RGBA'));bg.save(P/f'pilot-composite-{frame:04}.png')
 print(frame,raw.size,'alpha range',float(alpha.min()),float(alpha.max()),'affected px',int(np.count_nonzero(alpha>0)), 'raw highest alpha RGBA',a.reshape(-1,4)[a[:,:,3].argmax()].tolist())
