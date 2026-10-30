"""Flowers-style pass-1 assembly for the scene-1 plates.
usage: assemble.py boxes.json SOURCE OUT.png MASTER_LONG_EDGE
For each crop <name> (box in source px) the AI tile g-<name>.png is
registered with the repo's SIFT similarity (scripts/flowers/registration.py:
>=12 inliers, >=45% inliers, p95 <= 1.8 source px, rotation <= 0.6 deg)
against the LANCZOS-upscaled source crop, warped into master space, its low
frequencies matched to the source (no fine texture transfer), and blended
with a cosine feather over 20% of the padded box at interior edges only.
Rejected tiles keep the upscaled source pixels and are reported."""
import importlib.util, json, sys
import cv2, numpy as np
from PIL import Image
spec = importlib.util.spec_from_file_location("reg", "/home/michael/Github/energy-plus-quest/scripts/flowers/registration.py")
reg = importlib.util.module_from_spec(spec); spec.loader.exec_module(reg)

meta = json.load(open(sys.argv[1])); out = sys.argv[3]
S = cv2.imread(sys.argv[2], cv2.IMREAD_COLOR)
# Tiles are cut from the reflect-padded source (prep.py); assemble on the
# padded canvas, then crop the pad away.
PADX, PADY = meta.get("pad", [0, 0])
if PADX or PADY:
    S = cv2.copyMakeBorder(S, PADY, PADY, PADX, PADX, cv2.BORDER_REFLECT_101)
H, W = S.shape[:2]
k = float(sys.argv[4]) / max(W - 2 * PADX, H - 2 * PADY)
MW, MH = round(W * k), round(H * k)
base = cv2.resize(S, (MW, MH), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
acc = np.zeros_like(base); wsum = np.zeros((MH, MW, 1), np.float32)
rows = []
for t in meta["tiles"]:
    n = t["name"]; x0, y0, x1, y1 = t["box"]
    g = cv2.imread(f"g-{n}.png", cv2.IMREAD_COLOR)
    if g is None:
        rows.append({"tile": n, "accepted": False, "reason": "missing"}); continue
    X0, Y0, X1, Y1 = [round(v * k) for v in (x0, y0, x1, y1)]
    w, h = X1 - X0, Y1 - Y0
    ref = base[Y0:Y1, X0:X1].astype(np.uint8)
    affine, metric = reg.register(ref, g, reference_pixels_per_source_pixel=k)
    row = {"tile": n, "native": [g.shape[1], g.shape[0]], **{q: metric.get(q) for q in ("accepted", "inliers", "inlierFraction", "p95ResidualSourcePx", "reason")}}
    rows.append(row)
    if affine is None or not metric.get("accepted"):
        continue
    # warp the tile into this box of the master
    wg = cv2.warpAffine(g, affine, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT).astype(np.float32)
    valid = cv2.warpAffine(np.ones(g.shape[:2], np.float32), affine, (w, h), flags=cv2.INTER_LINEAR)
    valid = cv2.erode((valid > .999).astype(np.float32), np.ones((5, 5), np.uint8))
    hard = cv2.erode(valid, np.ones((9, 9), np.uint8))
    # low-frequency colour match to the source, counting only the tile's
    # own pixels (masked low-pass), so no halo where the tile ends.
    sig = max(w, h) / 48
    def lo(img, m):
        num = cv2.GaussianBlur(img * m[..., None], (0, 0), sig)
        den = cv2.GaussianBlur(m, (0, 0), sig)[..., None]
        return num / np.maximum(den, 1e-4)
    wg = np.clip(wg + lo(base[Y0:Y1, X0:X1], hard) - lo(wg, hard), 0, 255)
    # Soft fade inside the tile's own valid area, so a tile a few px short
    # of the canvas edge hands over smoothly to the source there.
    valid = cv2.GaussianBlur(cv2.erode(hard, np.ones((25, 25), np.uint8)), (0, 0), 4) * hard
    fx = np.ones(w, np.float32); fy = np.ones(h, np.float32)
    rx, ry = int(w * .2), int(h * .2)
    ramp = lambda r: (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, r))).astype(np.float32)
    fx[:rx] = ramp(rx) if X0 > 0 else 1
    fx[w - rx:] = ramp(rx)[::-1] if X1 < MW else 1
    fy[:ry] = ramp(ry) if Y0 > 0 else 1
    fy[h - ry:] = ramp(ry)[::-1] if Y1 < MH else 1
    a = (fy[:, None] * fx[None, :] * valid)[..., None]
    acc[Y0:Y1, X0:X1] += wg * a; wsum[Y0:Y1, X0:X1] += a
M = np.where(wsum > 1e-3, acc / np.maximum(wsum, 1e-3), base)
cx, cy = round(PADX * k), round(PADY * k)
OW, OH = round((W - 2 * PADX) * k), round((H - 2 * PADY) * k)
M = M[cy:cy + OH, cx:cx + OW]; wsum = wsum[cy:cy + OH, cx:cx + OW]
cv2.imwrite(out, np.clip(M + .5, 0, 255).astype(np.uint8))
cover = np.where(wsum[..., 0] > 0.5, 1, 0)
cv2.imwrite(out.replace(".png", "-coverage.png"), (np.clip(wsum[..., 0], 0, 1) * 255).astype(np.uint8))
json.dump({"master": [OW, OH], "coverage": float(cover.mean()), "tiles": rows}, open(out.replace(".png", ".json"), "w"), indent=1)
for r in rows: print(r)
print(out, OW, OH, "coverage>0.5", round(float(cover.mean()), 4))
