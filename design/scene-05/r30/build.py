"""R30: rebuild the shared 3D world. Port, branded vehicles and hut geometry descend from
scripts/lastmile-r5/build.py and its blender-v2-derived helpers. No raster plate is loaded.
Preview and final differ in terrain mesh/foliage density only; cameras are fixed.
"""
import bpy, math, random, sys, json
from pathlib import Path
from mathutils import Vector, Matrix, noise
from mathutils.kdtree import KDTree
from bpy_extras.object_utils import world_to_camera_view
OUT = Path(sys.argv[sys.argv.index('--') + 1]).resolve(); OUT.mkdir(parents=True, exist_ok=True)
MODE = sys.argv[-1] if sys.argv[-1] in ('preview', 'final', 'gate') else 'preview'
ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts/lastmile-r4'))
DY = -98
FL = .45 if MODE == 'preview' else 1.0
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
water_mat('cobalt', '#3F7FB8', '#5C9AC9', '#B9D6EE', (.035, .12))
water_mat('peat', '#2A2116', '#463626', '#8C7B5C', (.06, .2))
MAT['canvas'] = MAT['paving']


# docs/teo-feedback-assets/image-01.png (drawing px, nose left); first cabin windows 210/241 px = model x 0/-1.3 m.
GLYPH = [(168, 179), (169, 182), (187, 183), (206, 188), (208, 190), (212, 190), (214, 193), (220, 196), (221, 201), (220, 214), (216, 219), (213, 221), (209, 221), (202, 216), (192, 218), (192, 221), (203, 224), (212, 228), (217, 228), (218, 232), (221, 237), (221, 241), (216, 248), (206, 252), (198, 253), (195, 255), (196, 257), (223, 257), (227, 255), (227, 248), (232, 247), (237, 247), (239, 254), (255, 248), (259, 244), (260, 237), (253, 230), (245, 226), (227, 221), (228, 217), (233, 216), (233, 209), (237, 203), (245, 203), (249, 205), (252, 210), (259, 204), (261, 198), (259, 193), (256, 192), (254, 189), (250, 189), (249, 186), (237, 182), (216, 178), (179, 177), (170, 178)]
def heli_swoosh(group, side, transform):
    def inside(px, py):                                     # even-odd point in polygon
        c = False
        for (ax, ay), (bx, by) in zip(GLYPH, GLYPH[1:] + GLYPH[:1]):
            if (ay > py) != (by > py) and px < ax + (py - ay) * (bx - ax) / (by - ay): c = not c
        return c
    k, st = 1.3 / 31, 1.5                                   # m per drawing px, cell size in px (~6 cm)
    idx, vs, faces = {}, [], []
    def v(px, py):
        if (px, py) not in idx:
            x, z = -(px - 210) * k if side > 0 else (px - 241) * k, 2.65 - (py - 211) * k   # brand mark reads '3' on both sides (not mirrored)
            idx[px, py] = len(vs); vs.append((x, side * (1.95 * math.sqrt(max(.0025, 1 - ((x - 1.2) / 6.2) ** 2 - ((z - 2.4) / 1.95) ** 2)) + .07), z))
        return idx[px, py]
    for i in range(int(166 / st), int(263 / st)):
        for j in range(int(175 / st), int(259 / st)):
            cx, cy = (i + .5) * st, (j + .5) * st
            wx_ = -(cx - 210) * k if side > 0 else (cx - 241) * k
            if not inside(cx, cy) or min(math.hypot(wx_ - wx, (cy - 211) * k) for wx in (0, -1.3, -2.6)) < .52: continue   # cabin windows stay clear
            q = [v(i * st, j * st), v((i + 1) * st, j * st), v((i + 1) * st, (j + 1) * st), v(i * st, (j + 1) * st)]
            faces.append(tuple(reversed(q)) if side > 0 else tuple(q))
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

# ---- Compact river braid, bog band, harbour shore -----
knots = [(2700,-21),(1600,-35),(1000,-17),(600,-37),(360,-29),(112,-20),(60,-29),(27,-30),(2,-35),(-31,-23),(-30,-12),(-8,-4),(16,15),(20,39),(26,65),(41,93),(64,151),(58,240),(94,391),(100,621),(190,1002),(260,1302),(330,1702),(420,2302),(500,3002)]
river = catmull(knots)
# Smooth tangents at both ends: two open channels divide around the camp island.
fork = catmull([knots[9],(-46,-8),(-44,8),(-36,24),(-33,40),(-20,51),(-4,54),(13,65),knots[14]])
RIVER = kd(dense(river)); FORK = kd(dense(fork))
def river_dist(x, y): return min(RIVER.find((x, y, 0))[2], FORK.find((x,y,0))[2] + 2.2)
def wet_limits(x): return (PAD[3] + 3 + 1.5 * math.sin(x * .037) + .8 * math.sin(x * .19) + .5 * math.sin(x * .43), -30 + 3 * math.sin(x * .045 + 1) + 2 * math.sin(x * .22))
def shore(x):
    # Tundra headlands flank the berth; the unglaciated centre stays open to sea.
    q=max(-78-x, x-66, 0)
    return -77 - 30*smooth01(0,78,q) - 17*smooth01(70,185,q) + (3*math.sin(x*.047) if q else 0)

