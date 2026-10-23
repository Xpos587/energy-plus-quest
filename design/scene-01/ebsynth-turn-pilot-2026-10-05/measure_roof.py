from pathlib import Path
from PIL import Image
import numpy as np
import json

ROOT=Path(__file__).parent
results={}
for method in ('transfer-three','transfer-coordinates'):
    files=sorted((ROOT/method/'frames').glob('*.png'))
    if len(files)!=72: continue
    rows=[]
    for p in files:
        output=np.asarray(Image.open(p).convert('RGB')).astype(float)
        size=(output.shape[1],output.shape[0])
        coordinate=np.asarray(Image.open(ROOT/'geometry/coordinateframes'/p.name).resize(size,Image.Resampling.NEAREST))
        source=np.asarray(Image.open(ROOT/'geometry/guideframes'/p.name).convert('RGB').resize(size,Image.Resampling.LANCZOS))
        mask=(coordinate[:,:,3]>250)&(coordinate[:,:,2]>249)&(source.min(axis=2)>200)
        pixels=output[mask]
        blue=(pixels[:,2]-pixels[:,0]>8)&(pixels[:,0]<225)
        rows.append({'frame':int(p.stem),'roof_pixels':int(mask.sum()),'blue_patch_fraction':float(blue.mean()),'luminance_std':float(np.std(pixels.mean(axis=1)))})
    results[method]={'frames':rows,'mean_blue_patch_fraction':float(np.mean([r['blue_patch_fraction'] for r in rows])),'mean_roof_luminance_std':float(np.mean([r['luminance_std'] for r in rows]))}
receipt={'scope':'diagnostic on flat white trailer roof; not full art or temporal quality score','mask':'guide alpha >250 and local generated z >249 and source RGB min >200; no painted-output selection','blue_patch_threshold':'output B-R >8 and R <225','results':results}
(ROOT/'review/roof-diagnostic.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps({k:{n:v for n,v in r.items() if n!='frames'} for k,r in results.items()},indent=2))
