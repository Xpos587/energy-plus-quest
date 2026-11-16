"""R5 scene-5 world = the approved R4 composition (scripts/lastmile-r4/build.py) with:
perspective cameras, choices in one row on a sandy clearing (heli on a round pad),
explicit peat bog + mud rut trail, cobalt water with first ice, ochre ground, no trees,
the scene-4 barge (design/scene-04/blender-v4/quay.py:535-593, smoke omitted), clear daylight.
Landmarks (river spline, bog band, chums, ABK, rig, helipad, quay) keep the R4 positions.
blender -b --factory-startup --python-exit-code 1 -t 12 --python scripts/lastmile-r5/build.py -- <out> preview|final
"""
import bpy, math, random, sys, json
from pathlib import Path
from mathutils import Vector, Matrix, noise
from mathutils.kdtree import KDTree
from bpy_extras.object_utils import world_to_camera_view
OUT = Path(sys.argv[sys.argv.index('--') + 1]).resolve(); OUT.mkdir(parents=True, exist_ok=True)
MODE = sys.argv[-1] if sys.argv[-1] in ('preview', 'final', 'gate') else 'preview'
FL = {'final': 1, 'preview': .6, 'gate': 0}[MODE]   # flora density; 'gate' = layout/overlap check only
DY = -98                                            # R5-05e (Michael r10: spread the world out): bog, river and camp 10 m farther so the pad can hold a compact 2x2 vehicle group; was -119.
# R5-05d (Grisha: scale too large): far bank another 30 m closer, helipad beside the ABK, -114 for the cropped close wide (Grisha/coordinator: wide vehicles >= R5-05c size); was -74
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lastmile-r4'))
bpy.ops.wm.read_factory_settings(use_empty=True)
import helpers as h
from helpers import box, aabb, cyl, ball, beam, at, srgb, flush, MAT, GROUPS, ORANGE
_batch = h._bm
def _bounded_bm(group, color, mat, nolines):   # bmesh ops scale with the target mesh: cap batches (flora was O(n^2))
    b = h.BATCH.get((group, color, mat, nolines))
    if b is not None and len(b.verts) > 30000: flush()
    return _batch(group, color, mat, nolines)
h._bm = _bounded_bm
scene = bpy.context.scene
random.seed(11011)
rad = math.radians


def mesh(group, color, vertices, faces, mat='obj', transform=None, smooth=False):
    if transform: vertices = [transform @ Vector(v) for v in vertices]
    me = bpy.data.meshes.new(group); me.from_pydata(vertices, [], faces); me.materials.append(MAT[mat])
    ob = bpy.data.objects.new(group, me); scene.collection.objects.link(ob)
    ob.color = srgb(color); ob['group'] = group
    for p in me.polygons: p.use_smooth = smooth
    GROUPS.setdefault(group, []).append(ob)
    return ob


# ---- materials: toon response from helpers, softer warm/cool ramp, no ink ---------
def soft(name, build, ramp=(.62, .84, 1)): return h.toon(name, build, ramp=ramp)
def attr_color(nt):
    a = nt.nodes.new('ShaderNodeAttribute'); a.attribute_name = 'col'
    g = nt.nodes.new('ShaderNodeNewGeometry'); n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = .7; n.inputs['Detail'].default_value = 4
    nt.links.new(g.outputs['Position'], n.inputs['Vector'])
    grain = h.mnode(nt, 'ADD', h.mnode(nt, 'MULTIPLY', n.outputs['Fac'], .3), .85)
    c = nt.nodes.new('ShaderNodeCombineColor')
    for i in range(3): nt.links.new(grain, c.inputs[i])
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
    mul.inputs[0].default_value = 1
    nt.links.new(a.outputs['Color'], mul.inputs[6]); nt.links.new(c.outputs[0], mul.inputs[7])
    return mul.outputs[2]
MAT['ground'] = soft('ochre ground', attr_color)
def water_mat(name, c0, c1, glint, scale):
    def surface(nt):
        p = h.pos(nt); tc = nt.nodes.new('ShaderNodeCombineXYZ')
        nt.links.new(h.mnode(nt, 'MULTIPLY', p.outputs[0], scale[0]), tc.inputs[0])
        nt.links.new(h.mnode(nt, 'MULTIPLY', p.outputs[1], scale[1]), tc.inputs[1])
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 1.2; n.inputs['Detail'].default_value = 2
        nt.links.new(tc.outputs[0], n.inputs['Vector'])
        base = h.mix(nt, n.outputs[0], srgb(c0), srgb(c1))
        ripple = h.band(nt, h.mnode(nt, 'MULTIPLY', n.outputs[0], 5), 0, .045)
        return h.mix(nt, h.mnode(nt, 'MULTIPLY', ripple, .4), base, srgb(glint))
    MAT[name] = h.toon(name, surface, ramp=(.9, .96, 1))
water_mat('cobalt', '#3F7FB8', '#5C9AC9', '#B9D6EE', (.035, .12))   # R5-05c: scene-4 steel blue (was #1E56B4/#3B80D6)
water_mat('peat', '#2A2116', '#463626', '#8C7B5C', (.06, .2))   # R5-05d (coordinator): murky brown peat water, not blue lakes
MAT['canvas'] = MAT['paving']


# R4 heli kept as-is (Michael: ignore the livery stripes for now).
def heli_swoosh(group, side, transform):
    centers = []
    for cx, cz, start, stop in ((2.0, 3.05, 2.1, -1.9), (1.8, 2.12, 1.6, -2.0)):
        for i in range(23):
            t = start + (stop - start) * i / 22
            centers.append((cx + 1.12 * math.cos(t), cz + .57 * math.sin(t)))
    vs = []
    for i, (x, z) in enumerate(centers):
        a = Vector(centers[max(0, i - 1)]); b = Vector(centers[min(len(centers) - 1, i + 1)])
        d = (b - a).normalized(); n = Vector((-d.y, d.x)) * .135
        for sign in (-1, 1):
            xx, zz = x + n.x * sign, z + n.y * sign
            yy = side * (1.95 * math.sqrt(max(.04, 1 - ((xx - 1.2) / 6.2) ** 2 - ((zz - 2.4) / 1.95) ** 2)) + .13)
            vs.append((xx, yy, zz))
    faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(centers) - 1)]
    if side < 0: faces = [tuple(reversed(f)) for f in faces]
    mesh(group, '#F6F5F0', vs, faces, transform=transform)
h.heli_swoosh = heli_swoosh


def smooth01(a, b, x):
    t = max(0., min(1., (x - a) / (b - a))); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def lerpc(a, b, t): return tuple(lerp(x, y, t) for x, y in zip(a, b))
def N(x, y, f, s=0.): return noise.noise(Vector((x * f, y * f, s)))
def catmull(knots, step=20):
    pts = []
    for k in range(len(knots) - 1):
        a, b, c, d = (Vector(knots[max(0, k - 1)]), Vector(knots[k]), Vector(knots[k + 1]), Vector(knots[min(len(knots) - 1, k + 2)]))
        for i in range(step):
            t = i / step
            pts.append(.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3))
    pts.append(Vector(knots[-1])); return pts
def dense(pts, step=.5):
    out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int((b - a).length / step))
        out += [a.lerp(b, i / n) for i in range(n)]
    return out + [pts[-1]]
def frange(a, b, s):
    v = []; x = a
    while x < b: v.append(x); x += s
    return v
def kd(points):
    t = KDTree(len(points))
    for i, p in enumerate(points): t.insert((p.x, p.y, 0), i)
    t.balance(); return t
C = {k: srgb(v)[:3] for k, v in dict(gold='#C9A24C', ochre='#B3873A', straw='#DCBD6C', olive='#A29548',
     sand='#DCC69A', sand2='#CDAF7E', moss='#6F6A36', bogrust='#86602F', mud='#6A4F33', rut='#4E3B28', slurry='#735A3D', wetrut='#2E2318',
     wet='#8F7E5C', frost='#E4ECEF', bed='#2B4A6A', peat='#4A3826', bank='#6E5434').items()}