# ---- R5 additions: row clearing, heli pad, rut trail, side creek, peat pools ----
import os
QY = -69
ROW_Y = QY + 9
PAD = (-48, QY, 38, QY + 20)
HP = (-32, ROW_Y)
PITCH = 16.7
ROW = {k: (HP[0] + i * PITCH, ROW_Y) for i, k in enumerate(('rover','pipe_carrier','robot'), 1)}
ROT = dict.fromkeys(ROW, math.radians(-16))
AX, AY = 44, -3
RX0, RY0 = 100, 64
CHUM = (-3, 35)
HERD = (CHUM[0] + 17, CHUM[1] - 5)
CAMP = [(AX, AY, 28, 12), (RX0, RY0, 22, 16), (57, 20, 13, 14), (*CHUM, 12, 10)]
ROAD = kd(dense(catmull([(AX, AY - 12), (AX + 29, AY - 11), (AX + 32, AY + 11), (66, 31), (75, 43), (94, 56)], 20)))
def clearing(x, y):                                         # 1 on the slab pad, the camp and the herd patch
    pad = smooth01(3.2 + .6 * N(x, y, .12, 12), 2.2, max(PAD[0] - x, x - PAD[2], PAD[1] - y, y - PAD[3]))
    r = min(math.hypot((x - cx) / rx, (y - cy) / ry) for cx, cy, rx, ry in CAMP)
    r = min(r, math.hypot((x - HERD[0]) / 16, (y - HERD[1]) / 11))
    road = smooth01(3.4, 2.2, ROAD.find((x, y, 0))[2] + .4 * N(x, y, .2, 19))
    return max(pad, road, smooth01(1.05, .8, r + .16 * N(x, y, .045, 7) + .06 * N(x, y, .2, 13)))
TX = ROW['rover'][0]
TY1 = next(y for y in frange(PAD[3], PAD[3] + 80, .5) if river_dist(TX + 2.5, y) < 11.5)
trail = dense(catmull([(TX + .3 * math.sin(k * 1.7) + 2.2 * (k % 2), PAD[3] - 1 + (TY1 - PAD[3] + 1) * k / 5) for k in range(6)], 30))
_tn = [(trail[min(i + 1, len(trail) - 1)] - trail[max(i - 1, 0)]).normalized() for i in range(len(trail))]
trail2 = [p + Vector((-d.y, d.x)) * (3.0 + 1.3 * math.sin(i * .045)) for i, (p, d) in enumerate(zip(trail, _tn))][40:]   # second braided track (vehicles swerving round the worst holes)
TRAIL, TRAIL2 = kd(trail), kd(trail2)
def trail_dist(x, y): return min(TRAIL.find((x, y, 0))[2], TRAIL2.find((x, y, 0))[2])
def creek_dist(x, y): return 99
pools = [(q.x + 1.5, q.y, 2.8, 1.8, .3, 1.1) for q in (trail[int(len(trail) * f_)] for f_ in (.3, .55, .8))]
for i in range(3000):
    if len(pools) >= 85: break
    x = random.uniform(-150, 210); lo, hi = wet_limits(x); y = random.uniform(lo + 3, hi - 3)
    rx = random.uniform(2, 7.8); ry = rx * random.uniform(.38, .68)
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
        bogc = lerpc(bogc, C['peat'], .55 * smooth01(-.1, .35, N(x, y, .07, 16)))
        col = lerpc(col, bogc, m * .95)
        r = min_pool_r(x, y)
        if r < 1.7:                                             # pool: dark water with a raised peat lip
            lip = smooth01(1.7, 1.25, r) * smooth01(.92, 1.1, r)
            z = lerp(-.6, z + .32 * lip, smooth01(.88, 1.0, r))
            col = lerpc(C['peat'], col, smooth01(1.0, 1.65, r))
    t1, t2 = TRAIL.find((x, y, 0))[2], TRAIL2.find((x, y, 0))[2]; td = min(t1, t2)
    if td < 13 and y > PAD[3] - 1:
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
f = 1.45 if MODE == 'final' else 2.25
# from the cameras, so even the wide overscan's top row (+0.2 deg at tilt 40) meets ground; the original frames are unchanged
HAZE = srgb('#A3B4C3')[:3]
def rise(x,y):
    return smooth01(190,470,y)*smooth01(15,65,river_dist(x,y)) * (4+5*N(x,y,.012,54)+4*N(x,y,.003,52))

