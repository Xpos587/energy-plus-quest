# Scene 2 socks results v56: places 2-4 hold the SAME intact gift box with the sock pair (secured by the env strap); place 1 gets crushed box + scattered socks + shards (Grisha 09.11, Michael: place 4 stays secured).
# Run: uv run --with pillow --with numpy --with scipy python scripts/compose-socks-v56.py
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "public/compact-art"
REF = ROOT / "design/scene-01/assets/current/choices/socks.webp"
ENV = np.asarray(Image.open(ART / "compact-environment-v53-portrait.png").convert("RGB")).astype(int)
OUTLINE = (30, 40, 58, 255)
SOCK_H = 45  # px height of one lying sock in the 1368x1149 frame, same in every result


def socks():
    a = np.asarray(Image.open(REF).convert("RGB")).astype(int)
    inside = nd.binary_fill_holes(nd.binary_dilation(a.mean(-1) < 90, iterations=2))
    lab, n = nd.label(inside)
    out = []
    for i in range(1, n + 1):
        m = nd.binary_erosion(lab == i, iterations=1)
        if m.sum() < 20000:
            continue
        ys, xs = np.nonzero(m)
        rgba = np.dstack([a, m * 255]).astype(np.uint8)
        s = Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).rotate(90, expand=True)
        s = s.resize((round(s.width * SOCK_H / s.height), SOCK_H), Image.LANCZOS)
        out.append(outlined(s))
    return out  # [left sock, right sock], lying, cuffs to the left


def outlined(s):
    alpha = s.split()[3].point(lambda v: 255 if v > 90 else 0)
    ring = alpha.filter(ImageFilter.MaxFilter(3))
    c = Image.new("RGBA", (s.width + 2, s.height + 2), (0, 0, 0, 0))
    c.paste(Image.new("RGBA", ring.size, OUTLINE), (1, 1), ring)
    c.alpha_composite(s, (1, 1))
    return c


def pair(left, right):
    dx, dy = round(left.width * 0.1), round(SOCK_H * 0.2)
    c = Image.new("RGBA", (max(left.width, right.width) + dx, SOCK_H + 2 + dy), (0, 0, 0, 0))
    c.alpha_composite(right, (dx, 0))
    c.alpha_composite(left, (0, dy))
    return c


