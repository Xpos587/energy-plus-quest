"""Scene 5 r29 from r28 (call 21.11): windsock instead of the flag, rig moved to the far right corner,
chum moved far from АБК (other bank), helipad on a clean concrete square. Local raster edits only.
Run: ~/.local/share/comfyui/venv/bin/python design/scene-05/r29/compose.py
"""
from pathlib import Path
import numpy as np, cv2 as cv
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'public/scene-art/lastmile-family-v1/revision-28'
DST = ROOT / 'public/scene-art/lastmile-family-v1/revision-29'

def mask(size, pts, blur=0):
    m = Image.new('L', size); ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m

def clone(im, pts, dx, dy, blur=3):
    """Fill a polygon with the same-depth texture found at (+dx, +dy)."""
    src = im.transform(im.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), Image.BICUBIC)
    im.paste(src, (0, 0), mask(im.size, pts, blur))

def move(im, base, pts, to, scale, blur=4):
    """Cut a polygon from `base` and paste it scaled with its bbox top-left at `to` (feathered)."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]; box = (min(xs), min(ys), max(xs), max(ys))
    cut = base.crop(box).convert('RGBA'); cut.putalpha(mask(cut.size, [(x - box[0], y - box[1]) for x, y in pts], blur))
    cut = cut.resize((round(cut.width * scale), round(cut.height * scale)), Image.LANCZOS)
    im.paste(cut, to, cut)

def dirt(im, pts, rgb, blur=4):
    """Plain worn-dirt fill (pad colour + faint grain) for a cleared object footprint."""
    w, h = im.size; g = cv.GaussianBlur(np.random.default_rng(7).normal(0, 7, (h, w)).astype('float32'), (0, 0), 1.0)
    a = np.clip(np.array(rgb, 'float32')[None, None] + g[..., None], 0, 255).astype('uint8')
    im.paste(Image.fromarray(a), (0, 0), mask(im.size, pts, blur))

def camp(im, base, parts, to, scale, clearing):
    """Tents and reindeer cut tightly (no camp pad, no river), set on a small worn clearing."""
    cx, cy, rx, ry = clearing; w, h = im.size
    m = Image.new('L', im.size); ImageDraw.Draw(m).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(5))
    # same worn-dirt tone as the old camp pad, so the cut-outs' own ground blends in
    im.paste(Image.new('RGB', im.size, (204, 164, 131)), (0, 0), m)
    ox = min(p[0] for pts in parts for p in pts); oy = min(p[1] for pts in parts for p in pts)
    for pts in parts:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]; box = (min(xs), min(ys), max(xs), max(ys))
        cut = base.crop(box).convert('RGBA'); cut.putalpha(mask(cut.size, [(x - box[0], y - box[1]) for x, y in pts], 2.5))
        cut = cut.resize((round(cut.width * scale), round(cut.height * scale)), Image.LANCZOS)
        im.paste(cut, (round(to[0] + (box[0] - ox) * scale), round(to[1] + (box[1] - oy) * scale)), cut)

def helipad(im, base, quad, h_box):
    """Concrete square under the painted H circle; the white marking is kept from the original."""
    w, h = im.size; k = 4
    big = Image.new('RGBA', (w * k, h * k)); d = ImageDraw.Draw(big)
    q = [(x * k, y * k) for x, y in quad]
    sh = [(x * k + 3 * k, y * k + 4 * k) for x, y in quad]
    d.polygon(sh, fill=(70, 58, 50, 90))
    d.polygon(q, fill=(152, 154, 156, 255), outline=(232, 230, 222, 255), width=3 * k)
    pad = big.resize(im.size, Image.LANCZOS)
    # painterly slab: soft vertical light + faint noise
    a = np.asarray(pad).astype('float32'); yy = np.arange(h)[:, None]
    y0, y1 = min(p[1] for p in quad), max(p[1] for p in quad)
    light = np.clip((yy - y0) / max(1, y1 - y0), 0, 1) * 14 - 7
    noise = cv.GaussianBlur(np.random.default_rng(29).normal(0, 6, (h, w)).astype('float32'), (0, 0), 1.2)
    a[..., :3] = np.clip(a[..., :3] - light[..., None] + noise[..., None], 0, 255)
    pad = Image.fromarray(a.astype('uint8')); im.alpha_composite(pad) if im.mode == 'RGBA' else im.paste(pad, (0, 0), pad)
    # white circle + H, squashed like the painted one (h_box = circle bbox)
    x0, y0, x1, y1 = h_box; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    big = Image.new('RGBA', (w * k, h * k)); d = ImageDraw.Draw(big); W_ = (246, 246, 242, 255)
    d.ellipse(((cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k), outline=W_, width=round(ry * 0.13 * k))
    hw, hh, st = rx * 0.34, ry * 0.52, rx * 0.11
    for sx in (-1, 1): d.rectangle(((cx + sx * hw - st / 2) * k, (cy - hh) * k, (cx + sx * hw + st / 2) * k, (cy + hh) * k), fill=W_)
    d.rectangle(((cx - hw) * k, (cy - ry * 0.09) * k, (cx + hw) * k, (cy + ry * 0.09) * k), fill=W_)
    mark = big.resize(im.size, Image.LANCZOS); im.paste(mark, (0, 0), mark)
    # corner lights like the quay pad
    for x, y in quad: ImageDraw.Draw(im).ellipse((x - 2, y - 2, x + 2, y + 2), fill=(108, 214, 104))

def windsock(im, foot, top, length):
    """Orange/white aviation windsock on the existing pole, blown to the right."""
    w, h = im.size; k = 4; big = Image.new('RGBA', (w * k, h * k)); d = ImageDraw.Draw(big)
    fx, fy = foot; tx, ty = top
    d.line((fx * k, fy * k, tx * k, ty * k), fill=(92, 98, 108, 255), width=3 * k)
    mouth, tail = 7.0, 3.0  # half heights
    segs = 5
    for i in range(segs):
        t0, t1 = i / segs, (i + 1) / segs
        x0, x1 = tx + 2 + length * t0, tx + 2 + length * t1
        drop0, drop1 = 3 * t0 ** 2, 3 * t1 ** 2
        h0, h1 = mouth + (tail - mouth) * t0, mouth + (tail - mouth) * t1
        c = (236, 98, 36, 255) if i % 2 == 0 else (248, 246, 240, 255)
        d.polygon([(x0 * k, (ty + 5 + drop0 - h0) * k), (x1 * k, (ty + 5 + drop1 - h1) * k),
                   (x1 * k, (ty + 5 + drop1 + h1) * k), (x0 * k, (ty + 5 + drop0 + h0) * k)], fill=c)
    # outline + mouth ring
    d.line([((tx + 2) * k, (ty + 5 - mouth) * k), ((tx + 2 + length) * k, (ty + 5 + 3 - tail) * k)], fill=(70, 40, 30, 200), width=k)
    d.line([((tx + 2) * k, (ty + 5 + mouth) * k), ((tx + 2 + length) * k, (ty + 5 + 3 + tail) * k)], fill=(70, 40, 30, 200), width=k)
    d.line([((tx + 2) * k, (ty + 5 - mouth) * k), ((tx + 2) * k, (ty + 5 + mouth) * k)], fill=(70, 74, 80, 255), width=2 * k)
    s = big.resize(im.size, Image.LANCZOS); im.paste(s, (0, 0), s)

def wide():
    base = Image.open(SRC / 'choice-wide.webp').convert('RGB'); im = base.copy()
    # flag → windsock: clear the cloth (grass from the left), redraw on the same pole
    clone(im, [(906, 954), (970, 954), (970, 994), (920, 994), (920, 1004), (906, 1004)], -70, 0, 2)
    windsock(im, (915, 1004), (915, 958), 34)
    # rig: lift it with its gravel pad, fill with tundra of the same depth from the right
    rig = [(1428, 522), (1505, 522), (1527, 314), (1568, 314), (1590, 512), (1722, 512), (1768, 606), (1430, 606)]
    clone(im, rig, 330, 0, 6)
    # chum: off the АБК pad to the far left bank; the old spot becomes plain camp-pad dirt
    tents = [(1006, 568), (1030, 516), (1040, 516), (1062, 548), (1082, 548), (1100, 514), (1108, 514), (1136, 560), (1134, 568)]
    deer = [(1040, 572), (1068, 566), (1120, 566), (1124, 591), (1094, 593), (1046, 593)]
    herd = [(978, 578), (1016, 578), (1034, 594), (1032, 622), (980, 622)]
    # clean sources only: dirt/grass between the tents and the helipad, two strips; low strip from just above
    clone(im, [(998, 504), (1062, 504), (1062, 600), (970, 600), (970, 560), (986, 530)], 168, 0, 3)
    tip = np.asarray(mask(im.size, [(972, 518), (998, 518), (998, 562), (972, 562)]))
    im = Image.fromarray(cv.inpaint(np.asarray(im), tip, 5, cv.INPAINT_TELEA))
    clone(im, [(1060, 504), (1150, 504), (1150, 552), (1150, 598), (1060, 598)], 104, 0, 3)
    clone(im, [(970, 596), (1046, 596), (1046, 628), (970, 628)], 0, -30, 3)
    # last: bank edge where the tent stood, from the already-cleaned strip to the right
    clone(im, [(962, 512), (1004, 512), (1004, 598), (962, 598)], 150, 0, 6)
    camp(im, base, [tents, deer, herd], (538, 404), 0.62, (588, 446, 66, 36))
    move(im, base, rig, (1716, 368), 0.76, 4)
    helipad(im, base, [(1266, 544), (1404, 544), (1412, 598), (1258, 598)], (1290, 553, 1382, 589))
    return im

def tall():
    base = Image.open(SRC / 'choice-tall.webp').convert('RGB'); im = base.copy()
    rig = [(1036, 736), (1095, 736), (1112, 590), (1152, 590), (1170, 736), (1265, 736), (1278, 806), (1036, 806)]
    clone(im, rig, 300, 0, 6)
    tents = [(690, 765), (722, 716), (732, 716), (750, 745), (768, 716), (778, 716), (806, 762), (800, 768)]
    deer = [(726, 770), (750, 763), (798, 765), (800, 794), (726, 794)]
    clone(im, [(684, 750), (716, 704), (790, 704), (812, 750)], 130, 0, 4)
    dirt(im, [(680, 748), (816, 748), (818, 802), (716, 804), (678, 790)], (200, 162, 134), 5)
    camp(im, base, [tents, deer], (250, 520), 0.62, (288, 555, 52, 30))
    move(im, base, rig, (1112, 470), 0.74, 4)
    helipad(im, base, [(916, 752), (1060, 752), (1068, 818), (908, 818)], (938, 758, 1040, 812))
    return im

if __name__ == '__main__':
    DST.mkdir(exist_ok=True)
    for name, fn in (('wide', wide), ('tall', tall)):
        out = fn(); out.save(DST / f'choice-{name}.webp', 'WEBP', quality=92, method=6); print(name, out.size)
