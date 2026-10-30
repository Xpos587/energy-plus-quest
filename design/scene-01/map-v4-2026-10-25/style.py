# Scene 1 map v4: style pass over the approved blockout.
# blender --background --factory-startup --python style.py -- OUTDIR [test|wide|tall]
# Builds the blockout geometry (layout.py), then replaces the gray boxes with
# illustration materials (toon ramp + outlines), road markings, facade
# windows, trees, props and real truck models.
import math
import os
import random
import sys
from pathlib import Path

import bpy
import time
T0 = time.time()


def tick(msg):
    print(f"TICK {time.time()-T0:7.1f}s {msg}", flush=True)

from mathutils import Euler, Vector

HERE = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
OUT = Path(args[0] if args else "out-style")
MODE = args[1] if len(args) > 1 else "test"
OUT.mkdir(parents=True, exist_ok=True)

# ---- 1. Blockout geometry (single source of truth) --------------------------
os.environ["NO_RENDER"] = "1"
sys.argv = [sys.argv[0], "--", str(OUT / "layout")]
g = {"__name__": "layout", "__file__": str(HERE / "layout.py")}
exec(compile((HERE / "layout.py").read_text(), "layout.py", "exec"), g)
P, ROAD, WALK, LANE, WH_H = g["P"], g["ROAD"], g["WALK"], g["LANE"], g["WH_H"]
COLS, ROWS, ROUTES, TRUCK = g["COLS"], g["ROWS"], g["ROUTES"], g["TRUCK"]
XL, YL = g["XL"], g["YL"]
TRUCK_REAL, TRUCK_SCALE = g["TRUCK_REAL"], g["TRUCK_SCALE"]
scene = bpy.context.scene
random.seed(11)


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


PAL = {
    "asphalt": "#9AA5B4",
    "mark": "#F7F8FA",
    "walk": "#F1E7D3",
    "curb": "#E2D6BE",
    "grass": "#A9CC6E",
    "lawn": "#93BE5C",
    "roof": "#E4D8C6",
    "glass": "#6E9FD8",
    "frame": "#FFFFFF",
    "wh": "#F6F7F9",
    "brand": "#003CA6",
    "orange": "#FF5500",
    "door": "#3566C2",
    "yard": "#CDD2D8",
    "bay": "#F2C230",
    "trunk": "#8A5A3C",
    "line": "#1F2B3C",
}
FACADES = ["#EE9E74", "#F4C39A", "#F5F1EA", "#E8B48A", "#F2D3A6", "#DE8E6A"]
CROWNS = ["#F2C230", "#F0A32A", "#E8892B", "#9BC255", "#7FB04A", "#F5D046"]

tick('# ---- 2. Materials')
# ---- 2. Materials -------------------------------------------------------------
LINES_OFF = bpy.data.collections.new("NoLines")
scene.collection.children.link(LINES_OFF)