# ---- R4 geography (unchanged): inland river spline, bog band, harbour shore -----
knots = [(x, y + DY) for x, y in ((2700, 100), (1600, 95), (1000, 110), (600, 98), (360, 104), (112, 101), (50, 105), (-12, 111), (-62, 140), (-90, 191), (-78, 250), (-45, 330), (-15, 410), (20, 520), (55, 640), (90, 760), (130, 900), (190, 1100), (260, 1400), (330, 1800), (420, 2400), (500, 3100))]   # R5-05d r3: river runs on past the overscan
river = catmull(knots)
RIVER = kd(dense(river))
def river_dist(x, y): return RIVER.find((x, y, 0))[2]
# R5-05: bog ends >= 14 m before the river bank (Michael r6: the river must not run into the bog)
def wet_limits(x): return (PAD[3] + 3 + 1.5 * math.sin(x * .037) + .8 * math.sin(x * .19) + .5 * math.sin(x * .43), DY + 104 + 3 * math.sin(x * .045 + 1) + 2 * math.sin(x * .22))   # R5-05e (coordinator r10): mire from the pad's gravel strip right to the river bank
def shore(x): return -77 if -78 < x < 66 else -77 + 3 * math.sin(x * .04)

# ---- R5 additions: row clearing, heli pad, rut trail, side creek, peat pools ----
# R5-05: true metric vehicles (helpers models are ~1 unit = 1 m) parked on a road-slab pad behind the quay.
import os
QY = -69                                                     # R5-05b: quay back edge (deck 12 m, was 20 m) — pad sits right at the barge
ROW_Y = QY + 9
PAD = (-81, QY, -8, QY + 29)                                   # road-slab pad x0, y0, x1, y1; R5-05e: short and deep for the compact group
HP = (-50, QY + 9)                                              # heli marking on the slabs (rotor d = 21 m)
# R5-05e (Michael r10: vehicles in one tight group): 2x2 beside the helideck. Tall screen axes at yaw -38: u = .79x - .62y, v = .62x + .79y;
# pipe carrier right of the heli (along the view), robot above the heli, RUSAK above the carrier -> rings/labels clear in both views.
ROW = {'pipe_carrier': (-28, -43.5), 'rover': (-13.3, -55.5), 'robot': (-76.5, -58)}   # R5-05e (coordinator r10) gate g16l: tight group round the helideck, text-sized labels above/below
ROT = {'pipe_carrier': math.radians(-128), 'rover': math.radians(-38), 'robot': math.radians(-38)}
if os.environ.get('ROWXY'): ROW.update(json.loads(os.environ['ROWXY']))   # tuning aid
HERD = (-6, DY + 152)   # R5-05e: herd beside the moved chums
FACE = math.radians(-38); FC, FS = math.cos(FACE), math.sin(FACE)
# R5-05 (review: "buildings must stand in the terrain, not on rectangular pads"): camp ground = organic trampled
# blobs (final positions after FAR moves) instead of sand/paving boxes; slab pad gets a ragged gravel apron.
CAMP = [(40, DY + 150, 42, 25), (105, DY + 180, 28, 22), (10, DY + 205, 21, 19), (-22, DY + 167, 14, 11)]   # ABK, rig yard, helipad, chums; R5-05e (Michael r10): ABK 22 m off the river, helipad ~45 m from the chums
AX, AY = 40, 152 + DY
ROAD = kd(dense(catmull([(AX, AY - 20), (AX - 22, AY - 23), (-2, DY + 150), (-4, DY + 175), (6, DY + 190)], 20)))   # porch -> camp road -> helipad
def clearing(x, y):                                         # 1 on the slab pad, the camp and the herd patch
    pad = smooth01(3.2 + .6 * N(x, y, .12, 12), 2.2, max(PAD[0] - x, x - PAD[2], PAD[1] - y, y - PAD[3]))   # R5-05d: neat ~3 m gravel strip, straight edge
    r = min(math.hypot((x - cx) / rx, (y - cy) / ry) for cx, cy, rx, ry in CAMP)
    r = min(r, math.hypot((x - HERD[0]) / 16, (y - HERD[1]) / 11))
    road = smooth01(3.4, 2.2, ROAD.find((x, y, 0))[2] + .4 * N(x, y, .2, 19))
    return max(pad, road, smooth01(1.05, .8, r + .16 * N(x, y, .045, 7) + .06 * N(x, y, .2, 13)))
TX = ROW['rover'][0]
TY1 = next(y for y in frange(PAD[3], PAD[3] + 80, .5) if river_dist(TX + 2.5, y) < 11.5)   # R5-05e (Michael r10): the churned road crosses the whole bog to the river bank
trail = dense(catmull([(TX + .3 * math.sin(k * 1.7) + 2.2 * (k % 2), PAD[3] - 1 + (TY1 - PAD[3] + 1) * k / 5) for k in range(6)], 30))
_tn = [(trail[min(i + 1, len(trail) - 1)] - trail[max(i - 1, 0)]).normalized() for i in range(len(trail))]
trail2 = [p + Vector((-d.y, d.x)) * (3.0 + 1.3 * math.sin(i * .045)) for i, (p, d) in enumerate(zip(trail, _tn))][40:]   # second braided track (vehicles swerving round the worst holes)
TRAIL, TRAIL2 = kd(trail), kd(trail2)
def trail_dist(x, y): return min(TRAIL.find((x, y, 0))[2], TRAIL2.find((x, y, 0))[2])
def creek_dist(x, y): return 99                             # R5-05: side creek removed
pools = [(q.x + 1.5, q.y, 2.8, 1.8, .3, 1.1) for q in (trail[int(len(trail) * f_)] for f_ in (.3, .55, .8))]   # R5-05e: flooded potholes on the road
for i in range(3000):
    if len(pools) >= 130: break
    x = random.uniform(-150, 210); lo, hi = wet_limits(x); y = random.uniform(lo + 3, hi - 3)
    rx = random.uniform(5, 12); ry = rx * random.uniform(.4, .7)
    if not (lo + ry + 1 < y < hi - ry - 1) or trail_dist(x, y) < rx + 6 or river_dist(x, y) < rx + 12: continue
    if any(math.hypot(x - p[0], y - p[1]) < (rx + p[2]) * .6 for p in pools): continue   # overlap allowed: pools merge into chains
    pools.append((x, y, rx, ry, random.uniform(0, math.tau), random.uniform(0, math.tau)))
POOLS = kd([Vector((p[0], p[1], 0)) for p in pools])
def pool_r(p, x, y):
    a = math.atan2(y - p[1], x - p[0]); w = 1 + .16 * math.sin(3 * a + p[4]) + .09 * math.sin(5 * a + p[5])
    c, s = math.cos(p[4] * .3), math.sin(p[4] * .3); dx, dy = x - p[0], y - p[1]
    return math.hypot((c * dx + s * dy) / (p[2] * w), (-s * dx + c * dy) / (p[3] * w))
def min_pool_r(x, y):
    return min([pool_r(pools[i], x, y) for _, i, _ in POOLS.find_range((x, y, 0), 22)] or [9])