xs = frange(-2600,-250,32) + frange(-250,-115,2*f) + frange(-115,140,.75*f) + frange(140,250,2*f) + frange(250,2601,32)
ys = frange(-450,-90,10) + frange(-90,PAD[3]-2,f) + frange(PAD[3]-2,TY1+3,.43*f) + frange(TY1+3,301,f) + frange(301,3101,20)
vs = []; cols = []
for y in ys:
    for x in xs:
        z, c = ground(x, y); vs.append((x, y, z + rise(x, y))); c = lerpc(c, HAZE, smooth01(690, 2400, y) ** .7); cols.extend((*c, 1))
nx = len(xs)
terrain = mesh('tundra', '#FFFFFF', vs, [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(len(ys) - 1) for i in range(nx - 1)], 'ground', smooth=True)
terrain.data.color_attributes.new('col', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', cols)
aabb('harbor_water', '#2F6BC0', -2600, -2700, -1.3, 2600, -69, -1.22, mat='cobalt')
for course, width in ((river,10.1), (fork,7.9)):
    rv = []
    for i,p in enumerate(course):
        d=(course[min(i+1,len(course)-1)]-course[max(0,i-1)]).normalized(); n=Vector((-d.y,d.x))*width
        rv.extend([(p.x+n.x,p.y+n.y,-.5),(p.x-n.x,p.y-n.y,-.5)])
    mesh('river','#2F6BC0',rv,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(course)-1)],'cobalt')
for p in pools:
    ring=[]
    for j in range(32):
        a=j*math.tau/32; ux,uy=math.cos(a),math.sin(a); rr=.99/pool_r(p,p[0]+ux,p[1]+uy)
        ring.append((p[0]+ux*rr,p[1]+uy*rr,-.19))
    mesh('peat_pools', '#FFFFFF', ring + [(p[0], p[1], -.2)], [(j, (j + 1) % 32, 32) for j in range(32)], 'peat')
for tr, off in ((trail, 1.6), (trail2, 1.5)):
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
    n = 18; base = len(ice_v); ph = [random.random() * 6 for _ in range(4)]
    amp = [random.uniform(.1, .28), random.uniform(.05, .16), random.uniform(.03, .1), random.uniform(.02, .06)]
    jit = [random.uniform(-.09, .09) for _ in range(n)]
    for zz in (zbot, ztop):
        for j in range(n):
            a = j * math.tau / n; rr = r * (1 + sum(amp[k] * math.sin((k + 1) * a + ph[k]) for k in range(4)) + jit[j])
            dx, dy = math.cos(a) * rr * elong, math.sin(a) * rr
            ice_v.append((x + dx * math.cos(ang) - dy * math.sin(ang), y + dx * math.sin(ang) + dy * math.cos(ang), zz + (.08 * math.sin(a + ph[0]) if zz == ztop else 0)))
    ice_top.append(tuple(base + n + j for j in range(n)))
    ice_side.extend((base + j, base + (j + 1) % n, base + n + (j + 1) % n, base + n + j) for j in range(n))
BS, BX = .70, float(os.environ.get('BX', -39))
BARGE_BOX = (BX - 18 * BS, -77.3 - 15 * BS, BX + 34 * BS, -76)
placed = []
for i in range(3500):
    x = random.uniform(-260, 300); y = random.uniform(-260, -80)
    if BARGE_BOX[0] < x < BARGE_BOX[2] and BARGE_BOX[1] < y < BARGE_BOX[3]: continue
    r = random.uniform(.3, 1.1) if random.random() < .8 else random.uniform(1.1, 2.6)
    if any((x - a) ** 2 + (y - b) ** 2 < (r + c + 1.2) ** 2 for a, b, c in placed): continue
    if random.random() > (.75 if y > shore(x) - 25 else .3): continue
    placed.append((x, y, r)); floe(x, y, r, random.uniform(1, 1.8), random.uniform(0, math.pi), -.85, -1.5)
for x in frange(-260, 300, 4.5):
    if -82 < x < 70: continue
    if random.random() < .75: floe(x, shore(x) - random.uniform(1, 2.5), random.uniform(1, 2), 1.7, random.uniform(-.2, .2), -.8, -1.5)
for i in range(4, len(river) - 4, 2):
    p = river[i]
    if min((p - fork[0]).length, (p - fork[-1]).length) < 24: continue
    if random.random() < .28:
        side = random.choice((-.75, -.3, 0, .3, .75)); d = (river[i + 1] - river[i - 1]).normalized(); n = Vector((-d.y, d.x))
        floe(p.x + n.x * 7 * side, p.y + n.y * 7 * side, random.uniform(1, 2.4), 1.4, math.atan2(d.y, d.x), -.2, -.62)
