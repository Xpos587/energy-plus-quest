# Scene 1 carrier map v4: blockout (gray boxes + route lines).
# Run: blender --background --factory-startup --python layout.py -- OUTDIR
# Geometry is the single source of truth: plate renders, route polylines in
# screen space and landmark points are all exported from this scene.
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "out")
OUT.mkdir(parents=True, exist_ok=True)

# ---- City grid (metres) -----------------------------------------------------
P = 64.0  # road centre to road centre
ROAD = 14.0  # carriageway width
WALK = 3.0  # sidewalk ring inside each block
LANE = 3.2  # lane centre offset from the road centre line (right-hand traffic)
COLS = range(-5, 8)  # road line indices (x = XL[i])
ROWS = range(-4, 7)  # road line indices (y = YL[j])
# Non-uniform grid (v4b): a big warehouse block (0,0) in the middle of a 3x3
# district with narrow side columns/rows, so every loop fits a close camera.
WB, HB = 84.0, 80.0  # warehouse block, road centre to road centre
SA, SB = 48.0, 44.0  # side columns / rows


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
TRUCK_REAL = (16.5, 2.6, 3.9)
TRUCK_SCALE = 1.8  # game scale: rigs read like the game's other scenes
TRUCK = tuple(v * TRUCK_SCALE for v in TRUCK_REAL)
WH_DEPTH = 22.0
WH_H = 9.0

C = {
    "ground": (0.93, 0.90, 0.82, 1),
    "road": (0.48, 0.50, 0.54, 1),
    "walk": (0.90, 0.86, 0.76, 1),
    "grass": (0.62, 0.74, 0.42, 1),
    "house": (0.86, 0.84, 0.82, 1),
    "house2": (0.80, 0.78, 0.76, 1),
    "yard": (0.62, 0.63, 0.66, 1),
    "wh": (0.96, 0.96, 0.97, 1),
    "brand": (0.0, 0.235, 0.65, 1),
    "orange": (1.0, 0.333, 0.0, 1),
    "office": (0.55, 0.72, 0.90, 1),
    "tree": (0.45, 0.62, 0.30, 1),
    "treeY": (0.93, 0.72, 0.20, 1),
    "old": (0.86, 0.15, 0.13, 1),
    "near": (0.10, 0.35, 0.85, 1),
    "crew": (0.18, 0.70, 0.22, 1),
    "old4": (0.98, 0.78, 0.05, 1),
    "express": (1, 1, 1, 1),
    "roof": (0.78, 0.36, 0.28, 1),
}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def box(name, x0, y0, x1, y1, z0, z1, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    o.color = color
    return o


TREES = []


def tree(x, y, h=7, kind="tree"):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=h * 0.45, location=(x, y, h * 0.22))
    bpy.context.object.color = (0.45, 0.32, 0.2, 1)
    bpy.context.object.name = "trunk"
    bpy.ops.mesh.primitive_ico_sphere_add(radius=h * 0.32, subdivisions=2, location=(x, y, h * 0.62))
    o = bpy.context.object
    o.name = "crown"
    TREES.append((x, y, h, kind))
    o.scale.z = 1.25
    o.color = C[kind]


ground = box("ground", -800, -800, 1100, 1100, -0.2, 0, C["ground"])

# Roads: one strip per grid line, spanning the whole visible city.
X0, X1 = XL[COLS[0]] - P, XL[COLS[-1]] + P
Y0, Y1 = YL[ROWS[0]] - P, YL[ROWS[-1]] + P
for i in COLS:
    box(f"road_v{i}", XL[i] - ROAD / 2, Y0, XL[i] + ROAD / 2, Y1, 0, 0.05, C["road"])
for j in ROWS:
    box(f"road_h{j}", X0, YL[j] - ROAD / 2, X1, YL[j] + ROAD / 2, 0, 0.05, C["road"])

# Block plates (sidewalk) and content.
import random

# Block types near the routes are fixed by hand: blocks south of the warehouse
# stay low so it reads as the centre; tall towers sit only in the south-west
# corner of a block (both cameras look north/east, so they hide nothing but
# their own block interior).
BLOCK_TYPE = {
    (0, -1): "plaza", (-1, 0): "gas", (1, 0): "stadium", (0, 1): "shop",
    (-1, -1): "cottages", (1, -1): "L", (-1, 1): "L", (1, 1): "cottages",
    (2, 0): "tower", (2, 1): "L", (2, -1): "shop", (-2, 0): "L", (-2, 1): "tower", (-2, -1): "cottages",
    (0, 2): "L", (1, 2): "tower", (-1, 2): "cottages", (0, -2): "L", (1, -2): "cottages", (-1, -2): "tower",
}


