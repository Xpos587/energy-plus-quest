"""Small dependency-free (apart from existing Pillow/NumPy) artifact regression check."""
from pathlib import Path
from PIL import Image
import json,hashlib
import numpy as np
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
original=ROOT/'design/scene-01/assets/current/choices/professional.webp'
assert (P/'professional.webp').read_bytes()==original.read_bytes()
assert np.array_equal(np.array(Image.open(P/'professional-cutout.png'))[:,:,:3],np.array(Image.open(original).convert('RGB')))
manifest=json.loads((P/'manifest.json').read_text())
images=[]
for key in 'abc':
    path=P/f'map-{key}.jpg';image=np.array(Image.open(path).convert('RGB'))
    assert image.shape==(1000,1440,3)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['variants'][key]['sha256']
    assert (image[:8].max(axis=2)>20).all() and (image[-8:].max(axis=2)>20).all(),'Registration left black edge holes'
    assert json.loads((P/f'dock-check-{key}.json').read_text())['paintedBoundaries']==7
    images.append(image)
# Drawing is genuinely different on architecture, while crew placement stays common.
for a,b in zip(images,images[1:]):
    assert np.abs(a[110:275,385:606].astype(float)-b[110:275,385:606]).mean()>5
    assert np.max(np.abs(a[436:487,1130:1175].astype(int)-b[436:487,1130:1175]))==0
assert json.loads((P/'scene-check.json').read_text())['passed']
assert json.loads((P/'geometry-check.json').read_text())['openGateMeters']==9.3
print('PASS: three different painted variants; identical crew; no black borders; original character bytes and cutout RGB; 6/7 docks; source and fence evidence')