rd_ = dense(river, 3.2)
for i in range(1, len(rd_) - 1):                            # shelf ice edging both river banks
    if min((rd_[i] - fork[0]).length, (rd_[i] - fork[-1]).length) < 27: continue
    d = (rd_[i + 1] - rd_[i - 1]).normalized(); n = Vector((-d.y, d.x))
    for side in (-1, 1):
        if random.random() < .27:
            q = rd_[i] + n * side * random.uniform(8.2, 9.0)
            floe(q.x, q.y, random.uniform(1.2, 2.2), 2.0, math.atan2(d.y, d.x), -.3, -.7)
mesh('ice', '#EEF4F7', ice_v, ice_top, 'flat')
mesh('ice', '#C9DAE4', ice_v, ice_side, 'flat')

# ---- concrete precast-slab quay deck and scene-4 barge ---------------------------
# Large 8 x 3.4 m panels; narrow grey joints read as slab seams, never timber boards.
aabb('quay', '#AEB6B8', -78, -76, -1.2, 66, QY, .11)  # concrete subdeck beneath panels, original footprint
for x in frange(-78, 66, 8):
    aabb('quay', '#586166', x, -76, .14, x + .12, QY, .142)
aabb('quay', '#586166', -78, -72.55, .14, 66, -72.43, .142)  # transverse slab joints
for row, (y0, y1) in enumerate(((-75.94, -72.57), (-72.41, -69.06))):
    for col, x in enumerate(frange(-77.94, 65.94, 8)):
        x1 = min(x + 7.88, 65.94)
        aabb('quay', ('#B5BCBD', '#A9B1B3', '#B0B8BA')[(col + row) % 3], x, y0, .11, x1, y1, .14)
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
with bpy.data.libraries.load(str(ROOT / 'design/scene-04/blender-v4/quay.blend'), link=False) as (src, dst):
    dst.collections = ['Barge - approved geometry']
assert dst.collections[0], 'barge collection missing'
scene.collection.children.link(dst.collections[0])
for ob in dst.collections[0].all_objects:
    ob.matrix_world = BM @ ob.matrix_world; ob['group'] = 'barge'; GROUPS.setdefault('barge', []).append(ob)
    for slot in ob.material_slots: slot.material = MAT['glass' if slot.material.name.startswith('glass') else 'obj']
assert len(GROUPS['barge']) == 12, len(GROUPS['barge'])
CX, CS = float(os.environ.get('CX', -51)), .64
with bpy.data.libraries.load(str(ROOT / 'design/scene-04/blender-v4/quay.blend'), link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n.split('|')[0] in ('near', 'near_top', 'ladder')]
CM = Matrix.Translation((CX, -77.3 + 7.25 * CS, .14)) @ Matrix.Rotation(rad(float(os.environ.get('CR', 0))), 4, 'Z') @ Matrix.Scale(CS, 4) @ Matrix.Translation((-14, -7.25, 0))   # slew about the portal centre   # scene-4 NEAR_X = 14, quay face y=0
_cc = Matrix.Translation((CX, -77.3 + 7.25 * CS, 0))
CTOP = _cc @ Matrix.Rotation(rad(float(os.environ.get('CTR', 300))), 4, 'Z') @ _cc.inverted() @ CM
for ob in dst.objects:
    scene.collection.objects.link(ob); g_ = 'crane_top' if ob.name.startswith('near_top') else 'crane'; ob.matrix_world = (CTOP if g_ == 'crane_top' else CM) @ ob.matrix_world; ob['group'] = g_; GROUPS.setdefault(g_, []).append(ob)
    for slot in ob.material_slots: slot.material = MAT['flat' if slot.material.name.startswith('flat') else 'obj']
assert len(GROUPS['crane']) + len(GROUPS['crane_top']) == 15
for lx in (-12, 28): beam('mooring', '#5D5A50', BM @ Vector((lx, -2.6, -.4)), (BX + lx * BS + 5, -74, 1.0), .16)
# The warehouse parcel has a separate lid, ivory cross-wrap and folded ribbon loops.
GX, GY, K = -12, -72.6, .21
M = at(GX, GY, rad(-10), K, .15)
box('gift', '#B62425', (0,0,1.05), (2.65,2.3,2.1), M=M)
box('gift', '#C6322F', (0,0,2.07), (2.7,2.35,.16), M=M)
for axis in (0,1):
    x,y = ((.36,2.37) if axis==0 else (2.72,.36))
    box('gift', '#FFF1D6', (0,0,1.11), (x,y,2.14), M=M)
