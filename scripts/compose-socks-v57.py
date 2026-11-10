"""Compose the v57 socks results from the existing illustrated spill.

Two pairs everywhere: cream/blue Nordic and red/grey stripes. Secured boxes use
one 124x44 sprite, sit on the cloth/stack/floor, and have the strap IN FRONT.
No added drop shadows. Run:
  uv run --with pillow --with numpy --with scipy python scripts/compose-socks-v57.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "public/compact-art"
SRC = ROOT / "design/compact-socks-v57"
ENV = Image.open(ART / "compact-environment-v53-portrait.png").convert("RGBA")
SPILL = Image.open(SRC / "place1-box.png").convert("RGBA")
BOX_W, BOX_H = 124, 44
P1_CROP = (90, 400, 570, 720)
# Outlines in a 1000px-wide view of the source. Reuse the actual illustrated
# socks rather than painting different patterns for the secured/loose states.
NORDIC_PAIR = [(195, 275), (214, 264), (224, 264), (238, 256), (246, 259),
    (252, 266), (251, 270), (269, 285), (277, 287), (312, 292), (327, 296),
    (339, 303), (343, 313), (342, 323), (336, 330), (323, 334), (293, 334),
    (300, 346), (304, 359), (303, 369), (298, 377), (289, 383), (279, 383),
    (264, 377), (239, 356), (225, 347), (216, 348), (207, 340), (202, 324),
    (198, 307), (195, 294)]
RED_SOCK = [(355, 311), (356, 305), (361, 296), (373, 284), (382, 282),
    (392, 285), (406, 291), (424, 298), (442, 300), (462, 298), (483, 296),
    (495, 298), (502, 303), (506, 310), (505, 320), (500, 328), (491, 334),
    (472, 338), (451, 341), (433, 348), (421, 351), (411, 348), (394, 338),
    (382, 333), (366, 326), (357, 321)]


def cutout(points):
    mask = Image.new("L", SPILL.size)
    ImageDraw.Draw(mask).polygon([(round(x * SPILL.width / 1000),
                                  round(y * SPILL.width / 1000)) for x, y in points], fill=255)
    image = SPILL.copy()
    image.putalpha(mask.filter(ImageFilter.GaussianBlur(0.6)))
    return image.crop(image.getbbox())


def fit_height(image, height):
    return image.resize((round(image.width * height / image.height), height), Image.Resampling.LANCZOS)


def build_box():
    k = 6
    w, h = BOX_W * k, BOX_H * k
    face, edge, ink, inner = (240, 176, 107), (204, 142, 85), (96, 58, 28), (110, 70, 40)
    image = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 4 * k, fill=ink)
    d.rounded_rectangle((k, k, w - k - 1, h - k - 1), 3 * k, fill=face)
    d.rounded_rectangle((k, h - 5 * k, w - k - 1, h - k - 1), 3 * k, fill=edge)
    d.rectangle((k, k, w - k - 1, h - 6 * k), fill=face)
    d.rectangle((w // 2 - 4 * k, k, w // 2 + 4 * k, 3 * k), fill=(251, 218, 187))
    d.rectangle((5 * k, 3 * k, w - 5 * k, h - 4 * k), fill=ink)
    d.rectangle((6 * k, 4 * k, w - 6 * k, h - 5 * k), fill=inner)
    # A real two-sock Nordic pair, and two identical striped socks with offset
    # cuffs/toes so the second sock remains visible rather than merging into one.
    nordic = fit_height(cutout(NORDIC_PAIR), 34 * k)
    red = fit_height(cutout(RED_SOCK).rotate(-42, Image.Resampling.BICUBIC, expand=True), 31 * k)
    image.alpha_composite(nordic, (10 * k, 4 * k))
    image.alpha_composite(red, (69 * k, 4 * k))
    image.alpha_composite(red, (78 * k, 8 * k))
    return image.resize((BOX_W, BOX_H), Image.Resampling.LANCZOS)


def strap_layer(bounds, buckle):
    """Keep the band and complete metal buckle, without the blue wall/shadow."""
    pixels = np.asarray(ENV.crop(bounds).convert("RGB")).astype(int)
    red = (pixels[..., 0] > 150) & (pixels[..., 1] < 110) & (pixels[..., 2] < 110)
    assert red.any(), f"No strap in {bounds}"
    edge = nd.binary_dilation(red, iterations=2) & (pixels.mean(-1) < 170)
    mask = Image.fromarray(((red | edge) * 255).astype(np.uint8))
    ImageDraw.Draw(mask).rounded_rectangle(buckle, radius=1, fill=255)
    layer = ENV.crop(bounds)
    layer.putalpha(mask)
    return layer


def place1():
    """Keep the accepted damaged box/Nordic pair; replace the odd green sock."""
    x0, y0, x1, y1 = P1_CROP
    generated = SPILL.resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    g = np.asarray(generated.convert("RGB")).astype(int)
    e = np.asarray(ENV.crop(P1_CROP).convert("RGB")).astype(int)
    changed = nd.binary_opening(np.abs(g - e).sum(-1) > 60)
    region = np.zeros_like(changed)
    region[20:196, 5:250] = True  # damaged box, both Nordic socks, first red sock
    mask = Image.fromarray((nd.binary_dilation(changed & region, iterations=4) * 255).astype(np.uint8))
    result = ENV.copy()
    result.paste(generated, (x0, y0), mask.filter(ImageFilter.GaussianBlur(1.5)))
    # The fourth sock is the SAME striped sock, lying on the neighbouring cloth.
    loose = cutout(RED_SOCK).rotate(165, Image.Resampling.BICUBIC, expand=True)
    loose = loose.resize((72, round(loose.height * 72 / loose.width)), Image.Resampling.LANCZOS)
    result.alpha_composite(loose, (368, 604))
    return result


def main():
    box = build_box()
    # One box/sock arrangement, varying only its location and the existing strap.
    jobs = [
        ("socks-zone2-v57.png", (466, 621), (355, 565, 575, 602), (90, 12, 118, 33), 0),
        ("socks-zone3-secured-v57.png", (657, 478), (590, 436, 724, 475), (56, 15, 82, 35), 0),
        ("socks-zone4-v57.png", (972, 718), (902, 606, 1044, 650), (76, 11, 101, 30), 66),
    ]
    assert box.size == (124, 44)
    for name, (cx, bottom), strap, buckle, dy in jobs:
        result = ENV.copy()
        x0, y0, x1, y1 = strap
        if dy:
            # Empty wall between the two original straps replaces the old lower
            # strap; its mounts and band are relocated to the floor-level box.
            result.paste(ENV.crop((x0, y0 - 56, x1, y1 - 56)), (x0, y0))
            result.paste(ENV.crop(strap), (x0, y0 + dy))
        x, y = cx - BOX_W // 2, bottom - BOX_H
        assert y >= 430 and bottom <= 718 and x + BOX_W < 1046
        result.alpha_composite(box, (x, y))
        layer = strap_layer(strap, buckle)
        result.alpha_composite(layer, (x0, y0 + dy))
        # Runnable guard: the foreground strap pixels must survive compositing.
        opaque = np.asarray(layer.getchannel("A")) == 255
        actual = np.asarray(result.crop((x0, y0 + dy, x1, y1 + dy)))
        assert np.array_equal(actual[opaque], np.asarray(layer)[opaque])
        result.convert("RGB").save(ART / name, optimize=True)
        print(name, box.size, "strap in front")
    place1().convert("RGB").save(ART / "socks-zone1-unsecured-v57.png", optimize=True)
    print("socks-zone1-unsecured-v57.png: two matching pairs")


if __name__ == "__main__":
    main()
