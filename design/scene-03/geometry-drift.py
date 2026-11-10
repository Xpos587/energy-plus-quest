# Measure how far the hand-painted warehouse plate drifts from the straight Blender render.
#
# The restyle (design/scene-03/v10/gen.sh) keeps the render's layout but bends straight architecture:
# rack posts lean, beams and floor joints dip. This script measures that drift with block normalised
# cross-correlation between the plate and the render it was restyled from, and writes a report plus an
# overlay that a person can check by eye.
#
#   python3 design/scene-03/geometry-drift.py public/scene-art/inventory-master-v11.webp OUT_DIR
#
# Geometry (see export.py / extend.py): the 1536-wide render plane, render rows 80..944, maps onto the
# 1672x941 game plane; rows below 941 are out-painted lawn and carry no render structure.
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).parents[2]
RENDER = ROOT / ".tmp-work/wh3d/gen/desk-ref.png"  # 1536x1024 Blender plate, straight geometry
PLANE_W, RENDER_Y0 = 1672, 80
HALL = (40, 95, 1630, 900)  # x0, y0, x1, y1 of the measured hall interior
SCALE, BLOCK, STRIDE, SEARCH = 4, 20, 10, 4
MIN_TEXTURE, MIN_CORR = 5.0, 0.4


def render_on_plane(shape, render):
    """Resample the render onto the plate grid, and report which plate pixels it covers."""
    h, w = shape
    rw, rh = render.size
    r = np.asarray(render.convert("RGB"), np.float32)
    g = w / PLANE_W  # plate px per plane px (1 wide, 0.718 tall)
    xs = (np.arange(w) / g) * (rw / PLANE_W)
    ys = (np.arange(h) / g) * (rw / PLANE_W) + RENDER_Y0
    sx, sy = np.meshgrid(xs, ys)
    ok = (sx >= 0) & (sx < rw - 1) & (sy >= RENDER_Y0) & (sy < rh - 1)
    out = np.zeros((h, w, 3), np.float32)
    xi, yi = np.clip(sx[ok], 0, rw - 1.001), np.clip(sy[ok], 0, rh - 1.001)
    x0, y0 = xi.astype(int), yi.astype(int)
    fx, fy = (xi - x0)[..., None], (yi - y0)[..., None]
    top = r[y0, x0] * (1 - fx) + r[y0, x0 + 1] * fx
    bot = r[y0 + 1, x0] * (1 - fx) + r[y0 + 1, x0 + 1] * fx
    out[ok] = top * (1 - fy) + bot * fy
    return out, ok


def flow(painted_gray, render_gray, ok):
    """Block displacement of the plate relative to the render, with a confidence filter."""
    def small(a):
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        return np.asarray(im.resize((im.width // SCALE, im.height // SCALE), Image.BOX), np.float32)

    g1, g2 = small(painted_gray), small(render_gray)
    oks = np.asarray(Image.fromarray((ok * 255).astype(np.uint8)).resize((g2.shape[1], g2.shape[0]), Image.BOX), np.float32) > 200
    h, w = g1.shape
    half, r = BLOCK // 2, SEARCH
    pts, vec = [], []
    for cy in range(half + r, h - half - r, STRIDE):
        for cx in range(half + r, w - half - r, STRIDE):
            if not oks[cy, cx]:
                continue
            tpl = g1[cy - half:cy + half, cx - half:cx + half]
            if tpl.std() < MIN_TEXTURE:
                continue
            win = g2[cy - half - r:cy + half + r + 1, cx - half - r:cx + half + r + 1]
            if win.std() < MIN_TEXTURE:
                continue
            tn = (tpl - tpl.mean()) / tpl.std()
            st = np.lib.stride_tricks.sliding_window_view(win, (BLOCK, BLOCK))
            means, stds = st.mean(axis=(2, 3)), st.std(axis=(2, 3))
            with np.errstate(invalid="ignore", divide="ignore"):
                corr = ((st - means[:, :, None, None]) * tn).sum(axis=(2, 3)) / (stds * tpl.size)
            corr = np.nan_to_num(corr, nan=-1.0)
            iy, ix = np.unravel_index(np.argmax(corr), corr.shape)
            if corr[iy, ix] < MIN_CORR or iy in (0, 2 * r) or ix in (0, 2 * r):
                continue
            pts.append([cx * SCALE, cy * SCALE])
            vec.append([(ix - r) * SCALE, (iy - r) * SCALE])
    return np.asarray(pts, np.float32), np.asarray(vec, np.float32)


def stats(pts, vec, box):
    x0, y0, x1, y1 = box
    keep = (pts[:, 0] >= x0) & (pts[:, 0] <= x1) & (pts[:, 1] >= y0) & (pts[:, 1] <= y1)
    v = vec[keep]
    mag = np.sqrt((v ** 2).sum(1))
    return {"blocks": int(keep.sum()),
            "meanDriftPx": round(float(mag.mean()), 2) if len(v) else None,
            "p95DriftPx": round(float(np.percentile(mag, 95)), 2) if len(v) else None,
            "maxDriftPx": round(float(mag.max()), 2) if len(v) else None}


def overlay(plate, render, pts, vec, out):
    a = plate.copy()
    g = np.asarray(Image.fromarray(np.clip(render, 0, 255).astype(np.uint8)).convert("L"), np.float32)
    edge = (np.abs(np.diff(g, axis=1, prepend=g[:, :1])) + np.abs(np.diff(g, axis=0, prepend=g[:1]))) > 25
    edge &= np.asarray(Image.fromarray(np.full(g.shape, 255, np.uint8))).astype(bool)
    a[edge] = [255, 40, 40]
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    for (x, y), (vx, vy) in zip(pts, vec):
        d.line([x, y, x + vx * 6, y + vy * 6], fill=(0, 90, 255), width=2)
    im.save(out)


def main(argv):
    src, out_dir = Path(argv[0]), Path(argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    plate = np.asarray(Image.open(src).convert("RGB"), np.uint8)
    render, ok = render_on_plane(plate.shape[:2], Image.open(RENDER))
    gray = np.asarray(Image.fromarray(plate).convert("L"), np.float32)
    rgray = np.asarray(Image.fromarray(np.clip(render, 0, 255).astype(np.uint8)).convert("L"), np.float32)
    pts, vec = flow(gray, rgray, ok)
    rows = {
        "hall": stats(pts, vec, HALL),
        "rackRowLeft": stats(pts, vec, (380, 200, 620, 900)),
        "rackRowMiddle": stats(pts, vec, (620, 200, 900, 900)),
        "rackRowRight": stats(pts, vec, (900, 200, 1200, 900)),
        "floor": stats(pts, vec, (300, 560, 1300, 900)),
        "facade": stats(pts, vec, (150, 95, 1500, 260)),
    }
    report = {"source": str(src), "render": str(RENDER.relative_to(ROOT)), "measuredBox": HALL,
              "note": "drift = block displacement of the painted plate relative to the straight render; "
                      "0 means the paint follows the render's straight edges",
              "rows": rows}
    (out_dir / "geometry-drift.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    overlay(plate, render, pts, vec, out_dir / "geometry-drift-overlay.png")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