for side in (-1,1):
    # A broad curled strip with an actual opening (rather than balls on the lid).
    pts=[(0,0,2.21),(.30,.02,2.52),(.69,.04,2.68),(.9,.04,2.59),(.85,.02,2.44),(.58,0,2.28),(0,0,2.21)]
    verts=[(side*x,y+j,z) for x,y,z in pts for j in (-.13,.13)]
    mesh('gift','#FFF0D8',verts,[(i,i+1,i+3,i+2) for i in range(0,len(verts)-2,2)],transform=M,smooth=True)
    mesh('gift','#F8E5C5',[(0,0,2.24),(side*.19,-.1,2.25),(side*.56,-.85,2.19),(side*.38,-.73,2.19),(side*.31,-.96,2.19)],[(0,1,2,3,4)],transform=M)
ball('gift','#F8E2C2',(0,0,2.34),.19,sy=.9,sz=.85,M=M)

PZ = .2                                                                  # slab top
# west end: white FATO edge, yellow TD/PM circle, white H, green perimeter lights, tie-downs, steps, windsock.
DZ = .9                                                                  # deck top
HD = (HP[0] - 13, QY + .5, HP[0] + 13, QY + 17.5)
_heli_r4 = h.heli
def heli_livery(group, M):
    _heli_r4(group, M)
    zc, n, rings = .9, 48, 8                                    # cut 0.9 m above the axis = just over the round cabin windows
    c0 = math.acos(zc / 1.98)
    vs = [(1.2, 0, 2.4 + 1.98)]
    for r in range(1, rings + 1):
        ph = c0 * r / rings
        vs += [(1.2 + 6.23 * math.sin(ph) * math.cos(t * math.tau / n), 1.98 * math.sin(ph) * math.sin(t * math.tau / n), 2.4 + 1.98 * math.cos(ph)) for t in range(n)]
    faces = [(0, 1 + (t + 1) % n, 1 + t) for t in range(n)]
    faces += [(1 + (r - 1) * n + t, 1 + (r - 1) * n + (t + 1) % n, 1 + r * n + (t + 1) % n, 1 + r * n + t) for r in range(1, rings) for t in range(n)]
    mesh(group, '#232629', vs, faces, transform=M, smooth=True)
h.heli = heli_livery
h.heli('helicopter', at(HP[0], HP[1], ROT['pipe_carrier'], 1.0, DZ))
h.pipe_carrier('pipe_carrier', at(*ROW['pipe_carrier'], ROT['pipe_carrier'], 1.38, PZ))
h.rusak('rover', at(*ROW['rover'], ROT['rover'], 1.52, PZ))
h.robot('robot', at(*ROW['robot'], ROT['robot'], 2.48, PZ))
# Curved, framed cockpit glass on the actual Mi-8 shell, plus cabin door and steps.
M=at(*HP,ROT['rover'],1,DZ)
def shell(longitude,latitude):
    a,b=rad(longitude),rad(latitude)
    return (1.2+6.23*math.cos(a)*math.cos(b),1.982*math.sin(a)*math.cos(b),2.4+1.98*math.sin(b))
for side in (-1,1):
    for lon0,lon1 in ((2,27),(30,53)):
        verts=[shell(side*(lon0+(lon1-lon0)*i/5),5+j*7.3) for j in range(6) for i in range(6)]
        mesh('helicopter','#355B74',verts,[(j*6+i,j*6+i+1,(j+1)*6+i+1,(j+1)*6+i) for j in range(5) for i in range(5)],transform=M,smooth=True)
        for j in (0,5):
            for i in range(5): beam('helicopter','#343F44',verts[j*6+i],verts[j*6+i+1],.052,M=M)
    for x in (1,2.32):
        beam('helicopter','#754C31',(x,side*1.9,1.72),(x,side*1.97,3.1),.045,M=M)
    beam('helicopter','#CCD4D6',(1.45,side*1.99,2.34),(1.83,side*1.99,2.34),.055,M=M)
    beam('helicopter','#606C6E',(1.0,side*1.72,1.12),(2.46,side*1.72,1.12),.095,M=M)
    for i in range(7): cyl('helicopter','#C9AA82',(-2.8+i*.65,side*1.85,2.14),.035,.07,axis='Y',M=M)
# Cabin glazing and rail uprights on the barge's previously bare camera-facing walls.
for x,z0,z1,by in [(x,4.7,5.55,-11.37) for x in (24.1,25.55,27,28.45)]+[(x,2.0,3.0,-12.34) for x in (22,24,26,28.6)]:
    box('barge','#2D455A',(x,by,z0+(z1-z0)/2),(1.05,.09,z1-z0),M=BM)
for x in (-11,-6,-1,4,9,14,19):
    beam('barge','#D2BCAF',(x,-13.08,.1),(x,-13.08,1.11),.095,M=BM)
