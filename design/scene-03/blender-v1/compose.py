# Put the crisp Blender lettering back onto the aligned GPT restyle.
# Text mask = where the render with text differs from the render without it.
#   python3 compose.py NAME   (out/NAME.png, out/NAME-notext.png, gen/NAME-al.png -> gen/NAME-final.png)
import sys

import numpy as np
from PIL import Image, ImageFilter

n = sys.argv[1]
txt = np.asarray(Image.open(f"out/{n}.png").convert("RGB")).astype(np.float32)
bare = np.asarray(Image.open(f"out/{n}-notext.png").convert("RGB")).astype(np.float32)
gen = np.asarray(Image.open(f"gen/{n}-al.png").convert("RGB")).astype(np.float32)
d = np.abs(txt - bare).max(axis=2)
a = np.clip(d / 60.0, 0, 1)
a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.6))) / 255.0
# The restyle blanks the WMS screen; put the rendered chart back (hull of the
# largest screen-coloured #16324F blob).
import cv2
scr = (np.abs(txt - np.array([0x16, 0x32, 0x4F])).max(axis=2) < 14).astype(np.uint8)
k, lab, st, _ = cv2.connectedComponentsWithStats(scr)
if k > 1:
    big = 1 + int(np.argmax(st[1:, 4]))
    pts = cv2.findNonZero((lab == big).astype(np.uint8))
    hull = np.zeros(scr.shape, np.uint8)
    cv2.fillConvexPoly(hull, cv2.convexHull(pts), 1)
    a = np.maximum(a, cv2.GaussianBlur(hull.astype(np.float32), (3, 3), 0))
out = gen * (1 - a[..., None]) + txt * a[..., None]
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(f"gen/{n}-final.png")
print(n, "text px", int((a > 0.5).sum()))