def toon(name, build_color, ramp=(0.70, 0.86, 1.0)):
    """Lighting -> soft 3-step ramp -> multiplied by the surface colour."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    cr = nt.nodes.new("ShaderNodeValToRGB")
    e = cr.color_ramp
    e.interpolation = "EASE"
    e.elements[0].position = 0.09
    e.elements[0].color = (ramp[0],) * 3 + (1,)
    e.elements[1].position = 0.5
    e.elements[1].color = (ramp[2],) * 3 + (1,)
    mid = e.elements.new(0.22)
    mid.color = (ramp[1],) * 3 + (1,)
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    sc = nt.nodes.new("ShaderNodeMath")
    sc.operation = "MULTIPLY"
    sc.inputs[1].default_value = 0.4
    nt.links.new(s2r.outputs[0], bw.inputs[0])
    nt.links.new(bw.outputs[0], sc.inputs[0])
    nt.links.new(sc.outputs[0], cr.inputs[0])
    nt.links.new(cr.outputs[0], mul.inputs[6])
    nt.links.new(build_color(nt), mul.inputs[7])
    nt.links.new(mul.outputs[2], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def flat(hexcol):
    def build(nt):
        n = nt.nodes.new("ShaderNodeRGB")
        n.outputs[0].default_value = srgb(hexcol)
        return n.outputs[0]

    return build


def node(nt, kind, **inputs):
    n = nt.nodes.new(kind)
    for k, v in inputs.items():
        setattr(n, k, v)
    return n


def math_node(nt, op, a, b=None, clamp=False):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def mix(nt, fac, a, b):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = "RGBA"
    for i, v in ((0, fac), (6, a), (7, b)):
        if isinstance(v, tuple):
            n.inputs[i].default_value = v
        elif isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[2]


def band(nt, x, lo, hi):
    """1 where lo < fract(x) < hi."""
    f = math_node(nt, "FRACT", x)
    return math_node(nt, "MULTIPLY", math_node(nt, "GREATER_THAN", f, lo), math_node(nt, "LESS_THAN", f, hi))


def facade_parts(nt):
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nrm = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], nrm.inputs[0])
    # horizontal facade coordinate: x on south/north faces, y on east/west
    h = math_node(
        nt,
        "ADD",
        math_node(nt, "MULTIPLY", sep.outputs[0], math_node(nt, "ABSOLUTE", nrm.outputs[1])),
        math_node(nt, "MULTIPLY", sep.outputs[1], math_node(nt, "ABSOLUTE", nrm.outputs[0])),
    )
    roof = math_node(nt, "GREATER_THAN", nrm.outputs[2], 0.7)
    return sep, h, roof


def facade_color(nt):
    info = nt.nodes.new("ShaderNodeObjectInfo")
    sep, h, roof = facade_parts(nt)
    z = math_node(nt, "SUBTRACT", sep.outputs[2], 0.25)
    fx = math_node(nt, "DIVIDE", h, 3.4)
    fz = math_node(nt, "DIVIDE", z, 3.0)
    frame = math_node(nt, "MULTIPLY", band(nt, fx, 0.22, 0.78), band(nt, fz, 0.30, 0.86))
    glass = math_node(nt, "MULTIPLY", band(nt, fx, 0.29, 0.71), band(nt, fz, 0.38, 0.80))
    ground_floor = math_node(nt, "LESS_THAN", z, 0.5)
    frame = math_node(nt, "MULTIPLY", frame, math_node(nt, "SUBTRACT", 1, ground_floor))
    glass = math_node(nt, "MULTIPLY", glass, math_node(nt, "SUBTRACT", 1, ground_floor))
    # glass gets a light diagonal reflection
    refl = band(nt, math_node(nt, "DIVIDE", math_node(nt, "ADD", h, sep.outputs[2]), 2.2), 0.05, 0.22)
    gcol = mix(nt, math_node(nt, "MULTIPLY", refl, 0.5), srgb(PAL["glass"]), srgb("#BFD9F2"))
    c = mix(nt, frame, info.outputs["Color"], srgb(PAL["frame"]))
    c = mix(nt, glass, c, gcol)
    plinth = math_node(nt, "LESS_THAN", z, 0.9)
    c = mix(nt, math_node(nt, "MULTIPLY", plinth, 0.6), c, srgb("#8C7F73"))
    return mix(nt, roof, c, srgb(PAL["roof"]))


def warehouse_color(nt):
    sep, h, roof = facade_parts(nt)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nrm = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], nrm.inputs[0])
    fx = math_node(nt, "DIVIDE", h, 8.5)
    pil = band(nt, fx, 0.0, 0.07)
    not_front = math_node(nt, "GREATER_THAN", nrm.outputs[1], -0.5)
    zwin = math_node(nt, "MULTIPLY", math_node(nt, "GREATER_THAN", sep.outputs[2], 3.6), math_node(nt, "LESS_THAN", sep.outputs[2], 6.4))
    win = math_node(nt, "MULTIPLY", math_node(nt, "MULTIPLY", band(nt, fx, 0.18, 0.88), zwin), not_front)
    mull = math_node(nt, "MULTIPLY", win, band(nt, math_node(nt, "DIVIDE", h, 2.1), 0.0, 0.1))
    c = mix(nt, pil, srgb("#F3E8CF"), srgb(PAL["brand"]))
    c = mix(nt, win, c, srgb("#7FB3E3"))
    c = mix(nt, mull, c, srgb("#FFFFFF"))
    return mix(nt, roof, c, srgb("#DDE2E8"))


def door_color(nt):
    sep, h, roof = facade_parts(nt)
    rib = band(nt, math_node(nt, "DIVIDE", sep.outputs[2], 0.42), 0.0, 0.16)
    return mix(nt, rib, srgb(PAL["door"]), srgb("#264E9E"))


def office_color(nt):
    sep, h, roof = facade_parts(nt)
    mull = math_node(
        nt,
        "MAXIMUM",
        band(nt, math_node(nt, "DIVIDE", h, 1.8), 0.0, 0.10),
        band(nt, math_node(nt, "DIVIDE", math_node(nt, "SUBTRACT", sep.outputs[2], 0.25), 2.7), 0.0, 0.12),
    )
    refl = band(nt, math_node(nt, "DIVIDE", math_node(nt, "ADD", h, sep.outputs[2]), 6.0), 0.1, 0.3)
    g2 = mix(nt, math_node(nt, "MULTIPLY", refl, 0.55), srgb("#78B4E8"), srgb("#D2E8FA"))
    c = mix(nt, mull, g2, srgb("#F4F7FA"))
    return mix(nt, roof, c, srgb("#E6EBF0"))


def object_color(nt):
    return nt.nodes.new("ShaderNodeObjectInfo").outputs["Color"]


MAT = {k: toon(k, flat(PAL[k])) for k in ("asphalt", "walk", "curb", "grass", "lawn", "yard", "bay", "brand", "orange", "trunk")}
MAT["mark"] = toon("mark", flat(PAL["mark"]), ramp=(0.9, 0.95, 1.0))
MAT["facade"] = toon("facade", facade_color)
MAT["warehouse"] = toon("warehouse", warehouse_color, ramp=(0.78, 0.9, 1.0))
MAT["door"] = toon("door", door_color)
MAT["office"] = toon("office", office_color, ramp=(0.82, 0.92, 1.0))
MAT["object"] = toon("object", object_color)
MAT["ground"] = toon("ground", flat("#EDE3CC"))


def set_mat(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)


import bmesh
from mathutils import Matrix

BATCH = {}


def batch_add(key, mat, kind, loc, size=(1, 1, 1), rot=0.0, smooth_faces=False, **kw):
    """Append a primitive to a per-material bmesh (fast, no bpy.ops)."""
    if key not in BATCH:
        BATCH[key] = (bmesh.new(), mat)
    bm = BATCH[key][0]
    M = Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Diagonal((*size, 1))
    if kind == "cube":
        r = bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    elif kind == "ico":
        r = bmesh.ops.create_icosphere(bm, subdivisions=kw.get("sub", 2), radius=1.0, matrix=M)
    elif kind == "cyl":
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=kw.get("seg", 8), radius1=1.0, radius2=1.0, depth=1.0, matrix=M)
    if smooth_faces:
        fs = {f for v in r["verts"] for f in v.link_faces}
        for f in fs:
            f.smooth = True


def batch_flush(nolines=False):
    for key, (bm, mat) in BATCH.items():
        me = bpy.data.meshes.new(key)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(key, me)
        (LINES_OFF if nolines else scene.collection).objects.link(o)
        set_mat(o, mat)
    BATCH.clear()


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def bevel(o, w=0.15, seg=2):
    mod = o.modifiers.new("bevel", "BEVEL")
    mod.width = w
    mod.segments = seg
    mod.limit_method = "ANGLE"
    return mod


def cube(name, loc, size, mat, rot=0.0, color=None, parent=None, bev=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    o.rotation_euler = (0, 0, rot)
    set_mat(o, mat)
    if color:
        o.color = srgb(color)
    if parent:
        o.parent = parent
    if bev:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bevel(o, bev)
    return o


UNIT = bpy.data.meshes.new("unitcube")
_bm = bmesh.new()
bmesh.ops.create_cube(_bm, size=1.0)
_bm.to_mesh(UNIT)
_bm.free()


def obox(name, x0, y0, z0, x1, y1, z1, mat, color=None):
    """Axis-aligned box as an object sharing one mesh (fast, own colour)."""
    me = UNIT.copy()
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    o.scale = (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))
    if color:
        o.color = srgb(color) if isinstance(color, str) else color
    return o


def to_nolines(o):
    for c in o.users_collection:
        c.objects.unlink(o)
    LINES_OFF.objects.link(o)


tick('# ---- 3. Restyle')
# ---- 3. Restyle blockout objects ---------------------------------------------
# Trees that survived the occlusion fixer (crown centre z = 0.62 h).
KEPT_TREES = [(o.location.x, o.location.y, o.location.z / 0.62) for o in bpy.data.objects if o.name.startswith("crown")]
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    n = o.name
    if n.startswith(("route_", "placeholder_", "marker_", "Cone")):
        bpy.data.objects.remove(o)
    elif n == "ground":
        set_mat(o, MAT["ground"])
    elif n.startswith("road_"):
        set_mat(o, MAT["asphalt"])
        to_nolines(o)
    elif n.startswith("block_"):
        set_mat(o, MAT["walk"])
    elif n.startswith(("house_", "shop_", "cottage_")):
        set_mat(o, MAT["facade"])
        o.color = srgb(random.choice(FACADES))
    elif n.startswith("roof_"):
        set_mat(o, MAT["object"])
        o.color = srgb(random.choice(["#C9573F", "#B84A3A", "#D46A48"]))
    elif n == "warehouse":
        set_mat(o, MAT["warehouse"])
    elif n == "warehouse_base" or n.startswith("warehouse_cornice"):
        set_mat(o, MAT["brand"])
    elif n == "warehouse_sign":
        set_mat(o, MAT["object"])
        o.color = srgb("#FFFFFF")
    elif n.startswith("dock_door"):
        set_mat(o, MAT["door"])
    elif n == "office":
        set_mat(o, MAT["office"])
    elif n == "yard" or n.startswith(("parking_", "gas_") ) and n.endswith("apron") or n.startswith("parking_"):
        set_mat(o, MAT["yard"])
    elif n.startswith("bay_"):
        set_mat(o, MAT["bay"])
        to_nolines(o)
    elif n == "park" or n.startswith(("lawn_", "field_")):
        set_mat(o, MAT["lawn"] if n.startswith("lawn_") else MAT["grass"])
    elif n.startswith("plaza_"):
        set_mat(o, MAT["walk"])
    elif n.startswith("fountain_"):
        set_mat(o, MAT["object"])
        o.color = srgb("#7FB7E6")
    elif n.startswith("gas_"):
        set_mat(o, MAT["brand"] if ("canopy" in n or "totem" in n) else MAT["object"])
        o.color = srgb("#F6F7F9")
    elif n in ("crown", "trunk") or n.startswith(("crown.", "trunk.")):
        bpy.data.objects.remove(o)

tick('# Lawns inside')
# Street trees on the south and west kerbs of ordinary blocks (cameras look
# north-east, so they can hide only their own block).
STREET_TREES = []
SKIP = {k for k, v in g["SPECIAL"].items()} | {k for k, v in g["BLOCK_TYPE"].items() if v in ("gas", "plaza")}
for i in list(COLS)[:-1]:
    for j in list(ROWS)[:-1]:
        if (i, j) in SKIP:
            continue
        bx0, by0 = XL[i] + ROAD / 2 + WALK, YL[j] + ROAD / 2 + WALK
        bw, bh = XL[i + 1] - XL[i] - ROAD - 2 * WALK, YL[j + 1] - YL[j] - ROAD - 2 * WALK
        for t in range(max(1, int(bw // 18) + 1)):
            STREET_TREES.append((bx0 + 2 + t * 18 + random.uniform(-2, 2), by0 - 1.4, random.uniform(5.5, 7)))
        for t in range(1, max(2, int(bh // 18) + 1)):
            STREET_TREES.append((bx0 - 1.4, by0 + t * 18 + random.uniform(-2, 2), random.uniform(5.5, 7)))

# Houses: parapet, balconies, a contrasting stair core, entrance canopy.
WHITE = "#F6F3EE"
for o in [o for o in bpy.data.objects if o.name.startswith(("house_", "shop_"))]:
    x0 = o.location.x - o.dimensions.x / 2
    x1 = o.location.x + o.dimensions.x / 2
    y0 = o.location.y - o.dimensions.y / 2
    y1 = o.location.y + o.dimensions.y / 2
    top = o.location.z + o.dimensions.z / 2
    base = o.color[:]
    pc = "#D9CBB6"
    for a in ((x0, y0, x1, y0 + 0.5), (x0, y1 - 0.5, x1, y1), (x0, y0, x0 + 0.5, y1), (x1 - 0.5, y0, x1, y1)):
        obox("parapet", a[0], a[1], top, a[2], a[3], top + 0.7, MAT["object"], pc)
    floors = int((top - 0.6) // 3.0)
    south = o.name.endswith(("_s", "_tower", "_school"))
    if o.name.startswith("shop_") or o.name.endswith("_podium"):
        # shop front: glass band and awning along the south face
        obox("shopglass", x0 + 1, y0 - 0.05, 0.6, x1 - 1, y0, 3.6, MAT["office"])
        obox("awning", x0 + 0.5, y0 - 1.6, 3.7, x1 - 0.5, y0, 4.0, MAT["object"], random.choice(["#E9573F", "#2F8F5B", "#F2B233"]))
    elif south:
        # stair core in white, protruding from the south face
        cx = x0 + 3.4 * random.randint(3, max(3, int((x1 - x0) / 3.4) - 4))
        obox("core", cx, y0 - 0.5, 0.25, cx + 3.4, y0 + 0.1, top + 0.9, MAT["facade"], WHITE if base != srgb(WHITE) else "#EE9E74")
        obox("canopy", cx - 0.4, y0 - 1.8, 3.0, cx + 3.8, y0, 3.25, MAT["object"], "#F6F3EE")
        obox("door", cx + 1.0, y0 - 0.52, 0.25, cx + 2.4, y0 - 0.5, 2.6, MAT["object"], "#7A5238")
        cols = [k for k in range(int((x1 - x0) / 3.4)) if abs(x0 + 3.4 * k - cx) > 4 and k % 2 == 1]
        for n in range(1, floors):
            for k in cols:
                bx = x0 + 3.4 * k
                obox("balcony", bx + 0.3, y0 - 1.1, 0.25 + n * 3.0, bx + 3.1, y0, 0.25 + n * 3.0 + 1.05, MAT["object"], WHITE)
    elif o.name.endswith("_w"):
        cols = [k for k in range(int((y1 - y0) / 3.4)) if k % 3 == 1]
        for n in range(1, floors):
            for k in cols:
                by = y0 + 3.4 * k
                obox("balcony", x0 - 1.1, by + 0.3, 0.25 + n * 3.0, x0, by + 3.1, 0.25 + n * 3.0 + 1.05, MAT["object"], WHITE)

tick('# Roof units')
# Roof units on houses.
MAT_ROOFUNIT = toon("roofunit", flat("#D7DCE2"))
for o in [o for o in bpy.data.objects if o.name.startswith(("house_", "shop_"))]:
    top = o.location.z + o.dimensions.z / 2
    for _ in range(random.choice([1, 2, 2, 3])):
        batch_add(
            "roofunits",
            MAT_ROOFUNIT,
            "cube",
            (o.location.x + random.uniform(-0.3, 0.3) * o.dimensions.x, o.location.y + random.uniform(-0.3, 0.3) * o.dimensions.y, top + 0.6),
            (random.uniform(1.5, 3), random.uniform(1.5, 2.5), 1.2),
        )
batch_flush()

tick('# ---- 4. Road marki')
# ---- 4. Road markings (one mesh, no outlines) ---------------------------------
X0, X1 = XL[COLS[0]] - P, XL[COLS[-1]] + P
Y0, Y1 = YL[ROWS[0]] - P, YL[ROWS[-1]] + P
verts, faces = [], []


def quad(x0, y0, x1, y1, z=0.06):
    k = len(verts)
    verts.extend([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])
    faces.append((k, k + 1, k + 2, k + 3))


def near_cross(v, lines):
    return any(abs(v - L) < ROAD / 2 + 4.5 for L in lines)


DASH, GAP, W = 3.0, 3.5, 0.32
for i in COLS:  # vertical roads: dashed centre line
    y = Y0
    while y < Y1:
        if not near_cross(y + DASH / 2, [YL[j] for j in ROWS]):
            quad(XL[i] - W / 2, y, XL[i] + W / 2, y + DASH)
        y += DASH + GAP
for j in ROWS:
    x = X0
    while x < X1:
        if not near_cross(x + DASH / 2, [XL[i] for i in COLS]):
            quad(x, YL[j] - W / 2, x + DASH, YL[j] + W / 2)
        x += DASH + GAP
# Zebra crossings on every approach to every intersection.
for i in COLS:
    for j in ROWS:
        cx, cy = XL[i], YL[j]
        for sgn in (-1, 1):
            # crossing the vertical road (stripes along y), north/south of the box
            y0 = cy + sgn * (ROAD / 2 + 1.2)
            y1 = y0 + sgn * 3.0
            for k in range(6):
                x = cx - ROAD / 2 + 1.0 + k * 2.1
                quad(x, min(y0, y1), x + 1.1, max(y0, y1))
            x0 = cx + sgn * (ROAD / 2 + 1.2)
            x1 = x0 + sgn * 3.0
            for k in range(6):
                y = cy - ROAD / 2 + 1.0 + k * 2.1
                quad(min(x0, x1), y, max(x0, x1), y + 1.1)
mesh = bpy.data.meshes.new("markings")
mesh.from_pydata(verts, [], faces)
mk = bpy.data.objects.new("markings", mesh)
LINES_OFF.objects.link(mk)
set_mat(mk, MAT["mark"])

tick('# Yard driveway')
# Yard driveway through the sidewalk.
yard = bpy.data.objects["yard"]
yx0 = yard.location.x - yard.dimensions.x / 2
yx1 = yard.location.x + yard.dimensions.x / 2
cube("driveway", ((yx0 + yx1) / 2 + 2, ROAD / 2 + WALK / 2, 0.27), (yx1 - yx0 - 8, WALK + 0.1, 0.06), MAT["yard"])

tick('# ---- 5. Trees')
# ---- 5. Trees and lamps -------------------------------------------------------
crown_mats = [toon(f"crown{k}", flat(c), ramp=(0.66, 0.84, 1.0)) for k, c in enumerate(CROWNS)]


def make_tree(x, y, h):
    batch_add("trunks", MAT["trunk"], "cyl", (x, y, 0.3 + h * 0.25), (0.28, 0.28, h * 0.5))
    k = random.randrange(len(crown_mats))
    for dx, dy, dz, r in ((0, 0, 0.62, 0.30), (0.18, -0.1, 0.48, 0.22), (-0.16, 0.12, 0.5, 0.21)):
        batch_add(f"crowns{k}", crown_mats[k], "ico", (x + dx * h, y + dy * h, 0.3 + h * dz), (h * r, h * r, h * r * 1.15), smooth_faces=True)


for x, y, h in KEPT_TREES + STREET_TREES:
    make_tree(x, y, h)
batch_flush()

tick('lamp_mat = toon')
lamp_mat = toon("lamp", flat("#5A6676"))
for i in COLS:
    for j in ROWS:
        for sx, sy in ((1, 1), (-1, -1)):
            x = XL[i] + sx * (ROAD / 2 + 1.2)
            y = YL[j] + sy * (ROAD / 2 + 9)
            batch_add("lampposts", lamp_mat, "cyl", (x, y, 3.0), (0.12, 0.12, 5.5), seg=6)
            batch_add("lampposts", lamp_mat, "cube", (x - sx * 0.7, y, 5.7), (1.6, 0.4, 0.25))
batch_flush()

tick('# ---- 6. Warehouse')
# ---- 6. Warehouse details -----------------------------------------------------
wh = bpy.data.objects["warehouse"]
wf = wh.location.y - wh.dimensions.y / 2
wx0 = wh.location.x - wh.dimensions.x / 2
wx1 = wh.location.x + wh.dimensions.x / 2
top = wh.location.z + wh.dimensions.z / 2
# Dock front like the game's warehouse (scene 3 / results): cream wall, blue
# pilasters, each gate in a thick blue portal with a lamp, yellow bollards.
for k in range(3):
    d = bpy.data.objects[f"dock_door_{k}"]
    dx0 = d.location.x - d.dimensions.x / 2
    dx1 = d.location.x + d.dimensions.x / 2
    obox("portal", dx0 - 0.7, wf - 0.7, 0.9, dx0, wf, 6.8, MAT["brand"])
    obox("portal", dx1, wf - 0.7, 0.9, dx1 + 0.7, wf, 6.8, MAT["brand"])
    obox("portal", dx0 - 0.7, wf - 0.7, 6.0, dx1 + 0.7, wf, 6.8, MAT["brand"])
    obox("seal", dx0 + 0.1, wf - 0.5, 1.0, dx1 - 0.1, wf - 0.45, 1.25, MAT["object"], "#2A2F38")
    obox("lamp", d.location.x - 0.5, wf - 1.0, 6.5, d.location.x + 0.5, wf - 0.4, 6.8, MAT["object"], "#2A2F38")
    obox("leveler", dx0, wf - 2.2, 0.32, dx1, wf - 0.7, 0.45, MAT["object"], "#AEB6C0")
    for bx in (dx0 - 1.3, dx1 + 1.3):
        batch_add("bollards", toon("bollard", flat("#F2C230")), "cyl", (bx, wf - 1.2, 0.9), (0.25, 0.25, 1.3), seg=10)
batch_flush()
for k in range(4):
    cube("skylight", (wx0 + 6 + k * (wx1 - wx0 - 12) / 3, wh.location.y + 2, top + 0.25), (4, 9, 0.4), MAT["object"], color="#BFD6EE")
# sign frame posts (the board itself is a blockout object; the word is a game overlay)
sg = bpy.data.objects["warehouse_sign"]
obox("signedge", sg.location.x - 10.3, wf + 0.1, WH_H + 0.3, sg.location.x + 10.3, wf + 0.9, WH_H + 0.6, MAT["brand"])
obox("signedge", sg.location.x - 10.3, wf + 0.1, WH_H + 4.3, sg.location.x + 10.3, wf + 0.9, WH_H + 4.6, MAT["brand"])

of = bpy.data.objects["office"]
ot = of.location.z + of.dimensions.z / 2
cube("officecap", (of.location.x, of.location.y, ot + 0.3), (of.dimensions.x + 0.6, of.dimensions.y + 0.6, 0.6), MAT["object"], color="#F4F7FA")
cube("officeentry", (of.location.x - 2, of.location.y - of.dimensions.y / 2 - 1.0, 3.2), (5, 2, 0.3), MAT["brand"])


# ---- 7. Truck model -------------------------------------------------------------
def paint(name, hexcol, rust=0.0, gloss=0.0, ramp=(0.66, 0.85, 1.0)):
    """Truck paint: soft toon ramp, per-panel top-light gradient (painterly),
    optional rust/fade patches (old rigs) and a soft top highlight (new rigs)."""
    def build(nt):
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = srgb(hexcol)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        # darker at the bottom of each panel, lighter at the top
        grad = math_node(nt, "ADD", math_node(nt, "MULTIPLY", sep.outputs[2], 0.2), 0.86)
        c = nt.nodes.new("ShaderNodeMix")
        c.data_type = "RGBA"
        c.blend_type = "MULTIPLY"
        c.inputs[0].default_value = 1.0
        nt.links.new(rgb.outputs[0], c.inputs[6])
        g3 = nt.nodes.new("ShaderNodeCombineXYZ")
        for k in range(3):
            nt.links.new(grad, g3.inputs[k])
        nt.links.new(g3.outputs[0], c.inputs[7])
        out = c.outputs[2]
        if rust:
            nz = nt.nodes.new("ShaderNodeTexNoise")
            nz.inputs["Scale"].default_value = 0.9
            nz.inputs["Detail"].default_value = 4.0
            nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
            mask = math_node(nt, "GREATER_THAN", nz.outputs["Fac"], 0.7 - 0.04 * rust)
            m2 = nt.nodes.new("ShaderNodeMix")
            m2.data_type = "RGBA"
            nt.links.new(mask, m2.inputs[0])
            nt.links.new(out, m2.inputs[6])
            m2.inputs[7].default_value = srgb("#9A5A36")
            out = m2.outputs[2]
            fade = math_node(nt, "GREATER_THAN", nz.outputs["Fac"], 0.56)
            m3 = nt.nodes.new("ShaderNodeMix")
            m3.data_type = "RGBA"
            nt.links.new(math_node(nt, "MULTIPLY", fade, 0.25), m3.inputs[0])
            nt.links.new(out, m3.inputs[6])
            m3.inputs[7].default_value = srgb("#D9CDB8")
            out = m3.outputs[2]
        if gloss:
            geo = nt.nodes.new("ShaderNodeNewGeometry")
            nrm = nt.nodes.new("ShaderNodeSeparateXYZ")
            nt.links.new(geo.outputs["Normal"], nrm.inputs[0])
            # a thin soft highlight band near the top of side panels
            hi = math_node(nt, "MULTIPLY", math_node(nt, "MULTIPLY", math_node(nt, "GREATER_THAN", sep.outputs[2], 0.78), math_node(nt, "LESS_THAN", sep.outputs[2], 0.9)), gloss)
            hi = math_node(nt, "MULTIPLY", hi, math_node(nt, "LESS_THAN", nrm.outputs[2], 0.5))
            m4 = nt.nodes.new("ShaderNodeMix")
            m4.data_type = "RGBA"
            m4.blend_type = "SCREEN"
            nt.links.new(hi, m4.inputs[0])
            nt.links.new(out, m4.inputs[6])
            m4.inputs[7].default_value = (0.6, 0.6, 0.6, 1)
            out = m4.outputs[2]
        return out
    return toon(name, build, ramp=ramp)


def rcube(name, loc, size, mat, parent, bev=0.0, seg=3, color=None):
    o = cube(name, loc, size, mat, parent=parent, bev=bev, color=color)
    if bev:
        o.modifiers["bevel"].segments = seg
        smooth(o)
    return o


def cyl(name, loc, r, depth, mat, parent, axis="Y", verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if axis == "Y":
        o.rotation_euler = (math.pi / 2, 0, 0)
    elif axis == "X":
        o.rotation_euler = (0, math.pi / 2, 0)
    set_mat(o, mat)
    smooth(o)
    o.parent = parent
    return o


def make_truck(name, cab, trailer="#EEF1F5", frame="#2459B8", old=False, spoiler=False, rust=0.0, stripe=None, reefer=False, beacon=False):
    """Modern European cab-over rigs drawn like the game's result illustrations:
    tall rounded cab with a roof fairing, big black grille, wide windscreen with
    a sun visor, large mirrors, chrome tanks and side skirts, and a curtain-side
    (or reefer) trailer with coloured rails and posts on three axles. Built
    along +X, origin at the middle of the rig on the road."""
    root = bpy.data.objects.new(name, None)
    scene.collection.objects.link(root)
    L = TRUCK_REAL[0]
    front = L / 2
    cab_m = paint(f"{name}_cab", cab, rust=rust, gloss=0.35)
    trl_m = paint(f"{name}_trl", trailer, ramp=(0.76, 0.9, 1.0))
    frm_m = paint(f"{name}_frm", frame)
    black = paint(f"{name}_black", "#2B3038")
    grey = paint(f"{name}_grey", "#5B6470")
    tyre = paint(f"{name}_tyre", "#272B32", ramp=(0.8, 0.9, 1.0))
    glass = paint(f"{name}_glass", "#3C6A96", gloss=0.7, ramp=(0.85, 0.95, 1.0))
    chrome = paint(f"{name}_chrome", "#D3D9E0", gloss=0.6)
    rim = paint(f"{name}_rim", "#DCE1E6")
    lamp = toon(f"{name}_lamp", flat("#FFF8DA"), ramp=(1, 1, 1))
    red = toon(f"{name}_tail", flat("#E0452E"), ramp=(1, 1, 1))
    amber = toon(f"{name}_amber", flat("#FFA11C"), ramp=(1, 1, 1))
    W = 2.5
    # ---------------------------------------------------------------- trailer
    tl = 11.6
    cab_d = 2.35
    tx = front - cab_d - 0.55 - tl / 2
    t0 = tx - tl / 2
    H0, H1 = 1.25, 4.05  # trailer box bottom/top
    hz = (H0 + H1) / 2
    rcube("trailer", (tx, 0, hz), (tl, W + 0.05, H1 - H0), trl_m, root, bev=0.12, seg=3)
    if reefer:
        for k in range(1, 9):
            cube("panel", (t0 + k * tl / 9, 0, hz - 0.05), (0.05, W + 0.07, H1 - H0 - 0.3), paint(f"{name}_seam", "#C6CDD6"), parent=root)
        rcube("reefer", (tx + tl / 2 + 0.25, 0, H1 - 0.75), (0.5, 2.1, 1.3), paint(f"{name}_reefer", "#E4E8EE"), root, bev=0.12)
        for k in range(4):
            cube("reefer_grill", (tx + tl / 2 + 0.51, 0, H1 - 1.15 + k * 0.22), (0.03, 1.6, 0.08), black, parent=root)
        cube("trailer_rail", (tx, 0, H0 + 0.05), (tl, W + 0.08, 0.16), grey, parent=root)
    else:
        # curtain side: top and bottom rails, corner posts and tension straps
        for sy in (-1, 1):
            yy = sy * (W / 2 + 0.03)
            cube("rail_top", (tx, yy, H1 - 0.16), (tl + 0.04, 0.08, 0.24), frm_m, parent=root)
            cube("rail_bot", (tx, yy, H0 + 0.1), (tl + 0.04, 0.08, 0.22), frm_m, parent=root)
            for xx in (t0 + 0.08, t0 + tl - 0.08):
                cube("corner", (xx, yy, hz - 0.02), (0.16, 0.09, H1 - H0 - 0.04), frm_m, parent=root)
        for k in range(1, 15):
            cube("strap", (t0 + k * tl / 15, 0, H0 + 0.36), (0.06, W + 0.1, 0.32), frm_m, parent=root)
        for k in range(1, 4):
            cube("post", (t0 + k * tl / 4, 0, hz), (0.07, W + 0.085, H1 - H0 - 0.5), paint(f"{name}_crease", "#C9C2B4" if trailer.upper() > "#E" else "#B9C3CF"), parent=root)
    if stripe:
        cube("stripe", (tx, 0, H0 + 0.62), (tl - 0.6, W + 0.08, 0.28), paint(f"{name}_stripe", stripe), parent=root)
    # chassis, side underrun guards, landing legs, rear lights
    cube("trl_chassis", (tx, 0, H0 - 0.2), (tl - 0.4, 1.1, 0.3), black, parent=root)
    for sy in (-1, 1):
        cube("guard", (t0 + tl * 0.56, sy * 1.18, 0.75), (tl * 0.42, 0.06, 0.1), chrome, parent=root)
        cube("guard2", (t0 + tl * 0.56, sy * 1.18, 0.98), (tl * 0.42, 0.06, 0.1), chrome, parent=root)
        cube("leg", (t0 + tl - 2.3, sy * 0.8, 0.65), (0.14, 0.14, 1.0), grey, parent=root)
        cube("taillight", (t0 - 0.02, sy * 1.0, 0.95), (0.06, 0.38, 0.16), red, parent=root)
        cube("mudflap", (t0 + 0.35, sy * 1.1, 0.55), (0.05, 0.42, 0.55), black, parent=root)
        for k in range(5):
            cube("marker", (t0 + 0.8 + k * (tl - 1.6) / 4, sy * (W / 2 + 0.05), H0 + 0.02), (0.16, 0.03, 0.09), amber, parent=root)
    cube("rear_bumper", (t0 + 0.1, 0, 0.62), (0.16, W - 0.2, 0.16), grey, parent=root)
    trailer_objs = set(root.children)
    # ---------------------------------------------------------------- tractor
    cx = front - cab_d / 2
    cube("tractor_chassis", (front - 3.2, 0, 0.8), (6.2, 1.05, 0.34), black, parent=root)
    # cab body (floor at 1.05, roof at 3.45) and the high roof fairing
    rcube("cab", (cx, 0, 2.35), (cab_d, W, 2.6), cab_m, root, bev=0.34, seg=4)
    # high roof fairing reaching the trailer roof line
    rcube("roof", (cx - 0.12, 0, 3.92), (cab_d - 0.24, W - 0.1, 0.62), cab_m, root, bev=0.3, seg=4)
    rcube("roof_hatch", (cx - 0.2, 0, 4.24), (0.5, 0.6, 0.06), grey, root, bev=0.02)
    # black grille block with horizontal slats and a badge bar
    rcube("grille", (front - 0.02, 0, 1.75), (0.1, 1.75, 1.05), black, root, bev=0.05)
    for k in range(5):
        cube("slat", (front + 0.04, 0, 1.35 + k * 0.2), (0.03, 1.6, 0.06), grey, parent=root)
    cube("badge", (front + 0.05, 0, 2.38), (0.03, 1.2, 0.08), chrome, parent=root)
    # windscreen with black frame, sun visor, wipers
    cube("ws_frame", (front - 0.01, 0, 3.0), (0.05, 2.3, 1.08), black, parent=root)
    cube("windshield", (front + 0.02, 0, 3.0), (0.04, 2.12, 0.92), glass, parent=root)
    rcube("visor", (front + 0.05, 0, 3.6), (0.3, 2.42, 0.18), black, root, bev=0.05)
    for sy in (-0.45, 0.45):
        cube("wiper", (front + 0.05, sy, 2.6), (0.02, 0.75, 0.04), black, parent=root)
    # bumper with headlights, fog lights and a plate
    rcube("bumper", (front - 0.02, 0, 0.92), (0.3, W + 0.02, 0.5), black if not spoiler else grey, root, bev=0.1)
    cube("plate", (front + 0.14, 0, 0.92), (0.02, 0.55, 0.13), paint(f"{name}_plate", "#F4F4F0"), parent=root)
    for sy in (-1, 1):
        rcube("headlight", (front + 0.0, sy * 0.98, 1.38), (0.1, 0.42, 0.24), lamp, root, bev=0.04)
        cube("fog", (front + 0.13, sy * 0.95, 0.92), (0.03, 0.2, 0.1), lamp, parent=root)
        cube("indicator", (front + 0.0, sy * 1.16, 1.38), (0.08, 0.1, 0.18), amber, parent=root)
        # side: door with window, step, big mirror on an arm
        cube("door_line", (cx + 0.1, sy * (W / 2 + 0.01), 2.1), (1.25, 0.02, 1.9), paint(f"{name}_seamc", "#1F2B3C"), parent=root)
        cube("door", (cx + 0.1, sy * (W / 2 + 0.02), 2.1), (1.17, 0.02, 1.82), cab_m, parent=root)
        cube("sidewin", (cx + 0.3, sy * (W / 2 + 0.035), 2.95), (0.85, 0.02, 0.78), glass, parent=root)
        cube("step", (cx + 0.15, sy * (W / 2 - 0.08), 0.95), (0.9, 0.18, 0.2), black, parent=root)
        cube("mirror_arm", (front + 0.05, sy * (W / 2 + 0.12), 3.1), (0.06, 0.28, 0.05), black, parent=root)
        rcube("mirror", (front + 0.08, sy * (W / 2 + 0.28), 2.75), (0.14, 0.14, 0.75), black, root, bev=0.04)
        # chrome fuel tank and side skirt behind the cab
        cyl("tank", (cx - cab_d / 2 - 0.75, sy * 0.98, 0.95), 0.36, 1.25, chrome, root, axis="X")
        rcube("skirt", (cx - cab_d / 2 - 1.95, sy * 1.12, 0.95), (1.0, 0.12, 0.5), cab_m if spoiler else grey, root, bev=0.05)
    cube("antenna", (cx - 0.3, 0.9, 4.5), (0.03, 0.03, 0.7), black, parent=root)
    if beacon:
        rcube("beacon", (cx + 0.35, 0, 4.32), (0.26, 0.26, 0.2), amber, root, bev=0.05)
    if spoiler:
        for sy in (-0.6, 0, 0.6):
            cube("roof_lamp", (cx + 0.72, sy, 4.25), (0.1, 0.22, 0.09), amber, parent=root)
    # exhaust stack behind the cab (smoke anchor)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.14, depth=1.9, location=(cx - cab_d / 2 - 0.15, 1.05, 3.3))
    st = bpy.context.object
    set_mat(st, chrome)
    smooth(st)
    st.parent = root
    root["exhaust"] = (cx - cab_d / 2 - 0.15, 1.05, 4.3)
    tractor_objs = set(root.children) - trailer_objs
    # ---------------------------------------------------------------- wheels
    axles = [front - 1.2, front - 4.6, t0 + 1.2, t0 + 2.55, t0 + 3.9]
    pre_wheels = set(root.children)
    part_of_axle = {}
    for k, ax in enumerate(axles):
        part = "cab" if k == 0 else "chassis" if k == 1 else "trailer"
        for sy in (-1, 1):
            w = cyl("tyre", (ax, sy * 1.02, 0.52), 0.52, 0.5, tyre, root)
            bevel(w, 0.1, 3)
            for o in (w, cyl("rim", (ax, sy * 1.275, 0.52), 0.3, 0.03, rim, root),
                      cyl("hub", (ax, sy * 1.29, 0.52), 0.11, 0.03, grey, root, verts=10)):
                o["part"] = part
    # wheel arches on the tractor
    for k, ax in enumerate(axles[:2]):
        for sy in (-1, 1):
            rcube("arch", (ax, sy * 1.12, 1.12), (1.3, 0.3, 0.14), black, root, bev=0.05)["part"] = "cab" if k == 0 else "chassis"
    # Articulation: the trailer turns about the kingpin over the tractor's
    # rear axle; parts under the trailer nose form a low "chassis" sprite that
    # is always drawn before the trailer.
    for o in trailer_objs:
        o["part"] = "trailer"
    for o in tractor_objs:
        low = o.name.split(".")[0] in ("tractor_chassis", "skirt", "tank")
        o["part"] = "chassis" if low else "cab"
    root["kingpin"] = front - 4.25
    root.scale = (TRUCK_SCALE,) * 3
    return root


def place(root, pts, s):
    total = g["length"](pts)
    p, ang = g["at"](pts, s % total)
    root.location = (p.x, p.y, 0.06)
    root.rotation_euler = (0, 0, ang)


tick('# ---- 8. Light')
# ---- 8. Light, world, outlines ---------------------------------------------------
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
scene.collection.objects.link(sun)
sun.data.energy = 2.6
sun.data.angle = math.radians(6)
d = Vector((0.55, -0.75, 1.1)).normalized()  # towards the sun (south-east): west faces fall in shade
sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds["w"] if "w" in bpy.data.worlds else bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = srgb("#DCE8F4")
bg.inputs[1].default_value = 0.22
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.view_settings.exposure = 0.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.film_transparent = False
scene.render.use_freestyle = True
scene.render.line_thickness_mode = "ABSOLUTE"
vl = scene.view_layers[0]
vl.use_freestyle = True
fs = vl.freestyle_settings
fs.crease_angle = math.radians(120)
ls = fs.linesets[0] if fs.linesets else fs.linesets.new("lines")
ls.select_by_visibility = True
ls.select_by_edge_types = True
ls.select_silhouette = True
ls.select_border = True
ls.select_crease = True
ls.select_by_collection = True
ls.collection = LINES_OFF
ls.collection_negation = "EXCLUSIVE"
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new("ink")
ls.linestyle.color = srgb(PAL["line"])[:3]
ls.linestyle.alpha = 0.9


def render(name, cam, res, thickness):
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    ls.linestyle.thickness = thickness
    scene.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)


tick('trucks = {')
trucks = {
    "crew": make_truck("truck_crew", "#6CC24A", trailer="#DDE4EC", frame="#2459B8", spoiler=True),
    "near": make_truck("truck_near", "#1F63D6", trailer="#F3F5F8", frame="#1F63D6", reefer=True),
    "old": make_truck("truck_old", "#E8482C", trailer="#EFE5D0", frame="#2459B8", old=True, beacon=True),
    "old4": make_truck("truck_old4", "#F0B323", trailer="#EEE8DC", frame="#5F6B78", old=True, beacon=True),
}
START = {"near": 0.06, "old": 0.55, "old4": 0.35, "crew": 0.93}
for rid, root in trucks.items():
    place(root, ROUTES[rid], START[rid] * g["length"](ROUTES[rid]))
if os.environ.get("NO_TRUCKS"):
    for root in trucks.values():
        for o in [root] + list(root.children_recursive):
            o.hide_render = True

def closeup_cam(focus, scale):
    wide = bpy.data.objects["wide"]
    cam = bpy.data.objects.new("closeup", bpy.data.cameras.new("closeup"))
    scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = scale
    cam.data.clip_end = 4000
    cam.rotation_euler = wide.rotation_euler
    F = Euler(wide.rotation_euler, "XYZ").to_matrix() @ Vector((0, 0, -1))
    cam.location = Vector(focus) - F * 900
    return cam


if MODE in ("trucks", "truckpreview"):
    # the five rigs in a row on an empty ground, wide-plate camera rotation
    trucks["express"] = make_truck("truck_express", "#0057B8", trailer="#F7F9FC", frame="#0057B8", spoiler=True, stripe="#0057B8", reefer=True)
    if MODE == "truckpreview":
        for o in scene.objects:
            if o.type in ("MESH", "CURVE") and not any(o.name in {c.name for c in t.children_recursive} for t in trucks.values()):
                o.hide_render = True
    ang = math.radians(float(os.environ.get("PREVIEW_ANG", 200)))
    for k, rid in enumerate(("old", "old4", "near", "crew", "express")):
        r = trucks[rid]
        r.location = (k * float(os.environ.get("PREVIEW_GAP", 34)), 300, 0.06)
        r.rotation_euler = (0, 0, ang)
    zs = float(os.environ.get("PREVIEW_SCALE", 190))
    render("trucks", closeup_cam((2 * float(os.environ.get("PREVIEW_GAP", 34)), 300, 0), zs), (2400, round(2400 * 190 / 570 * zs / 190 * 1)) if False else (2400, 800), 2.0)
elif MODE == "sprites":
    # Each rig at 16 world headings, seen through each plate camera's rotation
    # (ortho => the look does not depend on position). 2x plate scale.
    import json
    from bpy_extras.object_utils import world_to_camera_view
    trucks["express"] = make_truck("truck_express", "#0057B8", trailer="#F7F9FC", frame="#0057B8", spoiler=True, stripe="#0057B8", reefer=True)
    blk = json.loads((HERE / "out-v5" / "blockout.json").read_text())
    keep = set()
    for root in trucks.values():
        keep.add(root.name)
        keep.update(o.name for o in root.children_recursive)
    for o in scene.objects:
        if o.type in ("MESH", "CURVE", "EMPTY") and o.name not in keep:
            o.hide_render = True
    for root in trucks.values():
        for o in [root] + list(root.children_recursive):
            o.hide_render = False
    scene.render.film_transparent = True
    # No ink outlines on the rigs: they read as hard black boxes on the map.
    scene.render.use_freestyle = os.environ.get("SPRITE_INK_ON") == "1"
    SPR = OUT / "sprites"
    SPR.mkdir(exist_ok=True)
    N = int(os.environ.get("HEADINGS", 32))
    SC = 1.5
    man = {"headings": N, "scale": SC, "plates": {}}
    _f = TRUCK_REAL[0] / 2
    _S = TRUCK_SCALE
    man["rig"] = {k: round(v * _S, 3) for k, v in {
        "front": _f, "frontAxle": _f - 1.2, "rearAxle": _f - 4.6, "kingpin": _f - 4.25,
        "tractorRear": _f - 6.3, "trailerFront": _f - 2.9, "bogie": -3.7, "trailerRear": -6.25,
        "width": 2.6,
    }.items()}
    for pname in ("wide", "tall"):
        pcam = bpy.data.objects[pname]
        mpp = blk["plates"][pname]["metresPerPx"]
        size = int(os.environ.get("SPR_SIZE", 240))  # plate px, square, centred on the kingpin
        res = int(size * SC)
        cam = bpy.data.objects.new(f"spr_{pname}", bpy.data.cameras.new(f"spr_{pname}"))
        scene.collection.objects.link(cam)
        cam.data.type = "ORTHO"
        cam.data.sensor_fit = "HORIZONTAL"
        cam.data.ortho_scale = size * mpp
        cam.data.clip_end = 4000
        cam.rotation_euler = pcam.rotation_euler
        F = Euler(pcam.rotation_euler, "XYZ").to_matrix() @ Vector((0, 0, -1))
        cam.location = Vector((0, 0, 0.4)) - F * 900
        scene.camera = cam
        scene.render.resolution_x = scene.render.resolution_y = res
        bpy.context.view_layer.update()
        pm = {"size": size, "trucks": {}}
        # Articulated rigs: tractor body ("cab"), its low rear frame
        # ("chassis") and the trailer, each rendered about the kingpin so the
        # game can turn the trailer independently. Express stays one piece.
        jobs = [(rid, part) for rid in ("old", "near", "crew", "old4") for part in ("cab", "chassis", "trailer")]
        jobs.append(("express", None))
        for rid, part in jobs:
            root = trucks[rid]
            for other in trucks.values():
                other.location = (5000, 5000, -500)
            for o in root.children_recursive:
                o.hide_render = part is not None and o.get("part", "cab") != part
            kp = root.get("kingpin", 0.0) * TRUCK_SCALE if part else 0.0
            frames = []
            for k in range(N):
                ang = 2 * math.pi * k / N
                root.rotation_euler = (0, 0, ang)
                root.location = (-math.cos(ang) * kp, -math.sin(ang) * kp, 0.06)
                bpy.context.view_layer.update()
                def scr(local):
                    w = root.matrix_world @ Vector(local)
                    v = world_to_camera_view(scene, cam, w)
                    return [round(v.x * size, 2), round((1 - v.y) * size, 2)]
                c0 = scr((0, 0, 0.4 / TRUCK_SCALE))
                fw = scr((4, 0, 0.4 / TRUCK_SCALE))
                dirv = [fw[0] - c0[0], fw[1] - c0[1]]
                ln = math.hypot(*dirv) or 1
                ex = root.get("exhaust")
                front = TRUCK_REAL[0] / 2
                frames.append({
                    "dir": [round(dirv[0] / ln, 4), round(dirv[1] / ln, 4)],
                    "exhaust": scr(tuple(ex)) if ex else c0,
                    "cab": scr((front - 1.2, 0, 4.6)),
                })
                ls.linestyle.thickness = float(os.environ.get("SPRITE_INK", 2.6))
                key = rid if part is None else f"{rid}-{part}"
                scene.render.filepath = str(SPR / f"{pname}-{key}-{k:02d}.png")
                bpy.ops.render.render(write_still=True)
            pm["trucks"][rid if part is None else f"{rid}-{part}"] = frames
            for o in root.children_recursive:
                o.hide_render = False
            root.location = (5000, 5000, -500)
        man["plates"][pname] = pm
    (SPR / "sprites.json").write_text(json.dumps(man, indent=1))
elif MODE == "still":
    # Stage-1 "full render" still: the four rigs at their start positions,
    # seen through the wide plate camera, trucks only on a transparent film
    # (composited over the painted plate), thin ink, small soft puffs (no
    # ink), plus a separate ground-shadow pass from the same sun.
    keep = set()
    for root in trucks.values():
        keep.add(root.name)
        keep.update(o.name for o in root.children_recursive)
    for o in scene.objects:
        if o.type in ("MESH", "CURVE") and o.name not in keep:
            o.hide_render = True
    PF = float(os.environ.get("PUFF", 0.45))
    puffs = []
    if PF > 0:
        puff_m = toon("puff", flat("#F2EFEA"), ramp=(0.8, 0.92, 1.0))
        for rid, root in trucks.items():
            ex = root.get("exhaust")
            if not ex:
                continue
            bpy.context.view_layer.update()
            base = root.matrix_world @ Vector(ex)
            back = root.matrix_world.to_3x3() @ Vector((-1, 0, 0))
            back.normalize()
            for k in range(3):
                r = (0.8 + 0.5 * k) * PF * TRUCK_SCALE
                loc = base + back * (0.8 + 1.6 * k) * TRUCK_SCALE * PF + Vector((0, 0, (0.6 + 0.9 * k) * TRUCK_SCALE * PF))
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r, location=loc)
                pf = bpy.context.object
                pf.name = f"puff_{rid}_{k}"
                set_mat(pf, puff_m)
                smooth(pf)
                to_nolines(pf)
                puffs.append(pf)
    scene.render.film_transparent = True
    th = float(os.environ.get("STILL_INK", 1.1))
    cam = bpy.data.objects["wide"]
    res = tuple(g["PLATES"]["wide"]["res"])
    render("still-wide", cam, res, th)
    # ---- shadow pass: plain white diffuse ground, rigs invisible to camera
    gnd = bpy.data.objects["ground"]
    gm = bpy.data.materials.new("shadowground")
    gm.use_nodes = True
    gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 1, 1, 1)
    gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
    set_mat(gnd, gm)
    gnd.hide_render = False
    scene.render.use_freestyle = False
    scene.render.film_transparent = False
    rigs = [o for root in trucks.values() for o in root.children_recursive if o.type == "MESH"]
    for o in rigs + puffs:
        o.visible_camera = False
    for o in puffs:
        o.visible_shadow = False
    render("still-wide-shA", cam, res, th)
    for o in rigs:
        o.hide_render = True
    render("still-wide-shB", cam, res, th)
elif MODE == "test":
    wide = bpy.data.objects["wide"]
    cam = bpy.data.objects.new("test", bpy.data.cameras.new("test"))
    scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.ortho_scale = 120
    cam.data.clip_end = 4000
    cam.rotation_euler = wide.rotation_euler
    F = Euler(wide.rotation_euler, "XYZ").to_matrix() @ Vector((0, 0, -1))
    focus = Vector((42, 30, 0))
    cam.location = focus - F * 900
    render("style-test" + ("-empty" if os.environ.get("NO_TRUCKS") else ""), cam, (1800, 1000), 2.0)
else:
    suffix = "-empty" if os.environ.get("NO_TRUCKS") else ""
    render(f"plate-{MODE}{suffix}", bpy.data.objects[MODE], tuple(g["PLATES"][MODE]["res"]), 1.6)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / f"style-{MODE}.blend"))
print("STYLE OK", MODE)
