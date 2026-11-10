# Patch the bog-on-the-trail into the rev-17 map (soft mask, vehicles/heli/ABK untouched) and write
# public/scene-art/lastmile-family-v1/revision-18/choice-{wide,tall}-{alva,khor,arseniy}.webp.
#   uv run --with pillow python finish_trail.py
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
here = Path(__file__).parent; root = here.parents[2]
R17 = root / "public/scene-art/lastmile-family-v1/revision-17"
OUT = root / "public/scene-art/lastmile-family-v1/revision-18"; OUT.mkdir(exist_ok=True)
# crop (x, y, w, h) in the full canvas, mask rectangle inside the crop, AI result
EDITS = {"wide": ("t-trail-wide", (1800, 1500, 1500, 844), (380, 200, 950, 560)),
         "tall": (sys.argv[1] if len(sys.argv) > 1 else "t2-trail-tall", (1100, 1350, 1500, 844), (120, 180, 700, 560))}
for f, (name, (x, y, w, h), (a, b, c, d)) in EDITS.items():
    ai = Image.open(here / f"gen/hf-{name}.png").convert("RGB").resize((w, h), Image.LANCZOS)
    m = Image.new("L", (w, h)); ImageDraw.Draw(m).rectangle((a, b, c, d), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(24))
    for who in ("alva", "khor", "arseniy"):
        img = Image.open(R17 / f"choice-{f}-{who}.webp").convert("RGB")
        img.paste(ai, (x, y), m)
        img.save(OUT / f"choice-{f}-{who}.webp", quality=86, method=6)
        if who == "arseniy": img.save(here / f"gen/final18-{f}-arseniy.png")
    print(f, "ok")