beam('barge','#D2BCAF',(-11,-13.08,1.08),(19,-13.08,1.08),.095,M=BM)
for x in (-10,1,12,27): cyl('barge','#384147',(x,-13.48,-.79),.44,.29,axis='Y',seg=16,M=BM)
for j, y in enumerate(frange(PAD[1], PAD[3] - .1, 2.1)):               # road slabs 6 x 2 m, staggered rows
    for x in frange(PAD[0] + (3 if j % 2 else 0) - 3, PAD[2], 6.1):
        x0, x1 = max(x, PAD[0]), min(x + 6, PAD[2])
        if y < HD[3] + .5 and x1 > HD[0] - .6 and x0 < HD[2] + .6:
            if x0 < HD[0] - .6: x1 = HD[0] - .6
            else: x0 = max(x0, HD[2] + .6)
        edge = min(x0 - PAD[0], PAD[2] - x1, y - PAD[1], PAD[3] - y - 2) < 1
        if x1 - x0 > .5:
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
def windsock(group,x,y,height,length,radius):
    cyl(group,'#6C7575',(x,y,height/2),.11,height,seg=12)
    cyl(group,'#535D60',(x,y,.27),.34,.54,seg=12)
    for z in (-.72,.72): beam(group,'#797A70',(x,y,height-.3),(x+.7,y,height-.42+z*radius),.056)
    for j in range(5):
        rings=[]
        for k in (j,j+1):
            t=k/5; r=radius*(1-.59*t)
            rings.extend((x+.7+t*length,y+r*math.cos(i*math.tau/20),height-.42-.69*t*t+r*math.sin(i*math.tau/20)) for i in range(20))
        mesh(group,('#DC661F','#FFF5DB')[j%2],rings,[(i,(i+1)%20,(i+1)%20+20,i+20) for i in range(20)],smooth=True)
windsock('windsock',*WS,6.1,3.8,.60)

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
# Smooth civil concrete TLOF, restrained slab joints and perimeter lights.
aabb('helipad','#999891',PX-16.4,PY-16.4,-.3,PX+16.4,PY+16.4,.11)
for j in range(4):
    for i in range(4):
        aabb('helipad',('#C9C6B9','#C5C4B9','#D1CCBD')[(i+j*2)%3],PX-16+i*8+.05,PY-16+j*8+.05,.1,PX-8+i*8-.05,PY-8+j*8-.05,.4)
for s in (-1,1):
    box('helipad','#F6EEDB',(PX+s*15.35,PY,.42),(.32,30.8,.035),mat='flat')
    box('helipad','#F6EEDB',(PX,PY+s*15.35,.42),(30.8,.32,.035),mat='flat')
    for t in (-1,1): cyl('helipad','#629F78',(PX+s*15.25,PY+t*15.25,.59),.37,.30,seg=12)
for k2 in range(80):
    a = k2 * math.tau / 80
    box('helipad', '#F4F1E6', (PX + 11.6 * math.cos(a), PY + 11.6 * math.sin(a), .42), (.98, .45, .035), rot=a + math.pi / 2, mat='flat')
for x in (-3, 3): box('helipad', '#F4F1E6', (PX + x, PY, .43), (1.3, 9, .03), mat='flat')
box('helipad', '#F4F1E6', (PX, PY, .43), (6, 1.3, .03), mat='flat')
windsock('helipad',PX+18,PY-13,6,3.9,.6)


for x, y, r, z in ((-68, 178, 3.6, 7.2), (-58, 182, 3.1, 6.4)):
    cyl('chums', '#6E5644', (x, y, z / 2), r, z, r2=.15, seg=32)
    mesh('chums', '#6C6453', [(x - .9, y - r - .02, 0), (x + .9, y - r - .02, 0), (x, y - r * .42, z * .45)], [(0, 1, 2)])
    for a in (.4, 2.4, 4.0, 5.1):
        beam('chums', '#E2D3B0', (x + math.cos(a) * r, y + math.sin(a) * r, 0), (x - math.cos(a) * .45, y - math.sin(a) * .45, z + 1), .1)
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
KEEP_OUT = [(cx - rx, cx + rx, cy - ry, cy + ry) for cx, cy, rx, ry in CAMP] + [(HERD[0] - 22, HERD[0] + 8, HERD[1] - 10, HERD[1] + 10)]
def free(x, y, margin=0.):
    if min(river_dist(x, y) - 10.5, creek_dist(x, y) - 4, y - shore(x) - 2) < margin: return False
    if clearing(x, y) > .4: return False
    if -82 < x < 70 and y < QY + 4: return False
    if any(a - margin < x < b + margin and c - margin < y < d + margin for a, b, c, d in KEEP_OUT): return False
    if min_pool_r(x, y) < 1.2: return False
    return trail_dist(x, y) > 8 or y < PAD[3] - 5
