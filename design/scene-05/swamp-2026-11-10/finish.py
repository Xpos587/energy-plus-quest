# Step 2-4: paste Higgsfield helicopter + ABK edits into gen/base-*.png, transplant the recipient people
# from revision-12, write public/scene-art/lastmile-family-v1/revision-17/choice-{wide,tall}-{alva,khor,arseniy}.webp.
#   uv run --with pillow --with numpy python finish.py
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
here = Path(__file__).parent
root = here.parents[2]
R12 = root / "public/scene-art/lastmile-family-v1/revision-12"
OUT = root / "public/scene-art/lastmile-family-v1/revision-17"; OUT.mkdir(exist_ok=True)
# name: (x, y, w, h) crop in the full canvas, mask rectangle inside the crop (None = whole crop)
EDITS = {
    "wide": [("h4-heli-wide", (430, 1410, 896, 504), (20, 20, 876, 484)), ("f-abk-wide", (2350, 1130, 1400, 788), (0, 0, 1130, 600))],
    "tall": [("h4-heli-tall", (740, 1830, 896, 504), (20, 20, 876, 484)), ("f-abk-tall", (1300, 560, 1400, 788), (0, 0, 1130, 600))],
}
PEOPLE = {"wide": {"alva": (2651, 1492, 2965, 1754), "khor": (2651, 1491, 3031, 1760)},
          "tall": {"alva": (1605, 975, 1843, 1191), "khor": (1604, 967, 2088, 1349)}}
def paste(base, patch, box, blur):
    m = Image.new("L", base.size); ImageDraw.Draw(m).rectangle(box, fill=255)
    base.paste(patch, (0, 0), m.filter(ImageFilter.GaussianBlur(blur)))
for f in ("wide", "tall"):
    base = Image.open(here / f"gen/base-{f}.png").convert("RGB")
    for name, (x, y, w, h), (mx0, my0, mx1, my1) in EDITS[f]:
        ai = Image.open(here / f"gen/hf-{name}.png").convert("RGB").resize((w, h), Image.LANCZOS)
        full = base.copy(); full.paste(ai, (x, y))
        paste(base, full, (x + mx0, y + my0, x + mx1, y + my1), 18)
    base.save(here / f"gen/final-{f}-arseniy.png")
    base.save(OUT / f"choice-{f}-arseniy.webp", quality=86, method=6)
    for who, (x0, y0, x1, y1) in PEOPLE[f].items():
        old = Image.open(R12 / f"choice-{f}-{who}.webp").convert("RGB")
        img = base.copy(); m = Image.new("L", base.size); ImageDraw.Draw(m).rectangle((x0 - 12, y0 - 12, x1 + 12, y1 + 12), fill=255)
        img.paste(old, (0, 0), m.filter(ImageFilter.GaussianBlur(8)))
        img.save(here / f"gen/final-{f}-{who}.png"); img.save(OUT / f"choice-{f}-{who}.webp", quality=86, method=6)
    print(f, "ok")
