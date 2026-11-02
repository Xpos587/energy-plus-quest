# Align a v10 restyle onto its Blender render and put the crisp Blender text back.
#   uv run --with opencv-python-headless --with numpy --with pillow python compose.py NAME W H
#   .tmp-work/v17/bl/NAME{,-notext}.png + gen/NAME.png -> gen/NAME-final.png
import subprocess
import sys
from pathlib import Path

import json

import cv2
import numpy as np

n, W, H = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
here = Path(__file__).parent
HEADS = json.loads((here / "manifest-wide-outcomes.json").read_text())["outcomes"]["keeper"]["story"]["heads"]  # 1960x840 px
w = here.parents[2] / ".tmp-work/wh3d"
g = lambda s: str(w / f"gen/{n}{s}")
rd = lambda p: cv2.resize(cv2.imread(str(p)), (W, H), interpolation=cv2.INTER_AREA)
txt, bare = rd(w / f"bl/{n}.png"), rd(w / f"bl/{n}-notext.png")
cv2.imwrite(g("-ref.png"), bare)
subprocess.run([sys.executable, str(here.parent / "blender-v1/align.py"), g("-ref.png"), g(".png"), g("-al.png"), g("-ov.jpg")], check=True)
gen = cv2.imread(g("-al.png")).astype(np.float32)
txt, bare = txt.astype(np.float32), bare.astype(np.float32)
# Text mask = where the render with text differs from the render without it.
a = np.clip(np.abs(txt - bare).max(axis=2) / 60.0, 0, 1)
a = cv2.GaussianBlur(cv2.dilate(a, np.ones((3, 3), np.uint8)), (0, 0), 0.6)
# The restyle blanks the WMS screen; put the rendered chart back (hull of the
# largest screen-coloured #16324F blob, BGR here).
scr = (np.abs(txt - np.array([0x4F, 0x32, 0x16])).max(axis=2) < 14).astype(np.uint8)
k, lab, st, _ = cv2.connectedComponentsWithStats(scr)
if k > 1:
    big = 1 + int(np.argmax(st[1:, 4]))
    if st[big, 4] > 30:
        hull = np.zeros(scr.shape, np.uint8)
        cv2.fillConvexPoly(hull, cv2.convexHull(cv2.findNonZero((lab == big).astype(np.uint8))), 1)
        a = np.maximum(a, cv2.GaussianBlur(hull.astype(np.float32), (3, 3), 0))
out = gen * (1 - a[..., None]) + txt * a[..., None]
out = out.clip(0, 255).astype(np.uint8)
if n == "outcome-keeper":
    from PIL import Image, ImageDraw, ImageFont
    im = Image.fromarray(out[..., ::-1])
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("/usr/share/fonts/TTF/RobotoCondensed-Bold.ttf", 56)
    for (x, y), (dx, dy) in zip(HEADS, ((45, -5), (6, -55))):  # projected heads; offsets keep clear of the banners
        d.text((x + dx, y + dy), "?", font=f, fill="#F26B2B", stroke_width=5, stroke_fill="white", anchor="mb")
    out = np.asarray(im)[..., ::-1]
cv2.imwrite(g("-final.png"), out)
print(n, "text px", int((a > 0.5).sum()))