def gable(name, x0, y0, x1, y1, z0, rise, color, along_x=True):
    """Pitched roof prism over a rectangle."""
    if along_x:
        ym = (y0 + y1) / 2
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, ym, z0 + rise), (x1, ym, z0 + rise)]
        f = [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    else:
        xm = (x0 + x1) / 2
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (xm, y0, z0 + rise), (xm, y1, z0 + rise)]
        f = [(0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (3, 5, 2), (0, 3, 2, 1)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.color = color
    return o


def build_block(i, j, ix0, iy0, ix1, iy1):
    """Block content scaled to the block interior (blocks differ in size)."""
    kind = BLOCK_TYPE.get((i, j)) or random.choice(["L", "L", "tower", "cottages", "shop"])
    tag = f"{i}_{j}"
    w, h = ix1 - ix0, iy1 - iy0
    small = min(w, h) < 32
    if kind == "L":
        d = min(11, 0.38 * min(w, h))
        h1 = random.choice([12, 15] if small else [12, 15, 18])
        box(f"house_{tag}_s", ix0, iy0, ix0 + w * random.uniform(0.62, 0.8), iy0 + d, 0.25, h1, C["house"])
        if h > 2.4 * d:
            box(f"house_{tag}_w", ix0, iy0 + d + 2, ix0 + d, iy0 + h * random.uniform(0.6, 0.8), 0.25, random.choice([9, 12]), C["house2"])
        box(f"lawn_{tag}", ix0 + d + 1, iy0 + d + 1, ix1, iy1, 0.25, 0.32, C["grass"])
        for _ in range(3 if small else 4):
            tree(random.uniform(ix0 + d + 4, ix1 - 3), random.uniform(iy0 + d + 4, iy1 - 3), random.uniform(5, 7), random.choice(["tree", "treeY"]))
    elif kind == "tower":
        t = min(17, 0.5 * min(w, h))
        box(f"house_{tag}_tower", ix0, iy0, ix0 + t, iy0 + t, 0.25, random.choice([21, 24, 27]), C["house"])
        if w > t + 12:
            box(f"house_{tag}_podium", ix0 + t, iy0, ix0 + min(w, t + 19), iy0 + min(12, t * 0.7), 0.25, 7, C["house2"])
        box(f"lawn_{tag}", ix0 + 1, iy0 + t + 1, ix1, iy1, 0.25, 0.32, C["grass"])
        for _ in range(4):
            tree(random.uniform(ix0 + 3, ix1 - 3), random.uniform(iy0 + t + 4, iy1 - 3), random.uniform(5, 7), random.choice(["tree", "treeY"]))
    elif kind == "cottages":
        box(f"lawn_{tag}", ix0, iy0, ix1, iy1, 0.25, 0.32, C["grass"])
        na, nb = max(1, int(w // 22)), max(1, int(h // 20))
        for a in range(na):
            for b in range(nb):
                x0 = ix0 + 3 + a * (w - 6) / na
                y0 = iy0 + 3 + b * (h - 6) / nb
                box(f"cottage_{tag}_{a}{b}", x0, y0, x0 + 11, y0 + 8, 0.32, 5.5, C["house"])
                gable(f"roof_{tag}_{a}{b}", x0 - 0.5, y0 - 0.5, x0 + 11.5, y0 + 8.5, 5.5, 3.2, C["roof"], along_x=True)
                if (w - 6) / na > 18:
                    tree(x0 + 15, y0 + 4, random.uniform(5, 6.5), random.choice(["tree", "treeY"]))
    elif kind == "shop":
        sd = min(18, h * 0.55)
        box(f"shop_{tag}", ix0, iy0, ix0 + min(w - 2, 40), iy0 + sd, 0.25, 7.5, C["house2"])
        box(f"parking_{tag}", ix0, iy0 + sd + 2, ix1, iy1, 0.25, 0.3, C["yard"])
        if w > 44:
            for _ in range(3):
                tree(random.uniform(ix0 + 42, ix1 - 2), random.uniform(iy0 + 2, iy0 + sd - 2), random.uniform(5, 6.5), random.choice(["tree", "treeY"]))
    elif kind == "stadium":
        sw = min(11, w * 0.4)
        box(f"house_{tag}_school", ix0, iy0, ix0 + sw, iy0 + h * 0.55, 0.25, 10, C["house"])
        box(f"field_{tag}", ix0 + sw + 2, iy0 + 2, ix1 - 2, iy1 - 2, 0.25, 0.33, C["grass"])
        for _ in range(3):
            tree(random.uniform(ix0 + 2, ix0 + sw - 2), random.uniform(iy0 + h * 0.6, iy1 - 3), random.uniform(5, 6.5), random.choice(["tree", "treeY"]))
    elif kind == "plaza":
        box(f"plaza_{tag}", ix0, iy0, ix1, iy1, 0.25, 0.3, C["walk"])
        cx, cy = (ix0 + ix1) / 2, (iy0 + iy1) / 2
        r = min(w, h) * 0.22
        box(f"fountain_{tag}", cx - r, cy - r, cx + r, cy + r, 0.3, 0.9, C["office"])
        for k in range(10):
            a = k / 10 * 2 * math.pi
            tree(cx + (w / 2 - 4) * math.cos(a), cy + (h / 2 - 3) * math.sin(a), random.uniform(5.5, 7), random.choice(["tree", "treeY"]))
    elif kind == "gas":
        box(f"gas_{tag}_apron", ix0, iy0, ix1, iy1, 0.25, 0.31, C["yard"])
        box(f"gas_{tag}_shop", ix0 + 2, iy1 - 12, ix1 - 2, iy1 - 2, 0.31, 4.5, C["wh"])
        cy0 = iy0 + 10
        box(f"gas_{tag}_canopy", ix0 + 3, cy0, ix1 - 3, cy0 + 16, 5.2, 6.2, C["brand"])
        for k in range(2):
            px = ix0 + w * (0.33 + 0.34 * k)
            box(f"gas_{tag}_pump{k}", px - 0.6, cy0 + 7.4, px + 0.6, cy0 + 8.6, 0.31, 1.9, C["wh"])
            box(f"gas_{tag}_post{k}", px - 0.25, cy0 + 3, px + 0.25, cy0 + 3.5, 0.31, 5.2, C["wh"])
            box(f"gas_{tag}_postb{k}", px - 0.25, cy0 + 12.5, px + 0.25, cy0 + 13, 0.31, 5.2, C["wh"])
        box(f"gas_{tag}_totem", ix1 - 3, iy0 + 1, ix1 - 1.5, iy0 + 2.2, 0.31, 7, C["brand"])


random.seed(4)
DOOR_W = 6.0
DOOR_GAP = 11.0


def DOOR_X(k):
    """West edge of dock door k (warehouse block interior starts at ROAD/2+WALK)."""
    return ROAD / 2 + WALK + 9 + k * DOOR_GAP


SPECIAL = {(0, 0): "warehouse", (3, 0): "park"}
for i in list(COLS)[:-1]:
    for j in list(ROWS)[:-1]:
        bx0, by0 = XL[i] + ROAD / 2, YL[j] + ROAD / 2
        bx1, by1 = XL[i + 1] - ROAD / 2, YL[j + 1] - ROAD / 2
        box(f"block_{i}_{j}", bx0, by0, bx1, by1, 0, 0.25, C["walk"])
        ix0, iy0, ix1, iy1 = bx0 + WALK, by0 + WALK, bx1 - WALK, by1 - WALK
        kind = SPECIAL.get((i, j))
        if kind == "warehouse":
            # Warehouse at the back of the block, docks face the south road
            # (towards the camera), office tower in the north-east corner.
            # Warehouse near the back of the block, docks face the south road
            # (towards both cameras). Low enough not to hide the lane behind.
            wf = iy1 - 3 - WH_DEPTH  # front wall (dock side)
            wx1_ = ix1 - 14
            box("warehouse", ix0, wf, wx1_, iy1 - 3, 0.25, WH_H, C["wh"])
            for k, (a, b, c, d) in enumerate(((ix0 - 0.3, wf - 0.3, wx1_ + 0.3, wf + 0.7), (ix0 - 0.3, iy1 - 3.7, wx1_ + 0.3, iy1 - 2.7),
                                              (ix0 - 0.3, wf - 0.3, ix0 + 0.7, iy1 - 2.7), (wx1_ - 0.7, wf - 0.3, wx1_ + 0.3, iy1 - 2.7))):
                box(f"warehouse_cornice{k}", a, b, c, d, WH_H - 1.0, WH_H + 0.6, C["brand"])
            box("warehouse_base", ix0 - 0.05, wf - 0.05, wx1_ + 0.05, iy1 - 2.95, 0.25, 0.9, C["brand"])
            # rooftop sign board over the docks, blank: the word is drawn by the game
            sx = (ix0 + wx1_) / 2
            box("warehouse_sign", sx - 10, wf + 0.2, sx + 10, wf + 0.8, WH_H + 0.4, WH_H + 4.4, C["wh"])
            for k in range(3):
                dx = DOOR_X(k)
                box(f"dock_door_{k}", dx, wf - 0.4, dx + DOOR_W, wf + 0.1, 1.0, 6.0, C["brand"])
            # Office in the front-right corner, beside the yard entrance.
            box("office", ix1 - 12, iy0, ix1, iy0 + 14, 0.25, 12, C["office"])
            box("yard", ix0, iy0, wx1_, wf, 0.25, 0.32, C["yard"])
            for k in range(4):
                lx = DOOR_X(k) - 2.5 if k < 3 else DOOR_X(2) + DOOR_W + 2.5
                box(f"bay_{k}", lx, wf - 20, lx + 0.3, wf - 1, 0.32, 0.34, (0.95, 0.85, 0.3, 1))
        elif kind == "park":
            box("park", ix0, iy0, ix1, iy1, 0.25, 0.35, C["grass"])
            for _ in range(14):
                tree(random.uniform(ix0 + 3, ix1 - 3), random.uniform(iy0 + 3, iy1 - 3), random.uniform(6, 9), random.choice(["tree", "treeY"]))
        else:
            build_block(i, j, ix0, iy0, ix1, iy1)


# ---- Routes -----------------------------------------------------------------
def rect_loop(x0, y0, x1, y1, inset, clockwise, radius):
    """Lane centre loop around a rectangle of road centre lines."""
    x0, y0, x1, y1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    corners = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]  # clockwise from SW
    if not clockwise:
        corners = corners[::-1]
    pts = []
    n = len(corners)
    for k in range(n):
        a = Vector(corners[k - 1])
        b = Vector(corners[k])
        c = Vector(corners[(k + 1) % n])
        d1 = (b - a).normalized()
        d2 = (c - b).normalized()
        p0 = b - d1 * radius
        p1 = b + d2 * radius
        # Quadratic Bezier corner: smooth enough for a 16 m rig.
        for s in range(9):
            t = s / 8
            q = p0 * (1 - t) ** 2 + b * 2 * (1 - t) * t + p1 * t * t
            pts.append((q.x, q.y))
    return pts


# Right-hand traffic. Block loops run clockwise (right turns hug their own
# corners, lane on the block side); the green rig runs the outer ring
# counter-clockwise in the outer lane. Every shared street is then used in
# opposite lanes and no two turning paths cross.
# v4b: the warehouse block is the centre; blue circles it, red and yellow run
# the west and east columns, green runs the whole 3x3 district.
ROUTES = {
    "near": rect_loop(XL[0], YL[0], XL[1], YL[1], LANE, True, 10),
    "old": rect_loop(XL[-1], YL[-1], XL[0], YL[2], LANE, True, 10),
    "old4": rect_loop(XL[1], YL[-1], XL[2], YL[2], LANE, True, 10),
    "crew": rect_loop(XL[-1], YL[-1], XL[2], YL[2], -LANE, False, 14),
}
SPEED_KMH = {"old": 36, "near": 17, "crew": 48, "old4": 27}


def length(pts):
    return sum((Vector(pts[k]) - Vector(pts[k - 1])).length for k in range(len(pts)))


def ribbon(name, pts, width, z, color):
    verts, faces = [], []
    n = len(pts)
    for k in range(n):
        a = Vector(pts[k - 1])
        b = Vector(pts[(k + 1) % n])
        d = (b - a).normalized()
        nrm = Vector((-d.y, d.x)) * width / 2
        p = Vector(pts[k])
        verts += [(p.x + nrm.x, p.y + nrm.y, z), (p.x - nrm.x, p.y - nrm.y, z)]
    for k in range(n):
        a, b = 2 * k, 2 * ((k + 1) % n)
        faces.append((a, a + 1, b + 1, b))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    o = bpy.data.objects.new(name, mesh)
    o.color = color
    bpy.context.collection.objects.link(o)
    return o


def at(pts, s):
    total = length(pts)
    s %= total
    for k in range(len(pts)):
        a, b = Vector(pts[k]), Vector(pts[(k + 1) % len(pts)])
        seg = (b - a).length
        if s <= seg:
            return a.lerp(b, s / seg if seg else 0), math.atan2(b.y - a.y, b.x - a.x)
        s -= seg
    return Vector(pts[0]), 0.0


route_objs = []
for rid, pts in ROUTES.items():
    route_objs.append(ribbon(f"route_{rid}", pts, 1.3, 0.4, C[rid]))
    total = length(pts)
    # Direction arrows every ~40 m.
    for k in range(int(total // 40)):
        p, ang = at(pts, k * 40 + 20)
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=2.2, depth=0.2, location=(p.x, p.y, 0.45))
        o = bpy.context.object
        o.rotation_euler = (0, 0, ang - math.pi / 2)
        o.scale = (0.8, 1.4, 1)
        o.color = C[rid]
        route_objs.append(o)

# Placeholder rigs (blockout only).
START = {"near": 0.15, "old": 0.55, "old4": 0.35, "crew": 0.05}
truck_objs = []
for rid, pts in ROUTES.items():
    p, ang = at(pts, START[rid] * length(pts))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(p.x, p.y, TRUCK[2] / 2 + 0.05))
    o = bpy.context.object
    o.scale = TRUCK
    o.rotation_euler = (0, 0, ang)
    o.color = C[rid]
    o.name = f"placeholder_{rid}"
    o["route_s"] = START[rid] * length(pts)
    truck_objs.append(o)

# Landmarks.
WH_FRONT = HB - ROAD / 2 - WALK - 3 - WH_DEPTH
DOCK = Vector((DOOR_X(1) + DOOR_W / 2, WH_FRONT - 4, 0.4))  # middle door
EXPRESS = Vector((DOCK.x, WH_FRONT - TRUCK[0] / 2 - 0.8, 0.4))  # backed up to the door
bpy.ops.mesh.primitive_cube_add(size=1, location=(EXPRESS.x, EXPRESS.y, TRUCK[2] / 2 + 0.3))
ex = bpy.context.object
ex.scale = TRUCK
ex.rotation_euler = (0, 0, math.pi / 2)
ex.color = C["express"]
ex.name = "placeholder_express"
truck_objs.append(ex)
AUTOPICK = Vector((DOOR_X(2) + DOOR_W + 6, HB - ROAD / 2 - WALK - 3 - WH_DEPTH / 2 + 3, WH_H + 0.4))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.6, location=AUTOPICK)
bpy.context.object.color = C["orange"]
bpy.context.object.name = "marker_autopick"

# ---- Render setup -----------------------------------------------------------
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "OBJECT"
sh.show_object_outline = True
sh.object_outline_color = (0.15, 0.15, 0.2)
sh.show_shadows = True
sh.shadow_intensity = 0.35
sh.show_cavity = True
scene.display.light_direction = (-0.45, -0.35, 0.82)
scene.view_settings.view_transform = "Standard"
scene.view_settings.exposure = 0.0
sh.light = "FLAT"
sh.show_specular_highlight = False
scene.render.film_transparent = False
world = bpy.data.worlds.new("w")
scene.world = world
world.color = (0.80, 0.88, 0.95)

def forward_of(az, el):
    from mathutils import Euler

    rot = (math.radians(90 - el), 0, math.radians(az))
    m = Euler(rot, "XYZ").to_matrix()
    return rot, m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0)), m @ Vector((0, 0, -1))


