"""Small runnable structural gate: python evidence-check.py EVIDENCE STRUCTURE.
Requires the existing Pillow/numpy/OpenCV environment, no new dependencies.
"""
import json, sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

root, structure = map(Path, sys.argv[1:3])
meta = json.loads((root / 'passes.json').read_text())
report = {}
for fmt, camera in meta['cameras'].items():
    pixels = np.asarray(Image.open(root / f'{fmt}-id.png').convert('RGB'))
    assert list(pixels.shape[1::-1]) == camera['size']
    report[fmt] = {}
    for group, rgba in meta['ids'].items():
        color = np.array([round(255 * (12.92*c if c <= .0031308 else 1.055*c**(1/2.4)-.055)) for c in rgba[:3]])
        yy, xx = np.where(np.max(abs(pixels.astype(int) - color), axis=2) < 4)
        assert len(xx) > 100, (fmt, group, 'not visibly rendered')
        box = [int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1]
        assert box[0] > 0 and box[1] > 0 and box[2] < pixels.shape[1] and box[3] < pixels.shape[0], (fmt,group,'clipped')
        report[fmt][group] = {'visible':True,'visible_pixels':len(xx),'visible_bounds':box}
    beauty = cv2.imread(str(structure / f'{fmt}-arseniy.png'))
    cv2.imwrite(str(root / f'{fmt}-edges.png'), cv2.Canny(beauty,70,150))
(root / 'visibility.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
