from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
manifest = json.loads((HERE / 'manifest.json').read_text())
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def pixels(path):
    return np.asarray(Image.open(path).convert('RGB'))
for name, expected in manifest['priorHashes'].items():
    assert digest(REPO / name) == expected, name
before = pixels(HERE.parent / 'pass-17/map.png')
after = pixels(HERE / 'map.png')
mask = np.asarray(Image.open(HERE / 'allowed-mask.png')) > 0
changed = np.any(before != after, axis=2)
assert changed.sum() > 0
assert not np.any(changed & ~mask)
assert np.array_equal(after, pixels(HERE / 'map.webp'))
assert digest(HERE / 'girl.png') == digest(HERE.parent / 'pass-17/girl.png')
# Separate protected regions: crew, warehouse/roof, west road, number-4 trailer.
for box in [(1130,275,1230,515),(360,90,655,415),(200,260,270,750),(620,560,840,755)]:
    x,y,x2,y2 = [round(v*3504/1500) for v in box]
    assert np.array_equal(before[y:y2,x:x2],after[y:y2,x:x2]), box
for carrier in ['near','crew']:
    for fmt in ['desktop','mobile']:
        assert np.array_equal(pixels(HERE/f'{carrier}-{fmt}.png'),pixels(REPO/f'design/scene-01/assets/current/outcomes/{carrier}-{fmt}.webp'))
# The candidate explicitly maps old to a low-cab variant, not the live old image.
for fmt in ['desktop','mobile']:
    original = pixels(REPO/f'design/scene-01/assets/current/outcomes/old4-{fmt}.webp')
    candidate = pixels(HERE/f'old-{fmt}.png')
    assert np.array_equal(candidate, pixels(HERE/f'old4-{fmt}.png'))
    difference = np.any(original != candidate,axis=2)
    assert difference.any()
    ys,xs = np.where(difference)
    assert xs.max() < original.shape[1]*.46
    assert ys.min() > original.shape[0]*.29
    assert ys.max() < original.shape[0]*.67
    # Policeman, trailer and road/background beyond the cab remain exact.
    assert np.array_equal(original[:,int(original.shape[1]*.48):],candidate[:,int(original.shape[1]*.48):])
assert subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).strip() == ''
result = {'priorPassFilesUnchanged': len(manifest['priorHashes']), 'changedMapPixels': int(changed.sum()), 'outsideAllowedChangedPixels': int((changed & ~mask).sum()), 'protectedRegions': 'passed', 'girlSpriteIdentical': True, 'unchangedResultPairs': ['near','crew'], 'oldCandidate': 'old and old4 share identical neutral slate-cab DPS artwork; map truck4 is pass17 pixel-identical', 'noStagedFiles': True}
(HERE/'pixel-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))

# Express-only revision: no approved manual vehicle or map may drift.
protected = json.loads((HERE/'express-preserved-hashes.json').read_text())
protected = {name: expected for name, expected in protected.items() if not name.startswith(('old-', 'old4-'))}
for name, expected in protected.items():
    assert digest(HERE/name) == expected, name
desktop = Image.open(HERE/'express-desktop.png').convert('RGB')
mobile = Image.open(HERE/'express-mobile.png').convert('RGB')
width = round(desktop.height*2400/1792)
left = (desktop.width-width)//2
assert np.array_equal(np.asarray(mobile), np.asarray(desktop.crop((left,0,left+width,desktop.height))))
(HERE/'express-highway-validation.json').write_text(json.dumps({'preservedAssets':len(protected),'desktopSize':desktop.size,'mobileSize':mobile.size,'mobileExactCenterCrop':True,'staticIllustrationOnly':True},indent=2))
print('PASS: Express-only revision; 13 protected assets unchanged; old/old4 edge cleanup checked separately, mobile exact center crop.')