# Plates. Content must stay inside `keep` (normalised, y down) so that every
# target viewport shows it next to the question panel:
#  wide 21:9 plate, "cover" fit: 1440x844 (1.71) crops the sides to
#  u 0.13..0.87 with the panel at the bottom right; 844x334 (2.53) crops
#  top/bottom and the panel takes u > 0.61. Keep u 0.16..0.60, v 0.08..0.92.
#  tall 2:3 plate: 390x582 shows it whole; 320x310 and 768x704 (~1:1) show
#  the central square only. Keep v 0.20..0.80, u 0.04..0.96.
PLATES = {
    "wide": dict(az=float(__import__("os").environ.get("WIDE_AZ", -18)), el=48, res=(2800, 1200), keep=(0.15, 0.06, 0.62, 0.93)),
    "tall": dict(az=float(__import__("os").environ.get("TALL_AZ", -70)), el=50, res=(1200, 1800), keep=(0.05, 0.20, 0.95, 0.80)),
}


def keep_points():
    pts = [Vector((x, y, 0.4)) for pts in ROUTES.values() for (x, y) in pts]
    pts += [DOCK, EXPRESS, AUTOPICK]
    # whole warehouse + office silhouette
    wh = bpy.data.objects["warehouse"]
    of = bpy.data.objects["office"]
    for o in (wh, of):
        pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    # rig half-length margin around every lane point
    m = TRUCK[0] / 2
    out = []
    for p in pts:
        out += [p + Vector((dx, dy, 0)) for dx in (-m, m) for dy in (-m, m)] if p.z < 1 else [p]
    return out


