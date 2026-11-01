# Paste the recipient edits (Mayma for alva, Khabt for khor) back into the Arseniy base.
#   python3 compose.py   -> gen/{wide,tall}-{alva,khor,arseniy}.png
# Each edit redraws a destination crop; only the rectangle around the changed people is
# pasted back (feathered), so the rest of the base stays bit-identical.
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

here = Path(__file__).parent / "gen"
CROPS = {"wide": ("wide-base.png", (1042, 0, 630, 420)), "tall": ("tall-2.png", (424, 20, 600, 400))}

for fmt, (src, (x, y, w, h)) in CROPS.items():
    base = Image.open(here / src).convert("RGB")
    base.save(here / f"{fmt}-arseniy.png")
    crop = np.asarray(base.crop((x, y, x + w, y + h))).astype(int)
    for who in ("alva", "khor"):
        edit = Image.open(here / f"dest-{fmt}-{who}.png").convert("RGB").resize((w, h), Image.LANCZOS)
        diff = np.abs(np.asarray(edit).astype(int) - crop).sum(2)
        # People live on the left half of the crop (the worker and the new recipient).
        ys, xs = np.nonzero(diff[:, : w * 3 // 5] > 350)
        box = (max(xs.min() - 18, 0), max(ys.min() - 18, 0), xs.max() + 18, min(ys.max() + 18, h))
        mask = Image.new("L", (w, h))
        ImageDraw.Draw(mask).rectangle(box, fill=255)
        out = base.copy()
        out.paste(edit, (x, y), mask.filter(ImageFilter.GaussianBlur(6)))
        out.save(here / f"{fmt}-{who}.png")
        print(fmt, who, "box", [b + o for b, o in zip(box, (x, y, x, y))])
