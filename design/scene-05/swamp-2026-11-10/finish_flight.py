# Paste the reference-livery Mi-8 (gen/hf-h7-fl-{boat,parcel}.png) into the four revision-13 flight screens
# and write public/scene-art/lastmile-family-v1/revision-18/flight-{boat,parcel}[-arseniy]-tall.webp.
#   uv run --with pillow python finish_flight.py
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
here = Path(__file__).parent; root = here.parents[2]
SRC = root / "public/scene-art/lastmile-family-v1/revision-13"
OUT = root / "public/scene-art/lastmile-family-v1/revision-18"; OUT.mkdir(exist_ok=True)
X, Y, W, H = 250, 500, 1244, 700
DOOR = (612, 252, 728, 338)
MASK = (40, 40, 1130, 420)  # helicopter only; sling and load below stay untouched
for gift in ("boat", "parcel"):
    ai = Image.open(here / f"gen/hf-h7-fl-{gift}.png").convert("RGB").resize((W, H), Image.LANCZOS)
    for suffix in ("", "-arseniy"):
        name = f"flight-{gift}{suffix}-tall.webp"
        base = Image.open(SRC / name).convert("RGB")
        full = base.copy(); full.paste(ai, (X, Y))
        m = Image.new("L", base.size); ImageDraw.Draw(m).rectangle((X + MASK[0], Y + MASK[1], X + MASK[2], Y + MASK[3]), fill=255)
        old = base.copy()
        base.paste(full, (0, 0), m.filter(ImageFilter.GaussianBlur(18)))
        d = Image.new("L", base.size); ImageDraw.Draw(d).rectangle((X + DOOR[0], Y + DOOR[1], X + DOOR[2], Y + DOOR[3]), fill=255)
        base.paste(old, (0, 0), d.filter(ImageFilter.GaussianBlur(3)))  # keep the original cargo door + gift exactly
        base.save(OUT / name, quality=86, method=6); print(name)