def ground(x, y):
    """One shared terrain: height and colour (R4 heights for dry land and water)."""
    col = lerpc(C['gold'], C['ochre'], smooth01(-.4, .5, N(x, y, .016, 2)))
    col = lerpc(col, C['straw'], .5 * smooth01(.2, .6, N(x, y, .05, 4)))
    col = lerpc(col, C['olive'], .45 * smooth01(.3, .7, N(x, y, .022, 5)))
    z = .07 * math.sin(x * .19) * math.sin(y * .16) + .12 * N(x, y, .08, 1)
    s = clearing(x, y)
    if s:                                                    # trampled earth + gravel, darker wheel-worn patches
        z = lerp(z, .02, s); g = lerpc(C['sand'], C['sand2'], smooth01(-.5, .5, N(x, y, .07, 8)))
        g = lerpc(g, srgb('#A99C86')[:3], .45 * smooth01(.1, .5, N(x, y, .11, 14))); g = lerpc(g, C['mud'], .25 * smooth01(.35, .6, N(x, y, .06, 15)))
        col = lerpc(col, g, s)
    lo, hi = wet_limits(x)
    edge = min(y - lo, hi - y) + 3 * N(x, y, .06, 3)
    m = smooth01(-4, 3, edge) * smooth01(11, 12.5, river_dist(x, y)) * (1 - clearing(x, y))   # dry strip at the river, gravel strip at the pad
    if m:
        col = lerpc(col, C['rut'], .45 * smooth01(-3, -.5, edge) * smooth01(3, .5, edge))   # dark wet border line
        z = lerp(z, -.05 + .14 * max(0, N(x, y, .3, 9)), m)
        bogc = lerpc(C['moss'], C['bogrust'], smooth01(-.2, .4, N(x, y, .05, 10)))
        bogc = lerpc(bogc, C['mud'], .8 * smooth01(.25, .55, N(x, y, .09, 11)))
        bogc = lerpc(bogc, C['peat'], .55 * smooth01(-.1, .35, N(x, y, .07, 16)))   # R5-05d: darker, reads as a mire
        col = lerpc(col, bogc, m * .95)
        r = min_pool_r(x, y)
        if r < 1.7:                                             # pool: dark water with a raised peat lip
            lip = smooth01(1.7, 1.25, r) * smooth01(.92, 1.1, r)
            z = lerp(-.6, z + .32 * lip, smooth01(.88, 1.0, r))
            col = lerpc(C['peat'], col, smooth01(1.0, 1.65, r))
    t1, t2 = TRAIL.find((x, y, 0))[2], TRAIL2.find((x, y, 0))[2]; td = min(t1, t2)
    if td < 13 and y > PAD[3] - 1:   # R5-05e (Michael r10: the road must look terrible): wide churned slurry, two braided tracks, deep water-filled ruts, torn turf
        mud = smooth01(13, 6, td + 3 * N(x, y, .1, 11)) * smooth01(PAD[3] - 1, PAD[3] + 3, y)
        col = lerpc(col, lerpc(C['slurry'], C['mud'], smooth01(-.3, .4, N(x, y, .3, 17))), mud)
        rut = max(smooth01(1.1, .3, abs(t1 - 1.6)), .9 * smooth01(1.0, .3, abs(t2 - 1.5))) * smooth01(PAD[3] - 1, PAD[3] + 2, y)
        berm = max(smooth01(1.2, .35, abs(abs(t1 - 1.6) - 1.15)), smooth01(1.1, .35, abs(abs(t2 - 1.5) - 1.1))) * mud
        z += .35 * berm * (1 + .7 * N(x, y, .6, 18)) - .75 * rut
        col = lerpc(col, C['moss'], .7 * berm * smooth01(.25, .45, N(x, y, .9, 21)))   # torn turf clods on the berms
        col = lerpc(col, C['wetrut'], rut)
    # water: R4 harbour shore and river bed; side creek is new and narrow
    rd = river_dist(x, y); cd = creek_dist(x, y); sh = y - shore(x)
    e = min(rd - 10.5, cd - 4.5, sh)
    if sh < 0: return -2.2, C['bed']
    if rd < 7: return -1.4, C['bed']
    if rd < 10.5: z = min(z, -1.4 + .42 * (rd - 7)); col = lerpc(C['bank'], col, smooth01(9.6, 10.6, rd))   # cut bank
    if cd < 4.5: z = min(z, -.95 + .4 * max(0, cd - 2)); col = lerpc(C['bank'], col, smooth01(3.8, 4.6, cd))
    if e < 6:
        frost = smooth01(.0, .35, N(x, y, .13, 12)) * smooth01(4, 1, e)
        col = lerpc(lerpc(C['wet'], col, smooth01(0, 6, e)), C['frost'], frost)
    if min(rd - 9.1, cd - 3.2, sh) < 0: col = C['bed']
    return z, col


# ---- terrain mesh (R4 grid extents) with per-vertex colour ------------------------
f = {'final': 1.0, 'preview': 1.5, 'gate': 6}[MODE]
# R5-05d r3 (coordinator: no world edge in any overscan): coarse tundra out to 2.6-3 km that slowly rises beyond 850 m
# from the cameras, so even the wide overscan's top row (+0.2 deg at tilt 40) meets ground; the original frames are unchanged
def rise(x, y): return 6e-5 * max(0, math.hypot(x + 25, y + 117) - 850) ** 2 * smooth01(-69, 60, y)
xs = frange(-2600, -340, 12) + frange(-340, -240, 4) + frange(-240, TX - 16, f) + frange(TX - 16, TX + 20, .35 * f) + frange(TX + 20, 241, f) + frange(244, 361, 4) + frange(372, 2601, 12)
ys = frange(-450, -90, 4) + frange(-90, PAD[3] - 2, f) + frange(PAD[3] - 2, TY1 + 3, .35 * f) + frange(TY1 + 3, 301, f) + frange(304, 701, 4) + frange(712, 3101, 12)   # R5-05e: fine grid under the ruts
vs = []; cols = []
for y in ys:
    for x in xs:
        z, c = ground(x, y); vs.append((x, y, z + rise(x, y))); cols.extend((*c, 1))
nx = len(xs)
terrain = mesh('tundra', '#FFFFFF', vs, [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(len(ys) - 1) for i in range(nx - 1)], 'ground', smooth=True)
terrain.data.color_attributes.new('col', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', cols)
aabb('harbor_water', '#2F6BC0', -340, -450, -1.3, 360, -69, -1.22, mat='cobalt')
rv = []
for i, p in enumerate(river):
    d = (river[min(i + 1, len(river) - 1)] - river[max(0, i - 1)]).normalized(); n = Vector((-d.y, d.x)) * 10.1
    rv.extend([(p.x + n.x, p.y + n.y, rise(p.x + n.x, p.y + n.y) - .5), (p.x - n.x, p.y - n.y, rise(p.x - n.x, p.y - n.y) - .5)])
mesh('river', '#2F6BC0', rv, [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(river) - 1)], 'cobalt')
for p in pools:
    ring = [(p[0] + math.cos(j * math.tau / 32) * p[2] * 1.3, p[1] + math.sin(j * math.tau / 32) * p[2] * 1.3, -.2) for j in range(32)]
    mesh('peat_pools', '#FFFFFF', ring + [(p[0], p[1], -.2)], [(j, (j + 1) % 32, 32) for j in range(32)], 'peat')
for tr, off in ((trail, 1.6), (trail2, 1.5)):                # R5-05e: standing water along both ruts of both tracks
    for i in range(0, len(tr) - 1, 4):
        a, b = tr[i], tr[i + 1]
        if a.y < PAD[3] + 1 or random.random() > .8: continue
        d = (b - a).normalized(); nn = Vector((-d.y, d.x))
        for side in (-1, 1):
            if random.random() > .75: continue
            c = a + nn * side * off; L = random.uniform(1.4, 3.2)
            ring = [c + d * math.cos(j * math.tau / 12) * L + nn * math.sin(j * math.tau / 12) * .5 for j in range(12)]
            mesh('peat_pools', '#FFFFFF', [(v.x, v.y, -.42) for v in ring] + [(c.x, c.y, -.42)], [(j, (j + 1) % 12, 12) for j in range(12)], 'peat')

