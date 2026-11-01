# v9.2 canvas: grow the v9.1 outpainted maps on every side so the camera can always cover the stage
# (no bands at any viewport) while the framed objects still fit.
#   wide 1672x1393 -> 2056x1841 at +192+352, tall 1280x1536 -> 1664x1952 at +192+288.
#   python3 extend2.py pad      -> gen/pad2-{wide,tall}.png (grey bands, model size)
#   p-extend2*.txt edits of pad2 -> gen/ext2-{wide,tall}.png
#   python3 extend2.py compose  -> gen/{fmt}-{who}-ext2.png (1x), upscale those to gen/*-ext2-up.png (4x RealESRGAN)
#   python3 extend2.py final    -> gen/{fmt}-{who}-ext2-2x.png: upscale + the unchanged v9.1 2x pixels pasted back.
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

Image.MAX_IMAGE_PIXELS = None
here = Path(__file__).parent / "gen"
GROW = {"wide": (192, 352, 2056, 1841, (1328, 1184)), "tall": (192, 288, 1664, 1952, (1184, 1392))}
WHO = ("alva", "khor", "arseniy")


def feather(size, box, blur):
    mask = Image.new("L", size)
    ImageDraw.Draw(mask).rectangle(box, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(blur))


step = sys.argv[1]
for fmt, (ox, oy, W, H, model) in GROW.items():
    if step == "pad":
        pad = Image.new("RGB", (W, H), (128, 128, 128))
        pad.paste(Image.open(here / f"{fmt}-alva-ext.png").convert("RGB"), (ox, oy))
        pad.resize(model, Image.LANCZOS).save(here / f"pad2-{fmt}.png")
    elif step == "compose":
        ext = Image.open(here / f"ext2-{fmt}.png").convert("RGB").resize((W, H), Image.LANCZOS)
        for who in WHO:
            mid = Image.open(here / f"{fmt}-{who}-ext.png").convert("RGB")
            w, h = mid.size
            out = ext.copy()
            out.paste(mid, (ox, oy), feather((W, H), (ox + 16, oy + 16, ox + w - 16, oy + h - 16), 10).crop((ox, oy, ox + w, oy + h)))
            out.save(here / f"{fmt}-{who}-ext2.png")
    elif step == "final":
        for who in WHO:
            up = Image.open(here / f"{fmt}-{who}-ext2-up.png").convert("RGB").resize((W * 2, H * 2), Image.LANCZOS)
            mid = Image.open(here / f"{fmt}-{who}-ext-2x.png").convert("RGB")
            w, h = mid.size
            up.paste(mid, (ox * 2, oy * 2), feather(up.size, (ox * 2 + 48, oy * 2 + 48, ox * 2 + w - 48, oy * 2 + h - 48), 16).crop((ox * 2, oy * 2, ox * 2 + w, oy * 2 + h)))
            up.save(here / f"{fmt}-{who}-ext2-2x.png")
