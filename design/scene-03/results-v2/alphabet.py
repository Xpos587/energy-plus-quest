# The three alphabet outcomes differ only in the aisle plaque (x 1055-1108, y 234-257 of 1999x786).
# One restyle (camera) is the base for all three, so the scene is identical; each plaque comes
# from its own aligned restyle with a feathered patch.  python3 alphabet.py GEN_DIR
import sys
from PIL import Image, ImageDraw, ImageFilter

g = sys.argv[1]
base = Image.open(f"{g}/al-alphabet-camera.png").convert("RGB")
box = (1030, 215, 1135, 278)
mask = Image.new("L", base.size)
ImageDraw.Draw(mask).rectangle((box[0] + 6, box[1] + 6, box[2] - 6, box[3] - 6), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(3))
for n in ("boat", "camera", "socks"):
    out = base.copy()
    out.paste(Image.open(f"{g}/al-alphabet-{n}.png").convert("RGB"), (0, 0), mask)
    out.save(f"{g}/fin-alphabet-{n}.png")