counts = dict(tussocks=0, shrubs=0, willows=0, lichen=0, boulders=0)
X0, X1, Y0, Y1 = -260, 250, -75, 400
# Low bent sedge in irregular stands: tapered blades, not repeated spheres or sticks.
random.seed(3005)
blades = {}; colors = ['#AB863D','#A49254','#C8AA66','#CFB36B','#B0763F','#D9BD76','#858451']
for i in range(int(10500*FL)):
    cx,cy=random.uniform(-235,235),random.uniform(-75,390)
    if random.random() < .82*smooth01(75,390,cy): continue
    if not free(cx,cy): continue
    for j in range(random.randrange(4,15)):
        x,y=cx+random.gauss(0,1.6),cy+random.gauss(0,1.1)
        if not free(x,y): continue
        z=ground(x,y)[0]; s=random.uniform(.46,1.15); col=random.choice(colors); v,f_=blades.setdefault(col,([],[]))
        for b in range(5):
            a=random.random()*math.tau; dx,dy=math.cos(a),math.sin(a); l=random.uniform(.3,1.1)*s; w=.13*s; i0=len(v)
            v.extend([(x-dy*w,y+dx*w,z),(x+dy*w,y-dx*w,z),(x+.4*l*dx,y+.4*l*dy,z+l*.72),(x+l*dx+.12,y+l*dy,z+l*1.12)])
            f_.extend([(i0,i0+1,i0+2),(i0+1,i0+3,i0+2)])
        counts['tussocks']+=1
for col,(v,fs_) in blades.items(): mesh('sedge',col,v,fs_)
del blades,v,fs_
for i in range(int(380 * FL)):                              # golden / rust dwarf-shrub clumps
    cx = random.uniform(X0, X1); cy = random.uniform(Y0, Y1)
    color = random.choice(('#B09746', '#C9AD62', '#9F6533', '#AB6431', '#AD593E', '#A0523D', '#939550'))
    for j in range(random.randint(5, 12)):
        x = cx + random.gauss(0, 2.5); y = cy + random.gauss(0, 1.8)
        lo, hi = wet_limits(x)
        if not free(x, y, 1) or lo - 2 < y < hi + 2: continue
        z = ground(x, y)[0]; r = random.uniform(.32,.84); counts['shrubs'] += 1
        for k2 in range(3):
            a = k2 * math.tau / 3 + random.random()
            ball('shrubs', color, (x + math.cos(a) * r * .7, y + math.sin(a) * r * .7, z + .55 * r), r * random.uniform(.75, 1.05), sz=.65, sub=1)
def willow(x, y):                                           # grey willow bush, 2-3 m, never a tree
    if not free(x, y, 1): return
    z = ground(x, y)[0]; r = random.uniform(.7, 1.0); color = random.choice(('#8B8454', '#B39C63', '#858553', '#A5965B')); counts['willows'] += 1
    for k2 in range(4):
        ball('willows', color, (x + random.gauss(0, .8 * r), y + random.gauss(0, .6 * r), z + r * (.7 + .4 * k2)), r * random.uniform(.75, 1.0), sz=1.0, sub=2)
if FL:
    rw = [p for p in dense(river, 6) if -280 < p.x < 320 and p.y < 430]
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
         sx=random.uniform(1, 1.4), sy=random.uniform(.8, 1.2), sz=.63, sub=1)
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
FAR = {'industry': ((IX, IY), .77, (RX0, RY0)), 'helipad': ((PX, PY), .60, (57, 20)), 'abk': ((AX, AY), .67, (AX, AY)), 'chums': ((-60, 180), 1.25, CHUM)}
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

# ---- R5-05c (Michael r8, restored R5-06): far mountain ridges, barely visible in haze (colour pre-mixed with the sky) ----
for k, (y0, depth, hmax, color) in enumerate(((1300, 350, 117, '#839BB0'), (1850, 510, 220, '#9EADBD'), (2490,620,320,'#B2BBC9'))):
    xs_=frange(-6000,6001,23); m=len(xs_); vs_=[]; cs=[]; fs_=[]
    for j in range(12):
        t=j/11
        for i,x in enumerate(xs_):
            y=y0+(t+.08*math.sin(x*.008))+depth*t + 64*N(x,t,.004,31+k)
            crest=.58+.24*math.sin(x*.008+k)+.34*N(x,1,.004,34+k)+.12*N(x,0,.017,38+k)
            profile=math.sin(math.pi*t)**1.07; rock=N(x,y,.012,40+k); hgt=.49*hmax*max(.12,crest)*profile*(1+.20*rock)
            vs_.append((x,y,-5+hgt+11*profile*rock)); shade=smooth01(-.5,.5,N(x+60*t,y,.008,30+k)+.55*math.sin(x*.026+8*t)); cc=lerpc(srgb(color)[:3],srgb('#D6CABC')[:3],shade*.46*profile)
            if hgt>hmax*.36: cc=lerpc(cc,srgb('#DFDFDC')[:3],smooth01(.36,.48,hgt/hmax)*.45)
            cs.extend((*cc,1))
            if i and j:
                a=j*m+i; fs_.extend([(a-m-1,a-m,a),(a-m-1,a,a-1)])
    ob=mesh('mountains',color,vs_,fs_,'ground'); ob.data.color_attributes.new('col','FLOAT_COLOR','POINT').data.foreach_set('color',cs)

