# Put the composed maps into outpainted canvases so the camera can cover any stage
# without grey bands: wide 1672x941 -> 1672x1393 (+226 top), tall 1024x1536 -> 1280x1536 (+128 left).
#   python3 compose.py && python3 extend.py -> gen/{fmt}-{who}-ext.png
# gen/ext-{wide,tall}.png = p-extend*.txt edits of gen/pad-{wide,tall}.png (base with grey bands).
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

here = Path(__file__).parent / "gen"
SHIFT = {"wide": (0, 226, 1672, 1393), "tall": (128, 0, 1280, 1536)}
for fmt, (ox, oy, W, H) in SHIFT.items():
    ext = Image.open(here / f"ext-{fmt}.png").convert("RGB").resize((W, H), Image.LANCZOS)
    for who in ("alva", "khor", "arseniy"):
        mid = Image.open(here / f"{fmt}-{who}.png").convert("RGB")
        w, h = mid.size
        mask = Image.new("L", (W, H))
        # Feather 12px into the original only on the sides that border the outpaint.
        ImageDraw.Draw(mask).rectangle((ox + (12 if ox else 0), oy + (12 if oy else 0), ox + w - (12 if ox else 0), oy + h - (12 if oy else 0)), fill=255)
        out = ext.copy()
        out.paste(mid, (ox, oy), mask.filter(ImageFilter.GaussianBlur(8)).crop((ox, oy, ox + w, oy + h)))
        out.save(here / f"{fmt}-{who}-ext.png")