# ---- first ice: floes on cobalt water, shelf ice along banks ----------------------
ice_v = []; ice_top = []; ice_side = []
def floe(x, y, r, elong, ang, ztop, zbot):
    n = 18; base = len(ice_v); ph = [random.random() * 6 for _ in range(4)]   # R5-05e (coordinator: floes read as hexagon tiles): irregular broken outlines
    amp = [random.uniform(.1, .28), random.uniform(.05, .16), random.uniform(.03, .1), random.uniform(.02, .06)]
    jit = [random.uniform(-.09, .09) for _ in range(n)]
    for zz in (zbot, ztop):
        for j in range(n):
            a = j * math.tau / n; rr = r * (1 + sum(amp[k] * math.sin((k + 1) * a + ph[k]) for k in range(4)) + jit[j])
            dx, dy = math.cos(a) * rr * elong, math.sin(a) * rr
            ice_v.append((x + dx * math.cos(ang) - dy * math.sin(ang), y + dx * math.sin(ang) + dy * math.cos(ang), zz))
    ice_top.append(tuple(base + n + j for j in range(n)))
    ice_side.extend((base + j, base + (j + 1) % n, base + n + (j + 1) % n, base + n + j) for j in range(n))
BS, BX = .9, -29   # R5-05d r2: 8 m left so the phone frame shows the wheelhouse; R5-05b (Michael r7 "barge only giant"; coordinator: ~40-45 m ≈ 3 pipe carriers, game scale); was 2.2
BARGE_BOX = (BX - 18 * BS, -77.3 - 15 * BS, BX + 34 * BS, -76)
placed = []
for i in range(3500):
    x = random.uniform(-260, 300); y = random.uniform(-260, -80)
    if BARGE_BOX[0] < x < BARGE_BOX[2] and BARGE_BOX[1] < y < BARGE_BOX[3]: continue
    r = random.uniform(.3, 1.1) if random.random() < .8 else random.uniform(1.1, 2.6)   # R5-05e: brash to 5 m pans, natural spread
    if any((x - a) ** 2 + (y - b) ** 2 < (r + c + 1.2) ** 2 for a, b, c in placed): continue
    if random.random() > (.75 if y > shore(x) - 25 else .3): continue
    placed.append((x, y, r)); floe(x, y, r, random.uniform(1, 1.8), random.uniform(0, math.pi), -.85, -1.5)   # R5-05e: low freeboard
for x in frange(-260, 300, 4.5):
    if -82 < x < 70: continue
    if random.random() < .75: floe(x, shore(x) - random.uniform(1, 2.5), random.uniform(1, 2), 1.7, random.uniform(-.2, .2), -.8, -1.5)
for i in range(4, len(river) - 4, 2):
    p = river[i]
    if random.random() < .55:
        side = random.choice((-.75, -.3, 0, .3, .75)); d = (river[i + 1] - river[i - 1]).normalized(); n = Vector((-d.y, d.x))
        floe(p.x + n.x * 7 * side, p.y + n.y * 7 * side, random.uniform(1, 2.4), 1.4, math.atan2(d.y, d.x), -.2, -.62)
rd_ = dense(river, 3.2)
for i in range(1, len(rd_) - 1):                            # shelf ice edging both river banks
    d = (rd_[i + 1] - rd_[i - 1]).normalized(); n = Vector((-d.y, d.x))
    for side in (-1, 1):
        if random.random() < .62:
            q = rd_[i] + n * side * random.uniform(8.2, 9.0)
            floe(q.x, q.y, random.uniform(1.2, 2.2), 2.0, math.atan2(d.y, d.x), -.3, -.7)
mesh('ice', '#EEF4F7', ice_v, ice_top, 'flat')
mesh('ice', '#C9DAE4', ice_v, ice_side, 'flat')   # R5-05e: softer edges, no hard blue rim

# ---- R4 quay (unchanged) and the scene-4 barge -----------------------------------
aabb('quay', '#A88358', -78, -76, -1.2, 66, QY, .14)                      # timber deck
for x in frange(-77.1, 66, 1.8): aabb('quay', '#7E5E3F', x, -75.9, .14, x + .14, QY - .2, .17)
for x in (-78, 64.6): aabb('quay', '#6E5238', x, -76, -1.2, x + 1.4, QY, .3)
aabb('quay', '#5B6467', -78.4, -77.2, -2.6, 66.4, -75.8, .34)                # steel cap + sheet piles
for x in frange(-78, 66, 1.2): aabb('quay', '#47525A', x, -77.6, -2.6, x + .6, -77.1, .2)
for x in range(-70, 66, 13):
    cyl('quay', '#2F383C', (x, -74.4, .75), .5, 1.2, seg=14)
    cyl('quay', '#2F383C', (x, -74.4, 1.4), .75, .25, seg=14)
    cyl('quay', '#2B2F31', (x + 6.5, -77.9, -.55), 1.0, .6, axis='Y', seg=18)


# Scene-4 frame: quay face y=0, quay top z=0, waterline z=-2 → R4 quay face y=-77, water z=-1.22.
BZW = -1.22 + 2 * BS
BM = Matrix.Translation((BX, -77.3, BZW)) @ Matrix.Scale(BS, 4)
# Approved scene-4 barge geometry, appended read-only from the scene-4 blend (same frame as quay.py).
with bpy.data.libraries.load(str(Path(__file__).resolve().parents[2] / 'design/scene-04/blender-v4/quay.blend'), link=False) as (src, dst):
    dst.collections = ['Barge - approved geometry']
assert dst.collections[0], 'barge collection missing'
scene.collection.children.link(dst.collections[0])
for ob in dst.collections[0].all_objects:
    ob.matrix_world = BM @ ob.matrix_world; ob['group'] = 'barge'; GROUPS.setdefault('barge', []).append(ob)
    for slot in ob.material_slots: slot.material = MAT['glass' if slot.material.name.startswith('glass') else 'obj']
assert len(GROUPS['barge']) == 12, len(GROUPS['barge'])
for lx in (-12, 28): beam('mooring', '#5D5A50', BM @ Vector((lx, -2.6, -.4)), (BX + lx * BS + 5, -74, 1.0), .16)
# Gift stays on the quay (R4 place): scene-4 tan box and red ribbon.
GX, GY = -12, -72.6                                                         # R5-05: gift ~2.4 m box (was 7 m)
box('gift', '#C79A5B', (GX, GY, .3), (3, 3, .3))
k = 1.15
def gb(x0, y0, z0, x1, y1, z1, c): aabb('gift', c, GX + x0 * k, GY + y0 * k, .5 + (z0 - .3) * k, GX + x1 * k, GY + y1 * k, .5 + (z1 - .3) * k)
gb(-1.05, -1.05, .3, 1.05, 1.05, 2, '#E2B977')
gb(-.18, -1.08, .3, .18, 1.08, 2.03, '#D62B2B')
gb(-1.08, -.18, .3, 1.08, .18, 2.03, '#D62B2B')
zt = .5 + 1.73 * k
for a in (.6, -.6, math.pi - .6, math.pi + .6):
    ball('gift', '#E53935', (GX + .42 * k * math.cos(a), GY + .42 * k * math.sin(a), zt + .17 * k), .38 * k, sy=.55, sz=.5, sub=2)
ball('gift', '#B71C1C', (GX, GY, zt + .12 * k), .2 * k)

# ---- choices: R4 models and scales; one row on the clearing, heli on a round pad ----
# R5-05 true sizes (Michael r6: Mi-8 > pipe carrier > RUSAK >> robot, all in proportion with the ABK):
# Mi-8 26 m incl. 21 m rotor, pipe carrier 13 m, RUSAK 7.3 m, robot cart 3.5 m.
PZ = .2                                                                  # slab top
# R5-05c (Michael r8: "a real helipad, not a circle on slabs"): raised 26 x 17 m concrete helideck at the pad's
# west end: white FATO edge, yellow TD/PM circle, white H, green perimeter lights, tie-downs, steps, windsock.
DZ = .9                                                                  # deck top
HD = (HP[0] - 13, QY + .5, HP[0] + 13, QY + 17.5)
h.heli('helicopter', at(HP[0], HP[1], rad(28), 1.0, DZ))
h.pipe_carrier('pipe_carrier', at(*ROW['pipe_carrier'], ROT['pipe_carrier'], 1.0, PZ))
h.rusak('rover', at(*ROW['rover'], ROT['rover'], .8, PZ))
h.robot('robot', at(*ROW['robot'], ROT['robot'], 1.0, PZ))
for j, y in enumerate(frange(PAD[1], PAD[3] - .1, 2.1)):               # road slabs 6 x 2 m, staggered rows
    for x in frange(PAD[0] + (3 if j % 2 else 0) - 3, PAD[2], 6.1):
        x0, x1 = max(x, PAD[0]), min(x + 6, PAD[2])
        if y < HD[3] + .5 and x1 > HD[0] - .6 and x0 < HD[2] + .6:   # R5-05e: slabs on both sides of the helideck, not under it
            if x0 < HD[0] - .6: x1 = HD[0] - .6
            else: x0 = max(x0, HD[2] + .6)
        edge = min(x0 - PAD[0], PAD[2] - x1, y - PAD[1], PAD[3] - y - 2) < 1
        if x1 - x0 > .5:                                               # R5-05d: complete slab edge (ragged edge read as a bug)
            aabb('slab_pad', random.choice(('#B9B6AE', '#AFACA4', '#C2BFB6', '#A9A69E')), x0, y, -.2, x1, y + 2, PZ, mat='paving')