# ---- clear daylight, soft shadows, no ink (the painted map has no outlines) -------
scene.render.engine = 'BLENDER_EEVEE'
scene.world = bpy.data.worlds.new('daylight'); scene.world.use_nodes = True
bg = scene.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.80, .86, .93, 1); bg.inputs[1].default_value = .3
_wn, _wl = scene.world.node_tree.nodes, scene.world.node_tree.links
_tc, _sz, _cr, _sky, _lp, _mx = (_wn.new(t) for t in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ', 'ShaderNodeValToRGB', 'ShaderNodeBackground', 'ShaderNodeLightPath', 'ShaderNodeMixShader'))
_cr.color_ramp.elements[0].position, _cr.color_ramp.elements[0].color = 0, (*srgb('#C3D0DC')[:3], 1)
_cr.color_ramp.elements[1].position, _cr.color_ramp.elements[1].color = .35, (*srgb('#86B2DE')[:3], 1)
_wl.new(_tc.outputs['Generated'], _sz.inputs[0]); _wl.new(_sz.outputs['Z'], _cr.inputs[0]); _wl.new(_cr.outputs[0], _sky.inputs[0])
_wl.new(bg.outputs[0], _mx.inputs[1]); _wl.new(_sky.outputs[0], _mx.inputs[2]); _wl.new(_lp.outputs['Is Camera Ray'], _mx.inputs[0])
_wl.new(_mx.outputs[0], _wn['World Output'].inputs[0])
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

# Both cameras look north: the four axles and pads share ONE ground baseline.
# Use horizontal sensor fit also for portrait, so f is in canvas pixels.
views={'wide': (2400,1800,(-8,-164,105),41,1800,1240), 'tall': (1700,2100,(-6,-134,117),49,1460,1350)}
for name,(W,H,xyz,tilt,f,cy) in views.items():
    cd=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,cd); scene.collection.objects.link(cam)
    cd.type='PERSP'; cd.sensor_fit='HORIZONTAL'; cd.sensor_width=36; cd.lens=f*36/W; cd.clip_end=6000
    cam.location=xyz; cam.rotation_euler=(rad(90-tilt),0,0); cd.shift_y=(cy-H/2)/W
    cam['W']=W; cam['H']=H
# Separate recipient objects: one per branch, none on the shared default plate.
def person(group,x,y,coat,trim,cap,helmet=False):
    M=at(x,y,rad(-78),2.4,.07)
    for s in (-1,1):
        beam(group,'#3D3B3C',(0,s*.105,.06),(.01,s*.105,.74),.15,M=M)
        box(group,'#514236',(.035,s*.105,.09),(.28,.17,.14),M=M)
    cyl(group,coat,(0,0,.94),.30,.75,r2=.22,seg=16,M=M)
    cyl(group,trim,(0,0,.65),.295,.055,seg=16,M=M)
    for s in (-1,1):
        end=(.10,s*.39,1.48 if s<0 else .86)
        beam(group,coat,(0,s*.19,1.23),end,.135,M=M); ball(group,'#C69C76',end,.09,M=M)
    ball(group,cap,(-.02,0,1.53),.218,sz=1.12,M=M)
    ball(group,'#DBAD8C',(.123,0,1.50),.15,sx=.72,sz=1.03,M=M)
    if helmet:
        ball(group,'#D9692C',(0,0,1.66),.208,sz=.65,M=M)
        cyl(group,'#CE5E26',(.037,0,1.63),.23,.035,seg=20,M=M)
    else:
        cyl(group,trim,(0,0,.81),.283,.05,seg=16,M=M)
person('alva',CHUM[0]+1,CHUM[1]-8,'#C7B699','#A54734','#EFE4C9')
person('khor',HERD[0]-5,HERD[1]-9,'#68503F','#D9B875','#7D654F')
person('arseniy',AX+7,AY-20,'#2C4D68','#D87638','#413A36',True)
flush()
for g in ('alva','khor','arseniy'):
    for ob in GROUPS[g]: ob.hide_render=True
bpy.context.view_layer.update()
scene.camera=bpy.data.objects['wide']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'world.blend'),compress=True)
print('R30_WORLD',MODE,counts,flush=True)
