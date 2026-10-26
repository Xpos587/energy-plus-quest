# Scene 1 map v4: smooth lane loops for the game (no Blender needed).
# python3 routes.py   -> rewrites "routes" in src/components/cityV4Manifest.json
#
# layout.py draws the plates; its rect_loop corners are a 10 m quadratic
# fillet that a 1.8x scaled 26 m rig cannot follow without its trailer
# cutting over the kerb (and the houses behind it). Here every corner is a
# swing-wide turn (out a little, then in), and the whole loop is one closed
# uniform cubic B-spline, so position, heading and curvature are continuous:
# no kinks where straights meet corners. The corner shape is tuned once per
# turn type so the swept tractor and trailer keep off every block.
import json
import math
import random
from bisect import bisect_right
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAN = REPO / "src" / "components" / "cityV4Manifest.json"

# Grid, as in layout.py.
P, ROAD, LANE = 64.0, 14.0, 3.2
WB, HB, SA, SB = 84.0, 80.0, 48.0, 44.0


def _line(k, base, side):
    if k == 0:
        return 0.0
    if k == 1:
        return base
    if k == 2:
        return base + side
    if k == -1:
        return -side
    if k > 2:
        return base + side + (k - 2) * P
    return -side + (k + 1) * P


XL = {i: _line(i, WB, SA) for i in range(-8, 12)}
YL = {j: _line(j, HB, SB) for j in range(-8, 12)}
# Block plates (kerb lines): everything a rig must stay off.
BLOCKS = [(XL[i] + ROAD / 2, YL[j] + ROAD / 2, XL[i + 1] - ROAD / 2, YL[j + 1] - ROAD / 2)
          for i in range(-5, 7) for j in range(-4, 6)]

man = json.loads(MAN.read_text())
RIG = man["rig"]


