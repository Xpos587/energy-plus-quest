"""Replace plaque text in warehouse art: relabel.py src out font cap_px 'cx,cy,TEXT' ..."""
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

src, out, font, cap = sys.argv[1:5]; cap = float(cap)
im = Image.open(src).convert("RGB"); a = np.asarray(im).astype(int)
H, W = a.shape[:2]
white = (a.min(axis=2) > 185) & (a.max(axis=2) - a.min(axis=2) < 60)
dark = (a[..., 2] - a[..., 0] > 40) & (a.sum(axis=2) < 420)

def plaque(cx, cy, c):
    rx, ry = int(1.5 * c) + 2, int(c) + 2
    # nearest white seed, then flood fill the white plaque face (text holes stay out)
    cands = sorted(((x, y) for y in range(cy - ry, cy + ry + 1) for x in range(cx - rx, cx + rx + 1)
                    if 0 <= x < W and 0 <= y < H and white[y, x]), key=lambda p: (p[0]-cx)**2 + (p[1]-cy)**2)
    best = set(); tried = 0
    for seed in cands:
        if seed in best or tried >= 6: continue
        tried += 1
        seen = {seed}; q = deque([seed])
        while q:
            x, y = q.popleft()
            for n in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if n not in seen and 0 <= n[0] < W and 0 <= n[1] < H and white[n[1], n[0]] and abs(n[0]-cx) < 6*c and abs(n[1]-cy) < 4*c:
                    seen.add(n); q.append(n)
        if len(seen) > len(best): best = seen
    seen = best
    rows = {}
    for x, y in seen:
        lo, hi = rows.get(y, (x, x)); rows[y] = (min(lo, x), max(hi, x))
    cols = {}
    for x, y in seen:
        lo, hi = cols.get(x, (y, y)); cols[x] = (min(lo, y), max(hi, y))
    return rows, cols

morph0 = lambda mask, n: np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(n))) > 127
for spec in sys.argv[5:]:
    cx, cy, text, *own = spec.split(","); cx, cy = int(cx), int(cy)
    bh = float(own[0]) if own else cap
    rows, cols = plaque(cx, cy, bh)
    # face = pixels between the white extents of each row AND each column
    face = np.zeros((H, W), bool)
    for y, (lo, hi) in rows.items(): face[y, lo:hi+1] = True
    colmask = np.zeros((H, W), bool)
    for x, (lo, hi) in cols.items(): colmask[lo:hi+1, x] = True
    face &= colmask
    m = face & ~white
    core = morph0(face, max(3, int(bh * 0.5) | 1)) & dark
    ty, tx = np.nonzero(core if core.any() else m)
    tx0, tx1, ty0, ty1 = tx.min(), tx.max(), ty.min(), ty.max()
    xs = np.array(sorted(cols)); tops = np.array([cols[x][0] for x in xs])
    slope = np.polyfit(xs, tops, 1)[0] if len(xs) > 3 else 0
    x0, x1 = xs.min(), xs.max()
    ink = tuple(int(v) for v in np.median(a[m & dark], axis=0) * 0.9) if (m & dark).any() else (20, 60, 140)
    paper = tuple(int(v) for v in np.median(a[face & white], axis=0))
    morph = lambda mask, flt: np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).filter(flt)) > 127
    fill = morph(face, ImageFilter.MinFilter(7)) | (morph(m, ImageFilter.MaxFilter(5)) & face)
    out_a = np.asarray(im).copy(); out_a[fill] = paper; im = Image.fromarray(out_a)
    # height of upright text = vertical extent minus the shear across its width
    bh = float(own[0]) if own else cap
    fy, fx = np.nonzero(face); fcx, fcy = fx.mean(), fy.mean()
    S = 4
    f = ImageFont.truetype(font, int(bh*S))
    l, t, r, b = f.getbbox(text)
    k = min(bh*S/(b-t), (x1-x0-6)*S/(r-l))
    f = ImageFont.truetype(font, max(4, int(bh*S*k))); l, t, r, b = f.getbbox(text)
    layer = Image.new("L", (r-l+2, b-t+2), 0); ImageDraw.Draw(layer).text((-l+1, -t+1), text, font=f, fill=255)
    layer = layer.transform((layer.width, layer.height + int(abs(slope) * layer.width) + 2), Image.AFFINE,
                            (1, 0, 0, -slope, 1, 0 if slope >= 0 else -(abs(slope) * layer.width)), Image.BICUBIC)
    layer = layer.resize((max(1, round(layer.width/S)), max(1, round(layer.height/S))), Image.LANCZOS)
    px = round(fcx - layer.width/2); py = round(fcy - layer.height/2)
    im.paste(Image.new("RGB", layer.size, ink), (px, py), layer)
    print(spec, "face x", (x0, x1), "text", (tx0, ty0, tx1, ty1), "slope %.2f" % slope)
im.save(out)