aabb('helideck', '#8F9096', *HD[:2], -.3, *HD[2:], DZ - .12)               # plinth
aabb('helideck', '#3A3D42', HD[0] - .12, HD[1] - .12, DZ - .3, HD[2] + .12, HD[3] + .12, DZ - .12)   # steel edge band
for i, x in enumerate(frange(HD[0], HD[2] - .1, 3.25)):                  # 3.25 x 3.4 m deck slabs
    for j, y in enumerate(frange(HD[1], HD[3] - .1, 3.4)):
        aabb('helideck', ('#CFCCC4', '#C7C4BC', '#D3D0C8')[(i * 7 + j * 3) % 3], x + .04, y + .04, DZ - .14, x + 3.21, y + 3.36, DZ, mat='paving')
for x0, y0, x1, y1 in ((HD[0] + .3, HD[1] + .3, HD[2] - .3, HD[1] + .8), (HD[0] + .3, HD[3] - .8, HD[2] - .3, HD[3] - .3),
                       (HD[0] + .3, HD[1] + .3, HD[0] + .8, HD[3] - .3), (HD[2] - .8, HD[1] + .3, HD[2] - .3, HD[3] - .3)):
    aabb('helideck', '#F4F1E6', x0, y0, DZ, x1, y1, DZ + .02, mat='flat')   # FATO/TLOF edge
for k2 in range(72):                                                     # yellow touchdown/positioning circle
    a = k2 * math.tau / 72
    box('helideck', '#F2C230', (HP[0] + 6 * math.cos(a), HP[1] + 6 * math.sin(a), DZ + .01), (.56, .6, .02), rot=a + math.pi / 2, mat='flat')
for x in (-1.4, 1.4): box('helideck', '#F4F1E6', (HP[0] + x, HP[1], DZ + .015), (.7, 4.2, .02), mat='flat')   # H
box('helideck', '#F4F1E6', (HP[0], HP[1], DZ + .015), (2.1, .7, .02), mat='flat')
for x in frange(HD[0] + .5, HD[2], 3.2):                                 # green perimeter lights
    for y in (HD[1] + .15, HD[3] - .15): cyl('helideck', '#36C46A', (x, y, DZ + .12), .16, .24, seg=10, mat='flat')
for y in frange(HD[1] + 3, HD[3] - 1, 3.4):
    for x in (HD[0] + .15, HD[2] - .15): cyl('helideck', '#36C46A', (x, y, DZ + .12), .16, .24, seg=10, mat='flat')
for a in range(8):                                                       # tie-down points
    cyl('helideck', '#2E3136', (HP[0] + 8.6 * math.cos(a * math.tau / 8 + .2), HP[1] + 7 * math.sin(a * math.tau / 8 + .2), DZ + .01), .22, .03, seg=12, mat='flat')
for s in range(4):                                                       # steps down to the quay side
    aabb('helideck', '#9A9BA0', HD[2] - 4.5, HD[1] - .4 - .45 * (3 - s), -.2, HD[2] - 2.5, HD[1] - .4 - .45 * (2 - s), PZ + (DZ - PZ) * s / 4)
WS = (HD[2] + 2.2, HD[3] - 1.2)                                         # windsock mast between deck and pipe carrier
beam('helideck', '#E9EBE6', (WS[0], WS[1], PZ), (WS[0], WS[1], PZ + 6), .14)
for k2 in range(5): cyl('helideck', ('#E8884B', '#F4F1E6')[k2 % 2], (WS[0] + .35 + k2 * .5, WS[1], PZ + 5.75), .42 - k2 * .05, .5, axis='X', r2=.37 - k2 * .05, seg=14)

# ---- far bank (R4 layout): ABK redrawn in the game palette; rig, helipad, chums enlarged after flush ----
# Scale ratio: rover ~10 m tall vs 2-storey ABK ~20 m (ridge) and chums ~19 m, so the near row no longer dwarfs them.
from helpers import BLUE, NAVY
# Vahta camp (ref design/scene-05/r4/refs/photo_2026-11-10_15-04-34.jpg): white/blue modular container blocks on a sand pad.
WHITE, SEAM, GLASS = '#F4F6F8', '#3B4350', '#9CC3E8'
def abk(x0, y0, z0, x1, y1, z1, c, mat='obj'): aabb('abk', c, AX + x0, AY + y0, z0, AX + x1, AY + y1, z1, mat=mat)
def module(x, y, z, L, D, H, wall=WHITE, wins=3):
    """One container block, long side facing the camera (-y)."""
    abk(x - L / 2, y - D / 2, z, x + L / 2, y + D / 2, z + H, wall)
    abk(x - L / 2 - .08, y - D / 2 - .08, z + H - .35, x + L / 2 + .08, y + D / 2 + .08, z + H + .05, NAVY if wall == WHITE else '#D3D9E0')   # roof rim
    abk(x - L / 2 + .05, y - D / 2 - .06, z, x + L / 2 - .05, y - D / 2, z + .45, BLUE if wall == WHITE else NAVY)                         # base stripe
    for k in range(wins):
        wx = x - L / 2 + L * (k + .5) / wins
        box('abk', BLUE, (AX + wx, AY + y - D / 2 - .06, z + H * .55), (1.7, .12, 1.6))
        box('abk', GLASS, (AX + wx, AY + y - D / 2 - .1, z + H * .55), (1.3, .12, 1.25), mat='glass')
for i in range(4):                                                       # two-storey dorm: 4 x 2 x 2 modules
    for row in (-9.5, -4.7):
        for lvl in (0, 1):
            module(-22 + i * 14.2, row, .7 + lvl * 4.5, 13.8, 4.6, 4.3, wins=3 if row < -5 else 0)
abk(-29.3, -12, 0, 27.8, -2.4, .7, '#5B6467')                             # skid foundation
# R5-05e (Michael r10): unclear orange external stair removed; the porch is the only entrance
abk(-4.2, -15.5, .7, 4.2, -11.8, 4.2, WHITE)                              # entrance tambour
box('abk', BLUE, (AX, AY - 15.55, 2.2), (2.6, .15, 3))
abk(-5.5, -17.2, 4.2, 5.5, -11.8, 4.6, ORANGE)                            # canopy
for i in range(3): abk(-2.4, -15.5 - (i + 1) * 1.0, 0, 2.4, -15.5 - i * 1.0, .7 - i * .22, '#A9AFB5')
for i in range(5):                                                       # second row: single-storey containers
    module(-25 + i * 10.4, 5, .5, 9.8, 4.2, 3.6, wall=(WHITE, WHITE, BLUE, WHITE, WHITE)[i], wins=2)
for x, y, L, D, H in ((33, -7.1, 9, 9.4, 5.2), (33, 5, 9, 4.2, 3.6)):     # blue utility blocks (canteen, generator); R5-05e: clear 0.6 m gap, no window clash (Michael r10)
    module(x, y, .4, L, D, H, wall=BLUE, wins=2)
