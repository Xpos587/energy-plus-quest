"""Prepare bounded per-carrier Comfy inputs from Blender RGBA cutouts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from PIL import Image


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cutouts", type=Path, required=True)
    p.add_argument("--layout", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    layout = json.loads(a.layout.read_text())
    out = a.output
    for viewport, vp in layout["viewports"].items():
        w, h = vp["size"]
        for carrier, vehicle in vp["vehicles"].items():
            bounds = vehicle["bounds"]
            left, top, right, bottom = (bounds[i] * (w if i % 2 == 0 else h) for i in range(4))
            pad_x = max(32, (right - left) * 0.65)
            pad_y = max(32, (bottom - top) * 0.9)
            box = (
                max(0, int(left - pad_x)),
                max(0, int(top - pad_y)),
                min(w, int(right + pad_x)),
                min(h, int(bottom + pad_y)),
            )
            source = Image.open(a.cutouts / viewport / f"{carrier}-color.png").convert("RGBA")
            mask = Image.open(a.cutouts / viewport / f"{carrier}-id.png").convert("L")
            crop = source.crop(box)
            crop_mask = mask.crop(box)
            canvas = Image.new("RGBA", crop.size, (204, 216, 222, 255))
            canvas.alpha_composite(crop)
            target = out / viewport / carrier
            target.mkdir(parents=True, exist_ok=True)
            canvas.convert("RGB").save(target / "input.png")
            crop_mask.save(target / "id.png")
            (target / "crop.json").write_text(json.dumps({"box": box, "size": list(crop.size), "source": str(source)}, indent=2) + "\n")


if __name__ == "__main__":
    main()