def frame(name, spec):
    rot, R, U, F = forward_of(spec["az"], spec["el"])
    W, H = spec["res"]
    aspect = W / H
    u0, v0, u1, v1 = spec["keep"]
    pr = [(p.dot(R), p.dot(U)) for p in keep_points()]
    xs = [a for a, _ in pr]
    ys = [b for _, b in pr]
    # Exact fit: frame width S such that the content box lands in keep.
    # keep is in y-down screen space; camera U points up.
    span_x = (max(xs) - min(xs)) / (u1 - u0)
    span_y = (max(ys) - min(ys)) / (v1 - v0) * aspect
    S = max(span_x, span_y)
    # centre so that min x maps to u0 and max y maps to v0 (top)
    cx = min(xs) + (0.5 - u0) * S - ((u1 - u0) * S - (max(xs) - min(xs))) / 2
    Hh = S / aspect
    cy = max(ys) - (0.5 - v0) * Hh + ((v1 - v0) * Hh - (max(ys) - min(ys))) / 2
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    bpy.context.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.ortho_scale = S
    cam.data.clip_end = 4000
    cam.rotation_euler = rot
    cam.location = R * cx + U * cy - F * 900
    return cam


def clear_occluders():
    """Lower or remove anything that hides a lane, the dock or the express spot
    from either camera (raycast towards the camera, rig roof and base)."""
    helpers = route_objs + truck_objs
    for o in helpers:
        o.hide_viewport = True
    samples = []
    for pts in ROUTES.values():
        for k in range(len(pts)):
            a, b = Vector(pts[k - 1]), Vector(pts[k])
            n = max(1, int((b - a).length // 2))
            for q in range(n):
                p = a.lerp(b, q / n)
                samples += [Vector((p.x, p.y, 0.6)), Vector((p.x, p.y, TRUCK[2]))]
    samples += [DOCK, EXPRESS, Vector((EXPRESS.x, EXPRESS.y, TRUCK[2]))]
    for k in range(3):
        d = bpy.data.objects[f"dock_door_{k}"]
        samples.append(d.matrix_world.translation + Vector((0, -0.6, 0)))
    report = {}
    for rounds in range(12):
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        hits = {}
        for name, spec in PLATES.items():
            _, _, _, F = forward_of(spec["az"], spec["el"])
            back = -F
            for p in samples:
                ok, loc, nrm, idx, obj, mat = scene.ray_cast(dg, p + back * 0.3, back)
                if ok and obj.name not in ("ground",) and not obj.name.startswith(("road_", "block_", "yard", "bay_", "park", "lawn_", "parking_", "field_", "plaza_", "fountain_")):
                    hits.setdefault(obj.name, 0)
                    hits[obj.name] += 1
        if rounds == 0:
            report["initialOccluders"] = dict(hits)
        if not hits:
            break
        for nm in hits:
            o = bpy.data.objects[nm]
            if nm.startswith(("house_", "shop_")) and o.dimensions.z > 7:
                top = o.location.z + o.dimensions.z / 2
                newh = max(6, (top - 0.25) * 0.75)
                o.scale.z = newh
                o.location.z = 0.25 + newh / 2
            elif nm == "office" and o.dimensions.z > 7:
                o.scale.z = o.dimensions.z - 1.5
                o.location.z = 0.25 + o.scale.z / 2
            elif nm.startswith(("crown", "trunk", "house_", "roof_", "cottage_", "gas_")):
                bpy.data.objects.remove(o)
            else:
                report.setdefault("unfixed", set()).add(nm)
    report["remaining"] = hits
    for o in helpers:
        o.hide_viewport = False
    report.pop("unfixed", None)
    return report


def face_of(name):
    o = bpy.data.objects[name]
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    y0 = min(v.y for v in vs)
    x0, x1 = min(v.x for v in vs), max(v.x for v in vs)
    z0, z1 = min(v.z for v in vs), max(v.z for v in vs)
    return [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)]


def sign_face():
    return face_of("warehouse_sign")


def gas_totem_face():
    name = next(o.name for o in bpy.data.objects if o.name.startswith("gas_") and o.name.endswith("_totem"))
    return face_of(name)


def project(cam, res, p):
    from bpy_extras.object_utils import world_to_camera_view

    v = world_to_camera_view(scene, cam, Vector((p[0], p[1], p[2] if len(p) > 2 else 0.4)))
    return [round(v.x, 5), round(1 - v.y, 5)]


occlusion = clear_occluders()
print("OCCLUSION", occlusion)

manifest = {"grid": {"P": P, "road": ROAD, "lane": LANE, "xl": XL, "yl": YL}, "speedKmh": SPEED_KMH, "occlusion": occlusion, "plates": {}}
for name, spec in PLATES.items():
    cam = frame(name, spec)
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = spec["res"]
    scene.render.resolution_percentage = 100
    bpy.context.view_layer.update()
    if not __import__("os").environ.get("NO_RENDER"):
        scene.render.filepath = str(OUT / f"blockout-{name}.png")
        bpy.ops.render.render(write_still=True)
    manifest["plates"][name] = {
        "az": spec["az"],
        "el": spec["el"],
        "res": spec["res"],
        "keep": spec["keep"],
        "orthoScale": cam.data.ortho_scale,
        "metresPerPx": cam.data.ortho_scale / spec["res"][0],
        "routes": {rid: [project(cam, spec["res"], p) for p in pts] for rid, pts in ROUTES.items()},
        "dock": project(cam, spec["res"], DOCK),
        "express": project(cam, spec["res"], EXPRESS),
        "autopick": project(cam, spec["res"], AUTOPICK),
        "warehouse": project(cam, spec["res"], bpy.data.objects["warehouse"].location),
        "office": project(cam, spec["res"], bpy.data.objects["office"].location + Vector((0, 0, 7))),
        # front face of the blank sign board (TL, TR, BR, BL): the game letters "Склад" here
        "sign": [project(cam, spec["res"], c) for c in sign_face()],
        "gasTotem": [project(cam, spec["res"], c) for c in gas_totem_face()],
    }
manifest["routeLengthM"] = {rid: round(length(pts), 1) for rid, pts in ROUTES.items()}
manifest["routesWorld"] = {rid: [[round(x, 3), round(y, 3)] for x, y in pts] for rid, pts in ROUTES.items()}
manifest["truckM"] = list(TRUCK)


def world_box(name):
    o = bpy.data.objects[name]
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    return [round(min(v.x for v in vs), 3), round(min(v.y for v in vs), 3), round(min(v.z for v in vs), 3),
            round(max(v.x for v in vs), 3), round(max(v.y for v in vs), 3), round(max(v.z for v in vs), 3)]


manifest["boxes"] = {n: world_box(n) for n in ("warehouse", "warehouse_sign", "office", "yard") if n in bpy.data.objects}
for name, spec in PLATES.items():
    cam = bpy.data.objects[name]
    # exact ortho projection: plate px = M @ (x, y, z, 1)
    W, H = spec["res"]
    from bpy_extras.object_utils import world_to_camera_view as w2c
    scene.render.resolution_x, scene.render.resolution_y = spec["res"]  # w2c uses the scene aspect
    bpy.context.view_layer.update()
    pts = [Vector((0, 0, 0)), Vector((100, 0, 0)), Vector((0, 100, 0)), Vector((0, 0, 100))]
    pr = [(w2c(scene, cam, p).x, 1 - w2c(scene, cam, p).y) for p in pts]
    o = (pr[0][0] * W, pr[0][1] * H)
    cols = [((q[0] * W - o[0]) / 100, (q[1] * H - o[1]) / 100) for q in pr[1:]]
    manifest["plates"][name]["proj"] = [[cols[0][0], cols[1][0], cols[2][0], o[0]], [cols[0][1], cols[1][1], cols[2][1], o[1]]]
(OUT / "blockout.json").write_text(json.dumps(manifest, indent=1))
if not __import__("os").environ.get("NO_RENDER"):
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "blockout.blend"))
print("OK", manifest["routeLengthM"])