# ---- rig kinematics (same as cityV4.ts rigAt / rigBoxes) ---------------------
class Loop:
    def __init__(self, pts):
        self.pts = pts
        self.cum = [0.0]
        n = len(pts)
        for k in range(1, n + 1):
            a, b = pts[k - 1], pts[k % n]
            self.cum.append(self.cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.L = self.cum[-1]

    def at(self, d):
        d %= self.L
        k = min(bisect_right(self.cum, d) - 1, len(self.pts) - 1)
        a, b = self.pts[k], self.pts[(k + 1) % len(self.pts)]
        span = self.cum[k + 1] - self.cum[k]
        t = (d - self.cum[k]) / span if span else 0
        return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


def rig_polys(r, d):
    fx, fy = r.at(d + RIG["frontAxle"])
    rx, ry = r.at(d + RIG["rearAxle"])
    tr = math.atan2(fy - ry, fx - rx)
    lead = RIG["kingpin"] - RIG["rearAxle"]
    kp = (rx + math.cos(tr) * lead, ry + math.sin(tr) * lead)
    bx, by = r.at(d + RIG["bogie"])
    tl = math.atan2(kp[1] - by, kp[0] - bx)
    k = RIG["kingpin"]
    out = []
    for h, c, hl in ((tr, (RIG["front"] + RIG["tractorRear"]) / 2 - k, (RIG["front"] - RIG["tractorRear"]) / 2),
                     (tl, (RIG["trailerFront"] + RIG["trailerRear"]) / 2 - k, (RIG["trailerFront"] - RIG["trailerRear"]) / 2)):
        cx, cy = kp[0] + math.cos(h) * c, kp[1] + math.sin(h) * c
        cs, sn, w = math.cos(h), math.sin(h), RIG["width"] / 2
        out.append([(cx + cs * u * hl - sn * v * w, cy + sn * u * hl + cs * v * w)
                    for u, v in ((1, 1), (1, -1), (-1, -1), (-1, 1))])
    return out


def gap(poly, R):
    """Separating distance of a convex polygon and a rectangle (<0: overlap)."""
    rc = [(R[0], R[1]), (R[2], R[1]), (R[2], R[3]), (R[0], R[3])]
    axes = [(1, 0), (0, 1)]
    for k in range(4):
        a, b = poly[k], poly[(k + 1) % 4]
        nx, ny = b[1] - a[1], a[0] - b[0]
        n = math.hypot(nx, ny)
        axes.append((nx / n, ny / n))
    best = -1e9
    for ax in axes:
        p = [q[0] * ax[0] + q[1] * ax[1] for q in poly]
        r = [q[0] * ax[0] + q[1] * ax[1] for q in rc]
        best = max(best, min(r) - max(p), min(p) - max(r))
    return best


def clearance(r, step=0.75):
    worst = 1e9
    for i in range(int(r.L / step)):
        for poly in rig_polys(r, i * step):
            cx = sum(q[0] for q in poly) / 4
            cy = sum(q[1] for q in poly) / 4
            for B in BLOCKS:
                if B[0] - 20 < cx < B[2] + 20 and B[1] - 20 < cy < B[3] + 20:
                    worst = min(worst, gap(poly, B))
    return worst


# ---- loops --------------------------------------------------------------------
def bspline(ctrl, per_m=1.0):
    """Closed uniform cubic B-spline, sampled about every per_m metres."""
    n = len(ctrl)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = ctrl[i - 1], ctrl[i], ctrl[(i + 1) % n], ctrl[(i + 2) % n]
        steps = max(2, round(math.dist(p1, p2) / per_m))
        for s in range(steps):
            t = s / steps
            b = ((1 - t) ** 3 / 6, (3 * t**3 - 6 * t * t + 4) / 6, (-3 * t**3 + 3 * t * t + 3 * t + 1) / 6, t**3 / 6)
            out.append((sum(w * q[0] for w, q in zip(b, (p0, p1, p2, p3))),
                        sum(w * q[1] for w, q in zip(b, (p0, p1, p2, p3)))))
    return out


def resample(pts, step):
    r = Loop(pts)
    n = round(r.L / step)
    return [r.at(k * r.L / n) for k in range(n)]


def loop(x0, y0, x1, y1, inset, clockwise, shape):
    """Lane loop around a rectangle of road centre lines; `shape` sets the
    corner: (L1, a, L2, c, L3, b, L4) in metres. L1/L4 start and end the
    turn, a/b swing out before and after it, c pulls the apex towards the
    inner kerb (negative: out into the junction, a wider turn)."""
    x0, y0, x1, y1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    corners = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
    if not clockwise:
        corners = corners[::-1]
    L1, a, L2, c, L3, b, L4 = shape
    ctrl = []
    n = len(corners)
    for k in range(n):
        A, B, C = corners[k - 1], corners[k], corners[(k + 1) % n]
        d1 = ((B[0] - A[0]) / math.dist(A, B), (B[1] - A[1]) / math.dist(A, B))
        d2 = ((C[0] - B[0]) / math.dist(B, C), (C[1] - B[1]) / math.dist(B, C))
        q = lambda u, v: (B[0] + u * d1[0] + v * d2[0], B[1] + u * d1[1] + v * d2[1])
        # mid-street point keeps the straight between corners exactly straight
        ctrl += [q(-math.dist(A, B) / 2, 0), q(-L1, 0), q(-L2, -a), q(-c, c), q(b, L3), q(0, L4)]
    return bspline(ctrl)


def min_radius(pts):
    best = 1e9
    n = len(pts)
    for k in range(n):
        a, b, c = pts[k - 1], pts[k], pts[(k + 1) % n]
        cr = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        if cr > 1e-9:
            best = min(best, math.dist(a, b) * math.dist(b, c) * math.dist(c, a) / (2 * cr))
    return best


# Right-hand traffic (see layout.py): blue and yellow circle their blocks
# clockwise in the inner lane (right turns), green runs the 3x3 ring
# counter-clockwise in the outer lane (left turns).
SPECS = {
    "near": (XL[0], YL[0], XL[1], YL[1], LANE, True),
    "old4": (XL[1], YL[-1], XL[2], YL[2], LANE, True),
    "crew": (XL[-1], YL[-1], XL[2], YL[2], -LANE, False),
}
LO = [8, 0, 4, -14, 4, 0, 8]
HI = [40, 6, 30, 14, 30, 6, 40]
MIN_R = 8.5  # the tractor's own turning circle, roughly
KERB = 1.5  # metres of sidewalk the swept body may cover (sidewalk is 3 m)


def counter_steer(r, step=0.5):
    """Largest wrong-way swing (degrees) of tractor or trailer: a swing-wide
    turn steers away from the corner first; past ~20 deg it reads as a wobble."""
    worst = 0.0
    for part in (0, 1):
        hs = []
        for i in range(int(r.L / step)):
            p = rig_polys(r, i * step)[part]
            hs.append(math.atan2(p[0][1] - p[3][1], p[0][0] - p[3][0]))
        ds = [(hs[(k + 1) % len(hs)] - hs[k] + 3 * math.pi) % (2 * math.pi) - math.pi for k in range(len(hs))]
        sign = 1 if sum(ds) > 0 else -1
        run = 0.0
        for d in ds:
            run = max(0.0, run - d * sign)
            worst = max(worst, run)
    return math.degrees(worst)


def score(ids, shape):
    rs = [loop(*SPECS[i], shape) for i in ids]
    clear = min(clearance(Loop(p)) for p in rs)
    rad = min(min_radius(p) for p in rs)
    wobble = max(counter_steer(Loop(p)) for p in rs)
    # The trailer may sweep up to 1.5 m into the 3 m sidewalk (never the
    # houses); within that, the least wrong-way swing, then gentle corners.
    return (-0.2 * wobble - 20 * max(0, -KERB - clear) - max(0, MIN_R - rad)
            + 0.5 * min(clear, 0.8)), clear, rad


# Last tuned shapes (search starts here, so a rerun only refines them).
START = {"near": [18.68, 1.78, 6.94, 0.77, 7.11, 2.74, 18.58],
         "crew": [30.35, 0, 21.31, 3.6, 11.56, 0, 23.31]}


def tune(ids, iters, seed=1):
    random.seed(seed)
    cur = START[ids[0]]
    cs = score(ids, cur)
    for it in range(iters):
        T = 1 - it / iters
        q = [min(h, max(l, v + random.gauss(0, (h - l) * 0.1 * T + 0.15))) for v, l, h in zip(cur, LO, HI)]
        qs = score(ids, q)
        if qs[0] > cs[0]:
            cur, cs = q, qs
    return [round(v, 2) for v in cur], cs


if __name__ == "__main__":
    import sys

    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    out = {}
    for ids in (("near", "old4"), ("crew",)):
        shape, (_, clear, rad) = tune(ids, iters)
        wb = [round(counter_steer(Loop(loop(*SPECS[i], shape))), 1) for i in ids]
        print(ids, "shape", shape, "kerb clearance %.2f m, min radius %.1f m, counter-steer %s deg" % (clear, rad, wb))
        for i in ids:
            out[i] = [[round(x, 3), round(y, 3)] for x, y in resample(loop(*SPECS[i], shape), 0.75)]
    man["routes"].update(out)
    man["routeShapes"] = "routes.py"
    man.pop("occluders", None)
    MAN.write_text(json.dumps(man, separators=(",", ":")))
    print({k: (len(v), round(Loop([tuple(p) for p in v]).L, 1)) for k, v in out.items()})
