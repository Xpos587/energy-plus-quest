"""Register gpt paints to the Blender R5 plate, compose overscan art, cut animated sprites, derive contours.
uv run --no-project --with opencv-python-headless --with numpy python scripts/lastmile-r5/compose.py <export> <gpt> <out> [<veh>]
<gpt>/{name}-full.png paints the whole overscan plate, <gpt>/{name}-inner.png only the original camera frame
(higher pixel density); both are ECC-registered to the plate, then per-landmark residuals are measured.
Optional <veh>: vehicles repainted at another size than their Blender proxies. <veh>/{name}-{key}.png are their silhouettes in
registered inner-frame pixels (they replace the ID masks for sprites, contours and hotspots, and skip the gate);
Optional <veh>/hub.json {name: {x, y, scale}} moves and scales the rotor onto the painted hub.
"""
import json, sys
from pathlib import Path
import cv2
import numpy as np

exp, gpt, out = map(Path, sys.argv[1:4]); out.mkdir(parents=True, exist_ok=True)
veh = Path(sys.argv[4]) if len(sys.argv) > 4 else None
HUB = json.loads((veh / 'hub.json').read_text()) if veh and (veh / 'hub.json').exists() else {}
L = json.loads((exp / 'layout.json').read_text()); PAL = L['id_palette']
GATE_PX = 3.0
TAP_MIN = 120   # plate px; the tall map shows at ~0.37x on a 390 px phone -> ≥44 CSS px
SPRITES = ('barge', 'rover', 'pipe_carrier')           # bob / idle layers (heli body stays in the plate)
gray = lambda im: cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (0, 0), 2).astype(np.float32) / 255


def ecc(ref, img, mode, init=None, iters=200):
    warp = init if init is not None else (np.eye(3, dtype=np.float32) if mode == cv2.MOTION_HOMOGRAPHY else np.eye(2, 3, dtype=np.float32))
    _, warp = cv2.findTransformECC(ref, img, warp, mode, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iters, 1e-6), None, 5)
    return warp


