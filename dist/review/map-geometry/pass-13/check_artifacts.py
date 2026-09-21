"""Pass13 raster/preservation regressions; drawing quality still needs visual review."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
SOURCE=Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-13')
REPO=Path('/home/michael/Github/energy-plus-quest')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in json.loads((SOURCE/'preserved-hashes.json').read_text()).items():
    assert sha(REPO/name)==digest, f'Protected artifact changed: {name}'
character=Image.open(REPO/'design/scene-01/assets/current/choices/professional.webp').convert('RGB')
cutout=Image.open(P.parent/'pass-12/professional-cutout.png').convert('RGBA')
assert np.array_equal(np.asarray(character),np.asarray(cutout)[:,:,:3])
image=Image.open(P/'map.jpg');assert image.size==(2880,2000)
pixels=np.asarray(image.resize((1440,1000),Image.Resampling.LANCZOS))
assert pixels.min(axis=2).max()>240
for edge in (pixels[0],pixels[-1],pixels[:,0],pixels[:,-1]):
    dark=edge.max(axis=1)<8
    assert not any(dark[i:i+8].all() for i in range(len(dark)-7)), 'Registration left a black frame hole'
rows=[]
for y in (403,405,412,420):
    white=pixels[y,355:602].min(axis=1)>215;runs=[];start=None
    for x,v in enumerate([*white,False]):
        if v and start is None:start=x
        if not v and start is not None:runs.append((start+355,x+354));start=None
    assert len(runs)==7,(y,runs)
    centers=[(a+b)/2 for a,b in runs]
    # Centers are manually inspected on the final six front doors, not invented by this test.
    for i,door in enumerate([395,429,463,498,533,568]):
        assert .35<(door-centers[i])/(centers[i+1]-centers[i])<.72
    rows.append({'y':y,'paintedBayBoundaries':centers})
old=np.asarray(Image.open(P.parent/'pass-12/map-a.jpg').convert('RGB'))
regions={'warehouse':(350,93,637,447),'foliage':(285,647,605,806),'trucks':(310,450,525,595),'road':(665,270,750,525),'shops':(775,650,1045,825)}
changes={}
for name,(x0,y0,x1,y1) in regions.items():
    delta=np.abs(pixels[y0:y1,x0:x1].astype(float)-old[y0:y1,x0:x1]).mean(axis=2)
    changes[name]={'meanRGBDifference':float(delta.mean()),'fractionDifferentByOver8':float((delta>8).mean())}
    assert changes[name]['fractionDifferentByOver8']>.65,(name,changes[name])
for path in P.glob('*.jpg'):
    with Image.open(path) as im: im.verify()
for path in P.glob('detail-*.png'):
    with Image.open(path) as im: im.verify()
registration=json.loads((P/'registration.json').read_text())
assert registration['oldEnvironmentPixelsInserted']==0
assert registration['minimumJacobian']>.25
assert json.loads((P/'scene-check.json').read_text())['passed']
result={'passed':True,'characterOriginalAndCutoutRGBUnchanged':True,'priorReviewsAndSourceUnchanged':True,'bayRows':rows,'wholeEnvironmentChange':changes,'blackBorderHoles':False,'note':'Pixel differences establish broad edit coverage, NOT subjective stylistic approval. Counts beyond bay lines were visually inspected and source-checked separately.'}
(P/'artifact-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