for y in (13, 16.4): cyl('abk', '#F0F0EC', (AX + 26, AY + y, 1.9), 1.5, 9, axis='X', seg=20)   # fuel tanks
box('abk', BLUE, (AX, AY - 11.97, 8.0), (11, .2, 2.4))                    # sign panel on the upper storey
cu = bpy.data.curves.new('ABK_sign', 'FONT'); cu.body = 'АБК'; cu.size = 2.0; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
cu.font = bpy.data.fonts.load('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf')
o = bpy.data.objects.new('ABK_sign', cu); scene.collection.objects.link(o)
o.location = (AX, AY - 12.1, 8.0); o.rotation_euler = (math.pi / 2, 0, 0); o.color = srgb(WHITE); cu.materials.append(MAT['flat'])
o['group'] = 'abk'; GROUPS.setdefault('abk', []).append(o)


IX, IY = 69, 175
for x, y, sx, sy in ((-14, -8, 13, 8), (7, -9, 15, 9), (12, 8, 19, 7), (-13, 9, 13, 7)):
    box('industry', '#D5DBD1', (IX + x, IY + y, 2.4), (sx, sy, 4.5))
    box('industry', '#387695', (IX + x, IY + y, 4.8), (sx + .5, sy + .5, .3))
    for k2 in range(int(sx / 3)): box('industry', '#54869B', (IX + x - sx / 2 + 2 + k2 * 3, IY + y - sy / 2 - .03, 2.8), (1.6, .08, 1.4))
for level in range(7):
    z0 = 1 + level * 4.5; z1 = z0 + 4.5; r0 = 3.4 - level * .32; r1 = r0 - .32
    col = '#E9E6DC' if level % 2 else '#C8382F'
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        beam('industry', col, (IX + sx * r0, IY + sy * r0, z0), (IX + sx * r1, IY + sy * r1, z1), .28)
        beam('industry', col, (IX + sx * r0, IY + sy * r0, z0), (IX - sx * r1, IY + sy * r1, z1), .16)
        beam('industry', col, (IX + sx * r1, IY + sy * r1, z1), (IX - sx * r1, IY + sy * r1, z1), .18)
box('industry', '#BAA05F', (IX, IY, 33), (3, 3, .6))
for x in (-6, -3, 0): cyl('industry', '#CFD5CD', (IX + x, IY + 15, 1.6), 1.5, 9, axis='X', seg=16)

PX, PY = 35, 222
cyl('helipad', '#BDB7A8', (PX, PY, .18), 16, .4, seg=64, mat='paving')
for k2 in range(80):
    a = k2 * math.tau / 80
    box('helipad', '#F4F1E6', (PX + 11.6 * math.cos(a), PY + 11.6 * math.sin(a), .42), (.98, .45, .035), rot=a + math.pi / 2, mat='flat')
for x in (-3, 3): box('helipad', '#F4F1E6', (PX + x, PY, .43), (1.3, 9, .03), mat='flat')
box('helipad', '#F4F1E6', (PX, PY, .43), (6, 1.3, .03), mat='flat')
beam('helipad', '#747E77', (PX + 19, PY - 13, 0), (PX + 19, PY - 13, 6), .12)
for k2 in range(5): cyl('helipad', ('#E8884B', '#E4E9DE')[k2 % 2], (PX + 19.3 + k2 * .45, PY - 13, 5.7), .45 - k2 * .055, .45, axis='X', r2=.4 - k2 * .055, seg=12)

for x, y, r, z in ((-68, 178, 3.6, 7.2), (-58, 182, 3.1, 6.4)):          # R5-05: real chum size (was 14 m tall)
    cyl('chums', '#C9B796', (x, y, z / 2), r, z, r2=.15, seg=32)
    mesh('chums', '#6C6453', [(x - .9, y - r - .02, 0), (x + .9, y - r - .02, 0), (x, y - r * .42, z * .45)], [(0, 1, 2)])
    for a in (.4, 2.4, 4.0, 5.1):
        beam('chums', '#8D7856', (x + math.cos(a) * r, y + math.sin(a) * r, 0), (x - math.cos(a) * .45, y - math.sin(a) * .45, z + 1), .1)
for y in (172, 173.6): beam('chums', '#8D7958', (-66, y, .25), (-61, y, .25), .12)
def deer(x, y, scale=1):
    m = at(x, y, rad(25), scale)
    ball('reindeer', '#6E5F4C', (0, 0, 2.4), 1, sx=2, sy=.7, sz=1, M=m)
    for xx in (-1.2, 1.1):
        for yy in (-.42, .42): beam('reindeer', '#766D5C', (xx, yy, 2.2), (xx + .12, yy, .1), .17, M=m)
    beam('reindeer', '#E6DFCF', (1.1, 0, 2.4), (1.7, 0, 3.9), .8, M=m)
    ball('reindeer', '#6E5F4C', (2.1, 0, 4), 1, sx=.9, sy=.4, sz=.45, M=m)
    for yy in (-.3, .3):
        beam('reindeer', '#766954', (1.55, yy, 4.2), (1.25, yy * 2, 5.4), .12, M=m)
        beam('reindeer', '#766954', (1.35, yy * 1.6, 4.9), (.8, yy * 2, 5.35), .09, M=m)
        beam('reindeer', '#766954', (1.27, yy * 1.9, 5.15), (1.8, yy * 2.2, 5.6), .08, M=m)
for dx, dy, ds in ((-25, -5, .55), (-21, -2, .5), (-23, 3, .5), (-17, -4, .55), (-19, 2, .45)): deer(HERD[0] + dx + 6, HERD[1] + dy, ds)   # herd of 5, ~2 m reindeer

# ---- flora: ochre sedge tussocks, autumn dwarf shrubs, lichen, boulders; no trees ---
KEEP_OUT = [(cx - rx, cx + rx, cy - ry, cy + ry) for cx, cy, rx, ry in CAMP] + [(HERD[0] - 22, HERD[0] + 8, HERD[1] - 10, HERD[1] + 10)]   # R5-05e   # ABK, rig yard, helipad, chums + herd
def free(x, y, margin=0.):
    if min(river_dist(x, y) - 10.5, creek_dist(x, y) - 4, y - shore(x) - 2) < margin: return False
    if clearing(x, y) > .4: return False
    if -82 < x < 70 and y < QY + 4: return False
    if any(a - margin < x < b + margin and c - margin < y < d + margin for a, b, c, d in KEEP_OUT): return False
    if min_pool_r(x, y) < 1.2: return False
    return trail_dist(x, y) > 8 or y < PAD[3] - 5
counts = dict(tussocks=0, shrubs=0, willows=0, lichen=0, boulders=0)
X0, X1, Y0, Y1 = -260, 250, -75, 400
def tussock(x, y, s, color, dark):                          # volumetric sedge tussock: peat dome + splayed blades
    z = ground(x, y)[0]; counts['tussocks'] += 1
    ball('sedge', dark, (x, y, z + .2 * s), .7 * s, sz=.6, sub=1)
    for k2 in range(6):
        a = k2 * math.tau / 6 + random.random()
        beam('sedge', color, (x + math.cos(a) * .2 * s, y + math.sin(a) * .2 * s, z + .3 * s),
             (x + math.cos(a) * .95 * s, y + math.sin(a) * .95 * s, z + random.uniform(1.2, 2.0) * s), .17 * s)
for i in range(int(32000 * FL)):
    x = random.uniform(X0, X1); y = random.uniform(Y0, Y1)
    if not free(x, y): continue
    lo, hi = wet_limits(x); inbog = lo - 3 < y < hi + 3; rim = min_pool_r(x, y) < 2.6
    if not (inbog or rim) and random.random() < .35: continue
    # R5-05: tussocks 0.4-0.8 m (were 2-3.4 m, taller than the RUSAK)
    if inbog: tussock(x, y, random.uniform(.32, .45), random.choice(('#B39A3E', '#C7A84C', '#9E8C3C', '#B97A3A', '#A9963F')), random.choice(('#6F5E32', '#7A6838')))
    else: tussock(x, y, random.uniform(.25, .38), random.choice(('#D3AE52', '#C49A3E', '#E1C26A', '#B58C3B')), '#8E7438')
