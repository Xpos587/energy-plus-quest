"""Source-named check of this reviewed image, not a general AI-art validator."""
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image
from dock_layout import DOORS, BOUNDARIES
P = Path(__file__).resolve().parent
image = Path(sys.argv[1]) if len(sys.argv) > 1 else P/'map.jpg'
pixels = np.asarray(Image.open(image).convert('RGB'))
assert pixels.shape == (1000,1440,3)
assert len(BOUNDARIES) == len(DOORS) + 1 == 7
for i, door in enumerate(DOORS):
    assert abs((BOUNDARIES[i] + BOUNDARIES[i+1])/2 - door) < 1e-8
# Door centers manually located on the full-resolution final painting.
gate_centers = [399,433.5,468,502.5,537,571.5]
rows = []
for y in [405,412,420]:
    white = pixels[y-1:y+2,365:605].mean(axis=0).min(axis=1) > 220
    runs = []; start = None
    for x, visible in enumerate([*white,False]):
        if visible and start is None: start = x
        if not visible and start is not None:
            runs.append((365+start,365+x-1)); start = None
    assert len(runs) == 7, f'{y}: expected 7 painted boundaries, got {runs}'
    lines = [(left+right)/2 for left,right in runs]
    for i, door in enumerate(gate_centers):
        fraction = (door-lines[i])/(lines[i+1]-lines[i])
        assert .4 < fraction < .66, (y,i,fraction)
    rows.append({'y':y,'lineCenters':lines})
result = {'passed':True,'sourceDoors':6,'sourceBoundaries':7,'paintedBoundaries':7,'doorCentersAreBetweenLines':True,'image':image.name,'rows':rows,'manualBasis':'Door centers inspected in dock-inspect.jpg; small perspective slant allowed.'}
(P/'dock-check.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
