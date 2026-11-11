"""Camera review candidate: same cardboard insert/camera in all secured places.

Reuse the actual camera from the existing fallen outcome (which stays unchanged)
and the approved socks restraint extraction. No image-generation request.
Run: uv run --with pillow --with numpy --with scipy python scripts/compose-camera-v54.py
"""
import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "public/compact-art"
spec = importlib.util.spec_from_file_location("socks", ROOT / "scripts/compose-socks-v57.py")
socks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(socks)
ENV = socks.ENV
BOX_W, BOX_H = 124, 44


def build_box():
    source = Image.open(ART / "camera-zone1-fallen-v53.png").convert("RGBA")
    mask = Image.new("L", source.size)
    ImageDraw.Draw(mask).polygon([
        (373, 601), (378, 598), (384, 598), (386, 595), (393, 595),
        (399, 600), (401, 603), (411, 606), (419, 611), (424, 618),
        (424, 625), (419, 629), (413, 629), (405, 625), (396, 624),
        (387, 623), (379, 619), (373, 614),
    ], fill=255)
    pixels = np.asarray(source).astype(int)
    # Remove residual cardboard/blue cloth along the hand-traced camera edge.
    dark_body = (pixels[..., :3].max(-1) < 170) & (pixels[..., 0] < 150)
    dark_body &= (pixels[..., 0] < 90) | (pixels[..., 0] < 1.35 * pixels[..., 2])
    components, count = socks.nd.label((np.asarray(mask) > 0) & dark_body)
    assert count, "Camera mask is empty"
    largest = np.bincount(components.ravel())[1:].argmax() + 1
    opaque = socks.nd.binary_fill_holes(components == largest)
    mask = Image.fromarray((opaque * 255).astype(np.uint8))
    source.putalpha(mask.filter(ImageFilter.GaussianBlur(0.4)))
    # Level the fallen camera for its secured pose; keep the same body/lens.
    camera = source.crop(source.getbbox()).rotate(25, Image.Resampling.BICUBIC, expand=True)
    camera = camera.crop(camera.getbbox())
    k = 6
    w, h = BOX_W * k, BOX_H * k
    image = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(image)
    # Same compact cardboard construction as the approved socks package.
    d.rounded_rectangle((0, 0, w - 1, h - 1), 4 * k, fill=(96, 58, 28))
    d.rounded_rectangle((k, k, w - k - 1, h - k - 1), 3 * k, fill=(240, 176, 107))
    d.rounded_rectangle((k, h - 5 * k, w - k - 1, h - k - 1), 3 * k, fill=(204, 142, 85))
    d.rectangle((k, k, w - k - 1, h - 6 * k), fill=(240, 176, 107))
    d.rectangle((w // 2 - 4 * k, k, w // 2 + 4 * k, 3 * k), fill=(251, 218, 187))
    d.rectangle((5 * k, 3 * k, w - 5 * k, h - 4 * k), fill=(96, 58, 28))
    # Pale packing liner separates the dark camera from the cardboard rim.
    d.rectangle((6 * k, 4 * k, w - 6 * k, h - 5 * k), fill=(255, 239, 210))
    camera = socks.fit_height(camera, 35 * k)
    image.alpha_composite(camera, ((w - camera.width) // 2, 2 * k))
    return image.resize((BOX_W, BOX_H), Image.Resampling.LANCZOS)


def main():
    box = build_box()
    jobs = [
        ("camera-zone2-v54.png", (466, 621), (355, 565, 575, 602), (90, 12, 118, 33), (355, 509, 575, 546)),
        ("camera-zone3-packed-v54.png", (657, 478), (590, 436, 724, 475), (56, 15, 82, 35), (430, 436, 564, 475)),
        ("camera-zone4-v54.png", (972, 718), (902, 606, 1044, 650), (76, 11, 101, 30), (902, 550, 1044, 594)),
    ]
    assert box.size == (124, 44)
    box_pixels = np.asarray(box)
    camera_pixels = box_pixels[..., :3].max(-1) < 125
    camera_pixels[:4] = camera_pixels[-5:] = False
    camera_pixels[:, :8] = camera_pixels[:, -8:] = False
    assert camera_pixels.sum() > 400, "Camera silhouette is missing"
    for name, (cx, bottom), strap, buckle, clean_wall in jobs:
        result = ENV.copy()
        x0, y0, x1, y1 = strap
        result.paste(ENV.crop(clean_wall), (x0, y0))
        x, y = cx - BOX_W // 2, bottom - BOX_H
        assert y >= 430 and bottom <= 718 and x + BOX_W < 1046
        result.alpha_composite(box, (x, y))
        # A narrower restraint crosses the package's lower rim, not the lens.
        layer = socks.strap_layer(strap, buckle).resize((x1 - x0, 22), Image.Resampling.LANCZOS)
        strap_y = bottom - 18
        result.alpha_composite(layer, (x0, strap_y))
        opaque = np.asarray(layer.getchannel("A")) == 255
        actual = np.asarray(result.crop((x0, strap_y, x1, strap_y + layer.height)))
        assert np.array_equal(actual[opaque], np.asarray(layer)[opaque])
        visible = np.all(np.asarray(result.crop((x, y, x + BOX_W, bottom))) == box_pixels, axis=-1)
        visible_fraction = visible[camera_pixels].mean()
        assert visible_fraction >= 0.85, f"Strap hides the camera in {name}: {visible_fraction:.1%} visible"
        # No accidental changes to the truck/other cargo outside this placement.
        changed = np.any(np.asarray(result) != np.asarray(ENV), axis=-1)
        allowed = np.zeros_like(changed)
        allowed[y:bottom, x:x + BOX_W] = True
        allowed[y0:y1, x0:x1] = True
        allowed[strap_y:strap_y + layer.height, x0:x1] = True
        assert not changed[~allowed].any(), f"Unrelated pixels changed in {name}"
        result.convert("RGB").save(ART / name, optimize=True)
        print(name, box.size, f"camera pixels visible: {visible_fraction:.1%}; foreground strap; exterior unchanged")


if __name__ == "__main__":
    main()
