"""Same camera in secured places, with native restraints and roof-safe headroom.

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


def build_box(height=BOX_H, camera_height=35, camera_top=2):
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
    w, h = BOX_W * k, height * k
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
    camera = socks.fit_height(camera, camera_height * k)
    image.alpha_composite(camera, ((w - camera.width) // 2, camera_top * k))
    return image.resize((BOX_W, height), Image.Resampling.LANCZOS)


def main(output=ART):
    # Keep the insert on its support; extend upward to clear the native band.
    # The niche has only 48px below the roof, so its same camera is 31px high.
    jobs = [
        ("camera-zone2-v54.png", (466, 621), (355, 565, 575, 602), (90, 12, 118, 33), 0, (68, 35, 2)),
        ("camera-zone3-packed-v54.png", (657, 478), (590, 436, 724, 475), (56, 15, 82, 35), 0, (48, 31, 1)),
        ("camera-zone4-v54.png", (972, 718), (902, 606, 1044, 650), (76, 11, 101, 30), 66, (59, 35, 2)),
    ]
    for name, (cx, bottom), strap, buckle, dy, dimensions in jobs:
        box = build_box(*dimensions)
        assert box.width == BOX_W
        box_pixels = np.asarray(box)
        camera_pixels = box_pixels[..., :3].max(-1) < 125
        camera_pixels[:4] = camera_pixels[-5:] = False
        camera_pixels[:, :8] = camera_pixels[:, -8:] = False
        assert camera_pixels.sum() > 400, "Camera silhouette is missing"
        result = ENV.copy()
        x0, y0, x1, y1 = strap
        if dy:
            # Same floor-level translation as socks; retain full-size mounts.
            result.paste(ENV.crop((x0, y0 - 56, x1, y1 - 56)), (x0, y0))
            result.paste(ENV.crop(strap), (x0, y0 + dy))
        x, y = cx - BOX_W // 2, bottom - box.height
        assert y >= 430 and bottom <= 718 and x + BOX_W < 1046
        result.alpha_composite(box, (x, y))
        layer = socks.strap_layer(strap, buckle)
        strap_y = y0 + dy
        result.alpha_composite(layer, (x0, strap_y))
        visible = np.all(np.asarray(result.crop((x, y, x + BOX_W, bottom))) == box_pixels, axis=-1)
        visible_fraction = visible[camera_pixels].mean()
        assert visible_fraction >= 0.70, f"Strap hides the camera in {name}: {visible_fraction:.1%} visible"
        # Match the accepted socks hardware pixel-for-pixel, without squashing
        # the band, buckle or mounts. Place 4 follows its floor-level translation.
        original = socks.strap_layer(strap, buckle)
        expected_y = y0 + (66 if "zone4" in name else 0)
        hardware = np.asarray(original.getchannel("A")) == 255
        actual = np.asarray(result.crop((x0, expected_y, x1, expected_y + original.height)))
        assert np.array_equal(actual[hardware], np.asarray(original)[hardware]), f"Distorted or displaced restraint in {name}"
        # No accidental changes to the truck/other cargo outside this placement.
        changed = np.any(np.asarray(result) != np.asarray(ENV), axis=-1)
        allowed = np.zeros_like(changed)
        allowed[y:bottom, x:x + BOX_W] = True
        allowed[y0:y1, x0:x1] = True
        allowed[strap_y:strap_y + layer.height, x0:x1] = True
        assert not changed[~allowed].any(), f"Unrelated pixels changed in {name}"
        result.convert("RGB").save(output / name, optimize=True)
        print(name, box.size, f"camera pixels visible: {visible_fraction:.1%}; foreground strap; exterior unchanged")


if __name__ == "__main__":
    main()