for i in range(int(380 * FL)):                              # golden / rust dwarf-shrub clumps
    cx = random.uniform(X0, X1); cy = random.uniform(Y0, Y1)
    color = random.choice(('#D9A93A', '#E6B84A', '#C8902E', '#D9A93A', '#C2783A', '#B0603A', '#A9A04E'))
    for j in range(random.randint(5, 12)):
        x = cx + random.gauss(0, 2.5); y = cy + random.gauss(0, 1.8)
        lo, hi = wet_limits(x)
        if not free(x, y, 1) or lo - 2 < y < hi + 2: continue
        z = ground(x, y)[0]; r = random.uniform(.45, .9); counts['shrubs'] += 1
        for k2 in range(3):
            a = k2 * math.tau / 3 + random.random()
            ball('shrubs', color, (x + math.cos(a) * r * .7, y + math.sin(a) * r * .7, z + .55 * r), r * random.uniform(.75, 1.05), sz=.8, sub=2)
def willow(x, y):                                           # grey willow bush, 2-3 m, never a tree
    if not free(x, y, 1): return
    z = ground(x, y)[0]; r = random.uniform(.7, 1.0); color = random.choice(('#9EA79A', '#B3B8AA', '#8C978C', '#A7AD9C')); counts['willows'] += 1
    for k2 in range(4):
        ball('willows', color, (x + random.gauss(0, .8 * r), y + random.gauss(0, .6 * r), z + r * (.7 + .4 * k2)), r * random.uniform(.75, 1.0), sz=1.0, sub=2)
if FL:
    rw = dense(river, 6)
    for i in range(1, len(rw) - 1):
        d = (rw[i + 1] - rw[i - 1]).normalized(); n = Vector((-d.y, d.x))
        for side in (-1, 1):
            if random.random() < .3:
                q = rw[i] + n * side * random.uniform(12, 17)
                for j in range(random.randint(1, 3)): willow(q.x + random.gauss(0, 2.5), q.y + random.gauss(0, 2.5))
    for x in frange(X0, X1, 5):
        lo, hi = wet_limits(x)
        for yy in (lo - 3, hi + 3):
            if random.random() < .22: willow(x + random.uniform(-2, 2), yy + random.gauss(0, 2))
for i in range(int(700 * FL)):
    x = random.uniform(X0, X1); y = random.uniform(Y0, Y1)
    lo, hi = wet_limits(x)
    if not free(x, y) or lo - 3 < y < hi + 3: continue
    counts['lichen'] += 1
    ball('lichen', random.choice(('#DAD5B6', '#C9CBB8')), (x, y, ground(x, y)[0] + .05), random.uniform(.5, 1.1), sz=.18, sub=1)
def boulder(x, y, r):
    counts['boulders'] += 1
    ball('boulders', random.choice(('#8F918A', '#A6A79E', '#7C7F7A', '#B3B0A4')), (x, y, ground(x, y)[0] + r * .2), r,
         sx=random.uniform(1, 1.4), sy=random.uniform(.8, 1.2), sz=.6, sub=2)
if FL:
    for x in frange(X0 - 40, X1 + 40, 3.0):
        if not -82 < x < 70 and random.random() < .6: boulder(x + random.uniform(-1, 1), shore(x) + random.uniform(.5, 3.5), random.uniform(.6, 1.3))
    for x in list(frange(-98, -79, 1.2)) + list(frange(67, 86, 1.2)):   # riprap at both quay ends
        for j in range(2): boulder(x + random.uniform(-.6, .6), shore(x) + random.uniform(-.5, 5), random.uniform(.7, 1.3))
    for p in river[::2]:
        if random.random() < .35:
            a = random.uniform(0, math.tau); boulder(p.x + math.cos(a) * 11.5, p.y + math.sin(a) * 11.5, random.uniform(.5, 1.1))
    for i in range(180):
        x = random.uniform(X0, X1); y = random.uniform(Y0, Y1)
        lo, hi = wet_limits(x)
        if free(x, y, 2) and not lo - 4 < y < hi + 4:
            for j in range(random.randint(1, 4)): boulder(x + random.gauss(0, 2), y + random.gauss(0, 2), random.uniform(.5, 1.2))

flush()
bpy.context.view_layer.update()
FAR = {'industry': ((IX, IY), 1, (105, 180 + DY)), 'helipad': ((PX, PY), 1, (10, 205 + DY)), 'chums': ((-60, 180), 1, (-22, 167 + DY))}   # R5-05e   # R5-05d r3 (Michael: a chum stood in the river): both chums >= 30 m from the water   # R5-05: moved only, no far enlargement
for g, ((ox, oy), k3, (nx_, ny_)) in FAR.items():
    T = Matrix.Translation((nx_, ny_, 0)) @ Matrix.Scale(k3, 4) @ Matrix.Translation((-ox, -oy, 0))
    for ob in GROUPS[g]: ob.matrix_world = T @ ob.matrix_world
CHOICES = ['helicopter', 'pipe_carrier', 'rover', 'robot']
for group in CHOICES:
    pts = [ob.matrix_world @ v.co for ob in GROUPS[group] if ob.type == 'MESH' for v in ob.data.vertices]
    low = min(p.z for p in pts)
    wet = [tuple(p) for p in pts if p.z < low + .25 and ground(p.x, p.y)[0] < -.2]
    assert not wet, f'{group}: wheels in water {wet[:3]}'
for group in ('rover', 'robot', 'pipe_carrier', 'abk', 'industry'):
    for ob in GROUPS[group]:
        if ob.type == 'MESH':
            mod = ob.modifiers.new('soft edges', 'BEVEL'); mod.width = .03 if group != 'abk' else .09; mod.segments = 2

# ---- clear daylight, soft shadows, no ink (the painted map has no outlines) -------
scene.render.engine = 'BLENDER_EEVEE'
scene.world = bpy.data.worlds.new('daylight'); scene.world.use_nodes = True
bg = scene.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.80, .86, .93, 1); bg.inputs[1].default_value = .3
ld = bpy.data.lights.new('sun', 'SUN'); lo_ = bpy.data.objects.new('sun', ld); scene.collection.objects.link(lo_)
ld.energy = 4.2; ld.angle = rad(6); ld.color = (1, .985, .96)   # shared style block: clear daylight, sun upper-left ~45 deg
lo_.rotation_euler = Vector((.5, -.5, -.71)).normalized().to_track_quat('-Z', 'Y').to_euler()
scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'
scene.render.use_freestyle = False
if hasattr(scene.eevee, 'taa_render_samples'): scene.eevee.taa_render_samples = {'final': 64, 'preview': 16, 'gate': 4}[MODE]
for m in bpy.data.materials:                                # deeper contact shadow / AO in every toon material
    for n in (m.node_tree.nodes if m.node_tree else ()):
        if n.type == 'AMBIENT_OCCLUSION': n.inputs['Distance'].default_value = 6
        elif n.type == 'MIX' and n.blend_type == 'MULTIPLY' and abs(n.inputs[0].default_value - .35) < 1e-4: n.inputs[0].default_value = .5
scene.render.threads_mode = 'FIXED'; scene.render.threads = 12
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGB'

