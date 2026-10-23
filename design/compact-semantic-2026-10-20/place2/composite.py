"""Stitch a generated cargo panel into the existing result, preserving exterior."""
import sys
from pathlib import Path
from PIL import Image, ImageChops

kind, generated = sys.argv[1:]
root = Path(__file__).resolve().parents[3]
original_name = {"camera": "camera-zone2-v36.png", "socks": "socks-zone2-v37.png", "boat": "boat-zone2-dishes-v46.png"}[kind]
original = Image.open(root / "public/compact-art" / original_name).convert("RGBA")
patch = Image.open(generated).convert("RGBA").resize((510, 330), Image.Resampling.LANCZOS)
out = original.copy()
out.paste(patch, (80, 410))
if kind == "boat":
    # Explicitly authorized cleanup of the old boat beyond the master crop.
    sibling = Image.open(root / "public/compact-art/boat-zone3-v32.png").convert("RGBA")
    wall = sibling.crop((571, 487, 575, 617)).resize((26, 158), Image.Resampling.BICUBIC)
    out.paste(wall, (590, 487))
assert out.size == original.size == (1368, 1149)
outside = ImageChops.difference(original.convert("RGB"), out.convert("RGB"))
outside.paste((0, 0, 0), (80, 410, 590, 740))
if kind == "boat":
    outside.paste((0, 0, 0), (590, 487, 616, 645))
assert outside.getbbox() is None, "Exterior changed"
patch.save(Path(__file__).parent / f"{kind}-panel.png")
destination = root / "public/compact-art" / f"{kind}-zone2-v53.png"
out.save(destination)
print(f"PASS {destination}: exterior unchanged, panel (80,410,510,330)")