def register(plate, paint):
    """Global homography paint->plate (ECC at half resolution); returns the warped paint and the matrix."""
    h, w = plate.shape[:2]; paint = cv2.resize(paint, (w, h), interpolation=cv2.INTER_AREA if paint.shape[1] > w else cv2.INTER_CUBIC)
    s = np.diag([.5, .5, 1]).astype(np.float32)
    Hh = ecc(gray(cv2.resize(plate, (w // 2, h // 2))), gray(cv2.resize(paint, (w // 2, h // 2))), cv2.MOTION_HOMOGRAPHY)
    H = np.linalg.inv(s) @ Hh @ s
    return cv2.warpPerspective(paint, H, (w, h), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT), H   # reflect: no streaks at the overscan edge


def mask_of(ids, key):
    return (np.max(np.abs(ids - np.array(PAL[key], np.int16)), axis=2) <= 3).astype(np.uint8)


def floes(ids):
    """Floes drifting in the harbour: ice components fully surrounded by its water (shore-fast and river ice stay in the plate)."""
    ice = mask_of(ids, 'ice'); water = mask_of(ids, 'water')
    _, wl, ws, _ = cv2.connectedComponentsWithStats(cv2.dilate(water | ice, np.ones((3, 3), np.uint8)), connectivity=8)
    water &= (wl == 1 + np.argmax(ws[1:, cv2.CC_STAT_AREA])).astype(np.uint8)                  # the harbour = largest water body
    n, lab, stats, _ = cv2.connectedComponentsWithStats(ice, connectivity=8)
    out = np.zeros_like(ice); h, w = ice.shape
    for k in range(1, n):
        x, y, bw, bh, area = stats[k]
        if area > 4000: continue
        x0, y0, x1, y1 = max(x - 3, 0), max(y - 3, 0), min(x + bw + 3, w), min(y + bh + 3, h)
        own = (lab[y0:y1, x0:x1] == k).astype(np.uint8)
        r = cv2.dilate(own, np.ones((5, 5), np.uint8)) & (1 - ice[y0:y1, x0:x1])
        if r.sum() and (r & water[y0:y1, x0:x1]).sum() >= .95 * r.sum(): out[y0:y1, x0:x1] |= own
    return out


def residual(plate, paint, m):
    """Translation (px) that best aligns the painted landmark to the Blender landmark, edge-based ECC on its padded box."""
    ys, xs = np.nonzero(m); x0, y0, x1, y1 = xs.min() - 24, ys.min() - 24, xs.max() + 25, ys.max() + 25
    a = cv2.Canny(cv2.cvtColor(plate[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY), 40, 120)
    b = cv2.Canny(cv2.cvtColor(paint[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY), 40, 120)
    a, b = (cv2.GaussianBlur(v, (0, 0), 2).astype(np.float32) / 255 for v in (a, b))
    try: t = ecc(a, b, cv2.MOTION_TRANSLATION, iters=100); return float(t[0, 2]), float(t[1, 2])
    except cv2.error: return None


report = {}; contours = {}; artwork = {}; anim = {}
for name, v in L['views'].items():
    W, H = v['width'], v['height']; o = v['original']; ox, oy, ow, oh = int(o['x']), int(o['y']), o['width'], o['height']
    plate = cv2.imread(str(exp / f'{name}-plate.png')); ids = cv2.imread(str(exp / f'{name}-id.png'))[:, :, ::-1].astype(np.int16)
    full, Hf = register(plate, cv2.imread(str(gpt / f'{name}-full.png')))
    inner, Hi = register(plate[oy:oy + oh, ox:ox + ow], cv2.imread(str(gpt / f'{name}-inner.png')))
    feather = np.zeros((H, W), np.float32); feather[oy + 64:oy + oh - 64, ox + 64:ox + ow - 64] = 1   # R5-05c: wider blend, no visible full/inner seam
    feather = cv2.GaussianBlur(feather, (0, 0), 28)[..., None]
    canvas = full.astype(np.float32); canvas[oy:oy + oh, ox:ox + ow] = inner
    art = (canvas * feather + full * (1 - feather)).astype(np.uint8)
    def obj(key):
        p = veh and veh / f'{name}-{key}.png'
        if not (p and p.exists()): return mask_of(ids, key)
        m = np.zeros((H, W), np.uint8); m[oy:oy + oh, ox:ox + ow] = cv2.imread(str(p), 0) > 127; return m
    rows = {}
    for key in list(L['views'][name]['objects']) + ['barge']:
        if veh and (veh / f'{name}-{key}.png').exists(): rows[key] = dict(dx=None, dy=None, ok=True, painted=True); continue
        m = mask_of(ids, key); r = residual(plate, art, m)
        rows[key] = dict(dx=None if r is None else round(r[0], 2), dy=None if r is None else round(r[1], 2),
                         ok=r is not None and max(map(abs, r)) <= GATE_PX)
    report[name] = dict(H_full=Hf.round(5).tolist(), H_inner=Hi.round(5).tolist(), landmarks=rows, gate_px=GATE_PX,
                        passed=all(r['ok'] for r in rows.values()))
    # sprites: painted cutouts on the Blender silhouette; plate under them inpainted for +/-2 px motion
    base = art.copy(); anim[name] = {}
    for key in SPRITES + ('floes',):
        m = floes(ids) if key == 'floes' else obj(key)
        m = cv2.dilate(m, np.ones((3, 3), np.uint8)); ys, xs = np.nonzero(m)
        x0, y0, x1, y1 = max(xs.min() - 4, 0), max(ys.min() - 4, 0), min(xs.max() + 5, W), min(ys.max() + 5, H)
        alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), .7)[y0:y1, x0:x1]
        sprite = np.dstack([art[y0:y1, x0:x1], (np.clip(alpha * 1.6, 0, 1) * 255).astype(np.uint8)])
        cv2.imwrite(str(out / f'{name}-{key}.png'), sprite)
        hole = cv2.dilate(m, np.ones((7, 7), np.uint8)); base = cv2.inpaint(base, hole, 5, cv2.INPAINT_TELEA)
        anim[name][key] = dict(x=int(x0), y=int(y0), w=int(x1 - x0), h=int(y1 - y0))
    cv2.imwrite(str(out / f'{name}-art.png'), art); cv2.imwrite(str(out / f'{name}-base.png'), base)
    cv2.imwrite(str(out / f'{name}-water.png'), cv2.GaussianBlur(mask_of(ids, 'water') * 255, (0, 0), 1.2))
    # rotor sprite cycle -> one horizontal strip cropped to the union alpha box
    frames = [cv2.imread(str(exp / f'{name}-rotor-{k:02d}.png'), cv2.IMREAD_UNCHANGED) for k in range(L['rotor_frames'])]
    al = np.max([f[..., 3] for f in frames], axis=0); ys, xs = np.nonzero(al > 0)
    x0, y0, x1, y1 = xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3
    frames = [f[y0:y1, x0:x1] for f in frames]
    if name in HUB:   # same blades about the painted hub: scale around the Blender hub, then translate
        hx, hy = L['views'][name]['hub']; n_ = HUB[name]; s = n_['scale']
        frames = [cv2.resize(f, None, fx=s, fy=s, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC) for f in frames]
        x0, y0 = round(n_['x'] + (x0 - hx) * s), round(n_['y'] + (y0 - hy) * s)
        x1, y1 = x0 + frames[0].shape[1], y0 + frames[0].shape[0]
    cv2.imwrite(str(out / f'{name}-rotor.png'), np.hstack(frames))
    anim[name]['rotor'] = dict(x=int(x0), y=int(y0), w=int(x1 - x0), h=int(y1 - y0), frames=len(frames))
    # tap contours + hotspots from the hard ID (already in overscan pixels)
    regions = {}; hotspots = []
    for g in L['views'][name]['objects']:
        m = cv2.dilate(cv2.morphologyEx(obj(g), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)), np.ones((3, 3), np.uint8))
        ys, xs = np.nonzero(m); grow = TAP_MIN - max(np.ptp(xs), np.ptp(ys))   # true-to-scale robot: tap area ≥ TAP_MIN px
        if grow > 0: m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow | 1, grow | 1)))
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cs = [cv2.approxPolyDP(c, 1, True)[:, 0, :] for c in cs if cv2.contourArea(c) > 2]; assert cs, (name, g)
        _, _, _, p = cv2.minMaxLoc(cv2.distanceTransform(m, cv2.DIST_L2, 5))
        key = g.replace('_', '-')
        regions[key] = {'path': ' '.join('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in c) + ' Z' for c in cs)}
        hotspots.append({'id': key, 'x': p[0] / W, 'y': p[1] / H})
    contours[name] = {'width': W, 'height': H, 'regions': regions, 'source': f'scene-art/lastmile-r5/choice-{name}.webp'}
    # framing = the camera frame the Blender scene was composed for; overscan only fills wider stages
    framing = [{'x': o['x'] / W, 'y': o['y'] / H}, {'x': (o['x'] + o['width']) / W, 'y': (o['y'] + o['height']) / H}]
    artwork[name] = {'width': W, 'height': H, 'original': o, 'framing': framing, 'hotspots': hotspots}
(out / 'registration.json').write_text(json.dumps(report, indent=2) + '\n')
(out / 'expandedArtwork.json').write_text(json.dumps(artwork, indent=2) + '\n')
(out / 'segmentedContours.json').write_text(json.dumps(contours, separators=(',', ':')) + '\n')
(out / 'animation.json').write_text(json.dumps(anim, indent=2) + '\n')
print(json.dumps({n: dict(passed=r['passed'], landmarks={k: (x['dx'], x['dy']) for k, x in r['landmarks'].items()}) for n, r in report.items()}))