# ---- perspective cameras fitted to the R4 story points -----------------------------
import os
def group_pts(g): return [ob.matrix_world @ Vector(c) for ob in GROUPS[g] for c in ob.bound_box]
# R5-05 (Michael: "мелковато"): fit on the slab pad + choices + far camp only; the barge/quay ends may crop,
# so the true-scale vehicles stay big in the foreground and the far bank shrinks with perspective.
FIT = group_pts('barge')                                                         # R5-05b: barge must be in frame (coordinator r7)
for g in ('chums', 'helipad', 'abk', 'reindeer', 'gift', 'industry') + tuple(CHOICES): FIT += group_pts(g)   # R5-05e (Michael r10): rig, camp, ABK whole in the desktop frame
# tall: width-bound portrait; fit on the row, barge, ABK, helipad, chums and the rig tower only (rig yard sheds may crop at the edge)
TALL_FIT = [p for g in tuple(CHOICES) + ('abk', 'helipad', 'chums') for p in group_pts(g)]   # R5-05e (coordinator r10): camp in the top quarter   # R5-05d r2 (coordinator: phone vehicles bigger, little water): fit the row only; barge (BX -29) and camp land in the frame   # R5-05b: barge in frame
CAMS = {'wide': dict(res=(1600, 1000), tilt=40, yaw=-2.5, lens=24, pad=.05, fit=FIT, shift=0),   # R5-05d r2 (coordinator: whole barge + ABK in the desktop frame): plain fit, QY/DY pulled 5 m in   # R5-05d: high angle like scenes 1/2/4, no sky; cropped in so vehicles keep the R5-05c size (camp/barge touch the edges)   # R5-05c: lower tilt -> horizon + far ridges in frame          # R5-05b: whole real-scale barge at the quay          # R5-05: wider lens, close camera = clear near->far perspective
        'tall': dict(res=(900, 1500), tilt=57, yaw=-38, lens=28, pad=.03, fit=TALL_FIT, shift=-.01)}   # R5-05d r2 (coordinator: phone = less water, bigger row): width fit on row+barge, frame shifted up to the barge   # R5-05d   # R5-05c (Michael: phone too far, empty distance): close wide lens + yaw -6 -> row ~1.4x bigger, no horizon
for _n, _c in CAMS.items():                                 # R5-05 tuning: CAM_WIDE="lens,tilt,yaw,pad,shift"
    if os.environ.get('CAM_' + _n.upper()):
        _c.update(zip(('lens', 'tilt', 'yaw', 'pad', 'shift', 'zoom'), map(float, os.environ['CAM_' + _n.upper()].split(','))))
cams = []
for name, c in CAMS.items():
    cd = bpy.data.cameras.new(name); cd.lens = c['lens']; cd.clip_end = 4000
    cam = bpy.data.objects.new(name, cd); scene.collection.objects.link(cam)
    cam.rotation_euler = (rad(90 - c['tilt']), 0, rad(c['yaw']))
    scene.render.resolution_x, scene.render.resolution_y = c['res']; bpy.context.view_layer.update()
    co, _ = cam.camera_fit_coords(bpy.context.evaluated_depsgraph_get(), [v for p in c['fit'] for v in p])
    fwd = cam.rotation_euler.to_matrix() @ Vector((0, 0, -1))
    cam.location = co - fwd * (sum(c['fit'], Vector()) / len(c['fit']) - co).length * c['pad']
    cd.lens *= c.get('zoom', 1)                              # R5-05d: crop in after the fit (camp/barge may touch or leave the frame edge)
    cd.shift_y = c.get('shift', 0)  # width-bound tall frame: spend vertical slack on land, not water
    cams.append((cam, *c['res']))

# ---- overlap gate: projected choice box + ring halo + label slot below -------------
def rect(cam, g, W, H):
    p = [world_to_camera_view(scene, cam, v) for v in group_pts(g)]
    return [min(v.x for v in p) * W, (1 - max(v.y for v in p)) * H, max(v.x for v in p) * W, (1 - min(v.y for v in p)) * H]
def hit(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
manifest = dict(revision='R5-draft-05', base='R4 composition (scripts/lastmile-r4/build.py)', mode=MODE, seed=11011, people=0, trees=0,
                choices=CHOICES, barge_source='design/scene-04/blender-v4/quay.blend collection "Barge - approved geometry" (appended read-only)', flora=counts,
                peat_pools=len(pools), cameras={}, overlap={})
fails = []
LABEL = {'helicopter': 'Вертолёт', 'pipe_carrier': 'Трубовоз', 'rover': 'Вездеход', 'robot': 'Тележка'}   # R5-05e (coordinator r10): text-sized label, above or below
import itertools
for cam, W, H in cams:
    scene.render.resolution_x, scene.render.resolution_y = W, H; bpy.context.view_layer.update()
    rows = {}
    for g in CHOICES:
        r = rect(cam, g, W, H); gap = .012 * W; lh = .026 * H
        ring = [r[0] - gap, r[1] - gap, r[2] + gap, r[3] + gap]
        lw = len(LABEL[g]) * .3 * lh + .5 * lh; cx = (r[0] + r[2]) / 2
        rows[g] = dict(box=[round(v, 1) for v in r], ring=[round(v, 1) for v in ring],
                       below=[cx - lw / 2, ring[3] + 2, cx + lw / 2, ring[3] + 2 + lh], above=[cx - lw / 2, ring[1] - 2 - lh, cx + lw / 2, ring[1] - 2])
    def clash(sides):
        out = []
        for g, sd in zip(CHOICES, sides):
            l = rows[g][sd]
            if min(rows[g]['ring'][:2]) < 0 or rows[g]['ring'][2] > W or rows[g]['ring'][3] > H or l[0] < 0 or l[1] < 0 or l[2] > W or l[3] > H: out.append(f'{cam.name}/{g} outside frame')
        for i, a in enumerate(CHOICES):
            for j in range(i + 1, len(CHOICES)):
                b = CHOICES[j]
                for ka, kb in (('ring', 'ring'), ('ring', sides[j]), (sides[i], 'ring'), (sides[i], sides[j])):
                    if hit(rows[a][ka], rows[b][kb]): out.append(f'{cam.name}: {a}.{ka} x {b}.{kb}')
        return out
    best = min(itertools.product(('below', 'above'), repeat=len(CHOICES)), key=lambda sd: (len(clash(sd)), sd.count('above')))
    fails += clash(best)
    for g, sd in zip(CHOICES, best):
        rows[g]['label'] = [round(v, 1) for v in rows[g][sd]]; rows[g]['label_side'] = sd; rows[g]['label_text'] = LABEL[g]
        del rows[g]['below'], rows[g]['above']
    manifest['overlap'][cam.name] = rows
    pp = [world_to_camera_view(scene, cam, v) for v in CAMS[cam.name]['fit']]
    if os.environ.get('PROBE'):                               # tuning aid: which group bounds the frame
        for g in ('barge', 'abk', 'helipad', 'chums', 'reindeer', 'industry', 'gift', 'helideck') + tuple(CHOICES):
            q = [world_to_camera_view(scene, cam, v) for v in group_pts(g)]
            print('PROBE', cam.name, g, 'x %.2f..%.2f y %.2f..%.2f' % (min(v.x for v in q), max(v.x for v in q), min(v.y for v in q), max(v.y for v in q)))
    print('FRAME', cam.name, 'content x %.2f..%.2f y %.2f..%.2f' % (min(v.x for v in pp), max(v.x for v in pp), min(v.y for v in pp), max(v.y for v in pp)),
          {g: round(rows[g]['box'][2] - rows[g]['box'][0]) for g in CHOICES}, flush=True)
    manifest['cameras'][cam.name] = dict(resolution=[W, H], type='PERSP', lens=cam.data.lens, location=list(cam.location), rotation=list(cam.rotation_euler))
manifest['overlap_failures'] = fails
print('OVERLAP', json.dumps(fails), flush=True)
OUT.mkdir(parents=True, exist_ok=True)   # clean:stale prunes empty dirs during a long build
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
bpy.context.preferences.filepaths.save_version = 0
if MODE != 'gate' or os.environ.get('SAVE'): bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'scene.blend'))
for cam, W, H in cams:
    scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.resolution_percentage = {'final': 100, 'preview': 50, 'gate': 25}[MODE]
    scene.render.filepath = str(OUT / f'{cam.name}.png'); bpy.ops.render.render(write_still=True)
print('R5_RENDER_COMPLETE', MODE, flush=True)