def contact_shadow(img, sprite, x, bottom, wall=False):
    a = sprite.split()[3]
    if wall:  # pressed to the wall: soft drop shadow down-right
        sh, ox, oy, blur, k = a, x + 3, bottom - sprite.height + 4, 3, 0.35
    else:  # lying on a surface: squashed, sheared silhouette under it
        sh = a.resize((sprite.width, max(4, sprite.height // 4))).transform(
            (sprite.width + 12, max(4, sprite.height // 4)), Image.AFFINE, (1, -0.3, 0, 0, 1, 0))
        ox, oy, blur, k = x, bottom - sh.height // 2, 3, 0.45
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * k))
    img.paste(Image.new("RGBA", sh.size, (20, 30, 50, 255)), (ox, oy), sh)


def tight(s):
    return s.crop(s.getbbox())


def crushed_box(width=86):
    """The truck's own cardboard box (env), crushed at the right corner, flaps torn open."""
    src = ENV[475:546, 595:720]
    card = ~(src[..., 2] > src[..., 0] + 8)
    lab, n = nd.label(nd.binary_fill_holes(card))
    keep = lab == 1 + np.argmax(nd.sum(card, lab, range(1, n + 1)))
    b = Image.fromarray(np.dstack([src, keep * 255]).astype(np.uint8))
    W, H = width, round(b.height * width / b.width)
    b = b.resize((W, H), Image.LANCZOS)
    h = W // 2
    crushed = b.transform((W, H), Image.MESH, [
        ((0, 0, h, H), (0, -0.06 * H, 0, H, h, H, h, -0.14 * H)),
        ((h, 0, W, H), (h, -0.14 * H, h, H, W, H, W, -0.55 * H)),
    ], Image.BICUBIC)
    pad = 26
    c = Image.new("RGBA", (W + 2 * pad, H + pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    ox, oy = pad, pad
    P = lambda pts: [(ox + x * W, oy + y * H) for x, y in pts]
    ink, card_in, card_out = (55, 31, 12, 255), (205, 135, 72, 255), (241, 179, 115, 255)
    # back flap standing up behind the box
    d.polygon(P([(0.12, 0.06), (0.5, 0.12), (0.58, -0.3), (0.2, -0.36)]), fill=card_in, outline=ink, width=2)
    c.alpha_composite(crushed, (ox, oy))
    # front-left flap folded open, torn edge
    d.polygon(P([(0.0, 0.05), (0.42, 0.11), (0.3, -0.22), (0.18, -0.16), (0.1, -0.26), (-0.18, -0.12)]),
              fill=card_out, outline=ink, width=2)
    # right flap crushed down over the dented corner
    d.polygon(P([(0.5, 0.12), (1.0, 0.36), (0.97, 0.62), (0.86, 0.52), (0.76, 0.66), (0.6, 0.4)]),
              fill=card_in, outline=ink, width=2)
    # creases from the dent
    d.line(P([(0.62, 0.42), (0.55, 0.62), (0.63, 0.8), (0.58, 0.96)]), fill=ink, width=2)
    d.line(P([(0.9, 0.62), (0.8, 0.8), (0.86, 0.97)]), fill=ink, width=2)
    d.line(P([(0.64, 0.44), (0.57, 0.62), (0.65, 0.8)]), fill=(255, 214, 160, 255), width=1)
    return tight(c.rotate(5, expand=True, resample=Image.BICUBIC))


def restore_env(res, box, pad=8):
    """Replace the old gift (box/tray/loose socks) with the empty-truck pixels."""
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    r = np.asarray(res.convert("RGB")).astype(int)
    m = np.zeros(r.shape[:2], bool)
    m[y0:y1, x0:x1] = np.abs(r[y0:y1, x0:x1] - ENV[y0:y1, x0:x1]).sum(-1) > 30
    m = nd.binary_dilation(m, iterations=4)
    m[:y0], m[y1:], m[:, :x0], m[:, x1:] = False, False, False, False
    mask = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    res.paste(Image.fromarray(ENV.astype(np.uint8)).convert("RGBA"), (0, 0), mask)


def redraw_strap(res, box):
    """Paste the env strap (red band, its dark edges, buckle) back over the socks."""
    x0, y0, x1, y1 = box
    e = ENV[y0:y1, x0:x1]
    red = (e[..., 0] > 170) & (e[..., 1] < 90) & (e[..., 2] < 90)
    near = nd.binary_dilation(red, iterations=2)
    lum = e.mean(-1)
    cols = np.nonzero(red.any(0))[0]
    gap = np.setdiff1d(np.arange(cols.min(), cols.max()), cols)  # buckle interrupts the red band
    buckle = np.zeros_like(red)
    rows = np.nonzero(red.any(1))[0]
    if len(gap):
        buckle[max(rows.min() - 4, 0):rows.max() + 5, gap.min() - 3:gap.max() + 4] = True
    m = (red | (near & (lum < 120)) | (buckle & ((e.max(-1) - e.min(-1) < 28) | (lum < 120))))
    mask = Image.new("L", res.size, 0)
    mask.paste(Image.fromarray((m * 255).astype(np.uint8)), (x0, y0))
    res.paste(Image.fromarray(ENV.astype(np.uint8)).convert("RGBA"), (0, 0), mask)


INK, CARD_IN, CARD_OUT = (55, 31, 12, 255), (205, 135, 72, 255), (241, 179, 115, 255)
BOX_W = 88  # one width for every secured place (Grisha: place 3 box == place 2 box)


def gift_box(bundle, width=BOX_W):
    """Intact open-top gift box (env front face) with the sock pair peeking out over the rim."""
    src = ENV[475:546, 595:720]
    face = Image.fromarray(np.dstack([src, np.full(src.shape[:2], 255)]).astype(np.uint8))
    face = face.resize((width, round(face.height * width / face.width)), Image.LANCZOS)
    W, H, rim, pad = width, face.height, 9, 8
    c = Image.new("RGBA", (W + 2 * pad, H + rim + bundle.height + pad), (0, 0, 0, 0))
    top = bundle.height  # y of the rim line inside c
    d = ImageDraw.Draw(c)
    # dark inside of the open box behind the socks
    d.polygon([(pad + 3, top + rim), (pad + W - 3, top + rim), (pad + W - 8, top), (pad + 8, top)], fill=(70, 42, 20, 255), outline=INK)
    c.alpha_composite(bundle, ((c.width - bundle.width) // 2, top - bundle.height + 28))
    # folded side flaps, then the front face over the socks' lower part
    d.polygon([(pad + 3, top + rim), (pad - 7, top + rim - 11), (pad - 2, top + rim - 15), (pad + 10, top + 2)], fill=CARD_IN, outline=INK)
    d.polygon([(pad + W - 3, top + rim), (pad + W + 7, top + rim - 11), (pad + W + 2, top + rim - 15), (pad + W - 10, top + 2)], fill=CARD_IN, outline=INK)
    c.alpha_composite(face, (pad, top + rim - 3))
    return tight(c)


def shards(res, box_x, box_w, crate_top):
    """Cardboard splinters around the crushed box (place 1 only)."""
    d = ImageDraw.Draw(res)
    cx = box_x + box_w // 2
    spec = [  # (dx from box centre, y, size, angle, light?)
        (-70, crate_top - 4, 13, 20, 1), (-44, crate_top - 1, 9, 200, 0), (62, crate_top - 2, 11, 80, 0),
        (90, crate_top - 6, 14, 150, 1), (118, crate_top - 1, 8, 300, 0),
        (-58, crate_top - 40, 9, 40, 1), (74, crate_top - 46, 10, 250, 0), (-26, crate_top - 62, 8, 120, 1),
    ]
    for dx, y, k, ang, light in spec:
        pts = []
        for i, (r, a) in enumerate([(1.0, 0), (0.55, 140), (0.9, 250)]):
            t = np.radians(ang + a)
            pts.append((cx + dx + k * r * np.cos(t), y + k * 0.7 * r * np.sin(t)))
        d.polygon(pts, fill=CARD_OUT if light else CARD_IN, outline=INK)


def main():
    left, right = socks()
    bundle = pair(left, right)
    box = gift_box(bundle)
    print("sock", left.size, "pair", bundle.size, "box", box.size)

    jobs = {
        # out file: (source, old gift bbox, (box centre x, bottom y), strap bbox, on wall)
        "socks-zone2-v56.png": ("socks-zone2-v53.png", (385, 542, 544, 624), (466, 617), (355, 565, 575, 602), False),
        "socks-zone3-secured-v56.png": ("socks-zone3-secured-v53.png", (584, 421, 730, 491), (657, 479), (590, 436, 724, 475), False),
        "socks-zone4-v56.png": ("socks-zone4-v53.png", (895, 495, 1047, 679), (972, 650), (905, 610, 1040, 642), True),
    }
    for out, (src, gift, (cx, bottom), strap, wall) in jobs.items():
        res = Image.open(ART / src).convert("RGBA")
        restore_env(res, gift)
        x = cx - box.width // 2
        contact_shadow(res, box, x, bottom, wall)
        res.alpha_composite(box, (x, bottom - box.height))
        redraw_strap(res, strap)
        res.convert("RGB").save(ART / out, optimize=True)
        print(out)

    # place 1: unsecured -> box crushed and torn open, socks flew out, cardboard shards around
    res = Image.open(ART / "socks-zone1-unsecured-v54.png").convert("RGBA")
    restore_env(res, (120, 505, 280, 585))
    restore_env(res, (357, 607, 413, 677))  # the old sock that flew onto the dishes crate
    crate_top = 569  # middle of the crate's top face
    box, bx = crushed_box(), 96
    by = crate_top - box.height + 3
    a = tight(left.rotate(-58, expand=True, resample=Image.BICUBIC))  # spilling out over the torn flap
    b = tight(right.rotate(-174, expand=True, resample=Image.BICUBIC))  # flung onto the dishes crate
    contact_shadow(res, box, bx + 6, crate_top)
    res.alpha_composite(a, (bx + box.width - 52, crate_top - a.height + 1))
    res.alpha_composite(box, (bx, by))
    shards(res, bx, box.width, crate_top)
    contact_shadow(res, b, 362, 620)
    res.alpha_composite(b, (362, 620 - b.height + 2))
    res.convert("RGB").save(ART / "socks-zone1-unsecured-v56.png", optimize=True)
    print("socks-zone1-unsecured-v56.png")


main()
