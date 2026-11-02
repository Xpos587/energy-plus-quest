# Scene 3 (warehouse) v1: the Inventory warehouse built as geometry, so racks,
# docks, trucks and people share one camera per format and every outcome is
# the same building, not a repaint of a repaint.
# blender --background --factory-startup --python warehouse.py -- OUTDIR MODE [FORMAT...]
#   MODE: test | plate | outcomes
# Reference: docs/scenario-assets/image7.jpg (isometric warehouse, tall blue/orange
# racks with big banners, dock doors with trucks, "зона отгрузки" signs).
# Layout: both dock doors in the back wall (receiving left, dispatch right) with
# their signs above, six rack rows running towards the docks, alphabet А–Б … Ю–Я
# left to right, keeper by Ю–Я, the «Автоподбор» desk at the back wall. Text is real geometry (Roboto) so it stays
# readable and can be re-composited after a style pass.
import json
import math
import os
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector, Euler

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
OUT = Path(args[0] if args else "out")
MODE = args[1] if len(args) > 1 else "test"
LAYOUT = os.environ.get("LAYOUT", "wide")
FORMATS = args[2:] or ["desk"]
OUT.mkdir(parents=True, exist_ok=True)
random.seed(3)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


# ---- materials: soft three-step toon ramp times the surface colour ----------
NOLINES = bpy.data.collections.new("NoLines")
scene.collection.children.link(NOLINES)


def toon(name, build, ramp=(0.70, 0.86, 1.0)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    sc = nt.nodes.new("ShaderNodeMath")
    sc.operation = "MULTIPLY"
    sc.inputs[1].default_value = 0.4
    cr = nt.nodes.new("ShaderNodeValToRGB")
    e = cr.color_ramp
    e.interpolation = "EASE"
    e.elements[0].position = 0.09
    e.elements[0].color = (ramp[0],) * 3 + (1,)
    e.elements[1].position = 0.5
    e.elements[1].color = (ramp[2],) * 3 + (1,)
    e.elements.new(0.22).color = (ramp[1],) * 3 + (1,)
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs[0].default_value = 1.0
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    nt.links.new(s2r.outputs[0], bw.inputs[0])
    nt.links.new(bw.outputs[0], sc.inputs[0])
    nt.links.new(sc.outputs[0], cr.inputs[0])
    nt.links.new(cr.outputs[0], mul.inputs[6])
    nt.links.new(build(nt), mul.inputs[7])
    nt.links.new(mul.outputs[2], em.inputs[0])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def mnode(nt, op, a, b=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
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
        if isinstance(v, (tuple, int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[2]


def band(nt, x, lo, hi):
    f = mnode(nt, "FRACT", x)
    return mnode(nt, "MULTIPLY", mnode(nt, "GREATER_THAN", f, lo), mnode(nt, "LESS_THAN", f, hi))


def pos(nt):
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    return sep


def object_color(nt):
    return nt.nodes.new("ShaderNodeObjectInfo").outputs["Color"]


def paving(nt):
    p = pos(nt)
    j = mnode(nt, "MAXIMUM", band(nt, mnode(nt, "DIVIDE", p.outputs[0], 6.0), 0.0, 0.035), band(nt, mnode(nt, "DIVIDE", p.outputs[1], 6.0), 0.0, 0.035))
    return mix(nt, mnode(nt, "MULTIPLY", j, 0.55), srgb("#DCD8CF"), srgb("#B9B4AA"))


def water(nt):
    p = pos(nt)
    tc = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(mnode(nt, "MULTIPLY", p.outputs[0], 0.045), tc.inputs[0])
    nt.links.new(mnode(nt, "MULTIPLY", p.outputs[1], 0.16), tc.inputs[1])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 1.0
    nt.links.new(tc.outputs[0], nz.inputs["Vector"])
    ripple = band(nt, mnode(nt, "MULTIPLY", nz.outputs[0], 7.0), 0.0, 0.07)
    # deeper water further from the quay
    depth = mnode(nt, "MINIMUM", mnode(nt, "DIVIDE", mnode(nt, "ABSOLUTE", p.outputs[1]), 90.0), 1.0)
    base = mix(nt, depth, srgb("#6DB6E6"), srgb("#3F8FD2"))
    return mix(nt, mnode(nt, "MULTIPLY", ripple, 0.75), base, srgb("#B9E0F7"))


def glass(nt):
    p = pos(nt)
    refl = band(nt, mnode(nt, "DIVIDE", mnode(nt, "ADD", p.outputs[0], p.outputs[2]), 5.0), 0.1, 0.32)
    return mix(nt, mnode(nt, "MULTIPLY", refl, 0.6), srgb("#4F86BE"), srgb("#CFE6F8"))


MAT = {
    "obj": toon("obj", object_color),
    "paving": toon("paving", paving, ramp=(0.78, 0.9, 1.0)),
    "water": toon("water", water, ramp=(0.92, 0.97, 1.0)),
    "glass": toon("glass", glass, ramp=(0.9, 0.95, 1.0)),
    "flat": toon("flat", object_color, ramp=(0.96, 0.98, 1.0)),
}

# ---- geometry helpers: one bmesh per (group, colour, material) --------------
BATCH = {}
GROUPS = {}


def _bm(group, color, mat, nolines):
    key = (group, color, mat, nolines)
    if key not in BATCH:
        BATCH[key] = bmesh.new()
    return BATCH[key]


def box(group, color, c, size, rot=0.0, mat="obj", M=None, nolines=False):
    T = Matrix.Translation(c) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Diagonal((*size, 1))
    bmesh.ops.create_cube(_bm(group, color, mat, nolines), size=1.0, matrix=(M @ T) if M else T)


def aabb(group, color, x0, y0, z0, x1, y1, z1, **kw):
    box(group, color, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), **kw)


def cyl(group, color, c, r, h, axis="Z", seg=24, r2=None, mat="obj", M=None, nolines=False):
    R = {"Z": Matrix(), "X": Matrix.Rotation(math.pi / 2, 4, "Y"), "Y": Matrix.Rotation(math.pi / 2, 4, "X")}[axis]
    T = Matrix.Translation(c) @ R @ Matrix.Diagonal((1, 1, h, 1))
    bmesh.ops.create_cone(_bm(group, color, mat, nolines), cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=1.0, matrix=(M @ T) if M else T)


def ball(group, color, c, r, sx=1, sy=1, sz=1, mat="obj", M=None, nolines=False, sub=2):
    T = Matrix.Translation(c) @ Matrix.Diagonal((r * sx, r * sy, r * sz, 1))
    res = bmesh.ops.create_icosphere(_bm(group, color, mat, nolines), subdivisions=sub, radius=1.0, matrix=(M @ T) if M else T)
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.smooth = True


def beam(group, color, p0, p1, w, h=None, M=None, nolines=False):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    q = d.to_track_quat("X", "Z")
    T = Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((d.length, w, h or w, 1))
    bmesh.ops.create_cube(_bm(group, color, "obj", nolines), size=1.0, matrix=(M @ T) if M else T)


def flush():
    for (group, color, mat, nolines), bm in BATCH.items():
        me = bpy.data.meshes.new(f"{group}|{color}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(MAT[mat])
        o = bpy.data.objects.new(f"{group}|{color}|{mat}", me)
        (NOLINES if nolines else scene.collection).objects.link(o)
        o.color = srgb(color)
        o["group"] = group
        GROUPS.setdefault(group, []).append(o)
    BATCH.clear()




# ---- extra surfaces -------------------------------------------------------------
def floor_tiles(nt):
    p = pos(nt)
    j = mnode(nt, "MAXIMUM", band(nt, mnode(nt, "DIVIDE", p.outputs[0], 4.0), 0.0, 0.02), band(nt, mnode(nt, "DIVIDE", p.outputs[1], 4.0), 0.0, 0.02))
    return mix(nt, mnode(nt, "MULTIPLY", j, 0.45), srgb("#D6DEE7"), srgb("#AEB9C6"))


def asphalt(nt):
    return srgb("#9AA4B1")


MAT["floor"] = toon("floor", floor_tiles, ramp=(0.8, 0.9, 1.0))
MAT["asphalt"] = toon("asphalt", lambda nt: object_color(nt), ramp=(0.86, 0.94, 1.0))

FONT = bpy.data.fonts.load("/usr/share/fonts/TTF/Roboto-Black.ttf")
TEXTS = []


def text(group, s, c, size, color, rot=(math.pi / 2, 0, 0), align="CENTER"):
    """Real text geometry facing -y by default (readable from the camera side)."""
    cu = bpy.data.curves.new(f"t{len(TEXTS)}", "FONT")
    cu.body = s
    cu.font = FONT
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.extrude = 0.01
    o = bpy.data.objects.new(f"{group}|text|{s}", cu)
    NOLINES.objects.link(o)
    o.location = c
    o.rotation_euler = rot
    o.data.materials.append(MAT["flat"])
    o.color = srgb(color)
    o["group"] = group
    GROUPS.setdefault(group, []).append(o)
    TEXTS.append(o)
    return o


# ---- layout (metres): x left->right, y from the cut front edge to the dock wall, z up --
FZ = 1.2  # dock-height floor
# v16 = the pre-3D illustration's plan (public/scene-art/inventory-master-labels-v6.webp)
# built as real geometry: receiving doors in the LEFT wall, dispatch doors in the RIGHT
# wall (mirror images), windows in the back wall, open front. Three back-to-back rack
# pairs run from the front towards the back wall; their front-end plaques read left to
# right А–Б … Ю–Я. Forklift in front of the racks, pallets front-left, the «Автоподбор»
# desk front-right, keeper Pavel by dispatch. The camera is centred (azimuth 0), so the
# two side walls are true mirror images.
LAYOUTS = {
    "wide": dict(X1=42.0, Y1=28.0, DOORS_Y=(12.5, 19.5), RY=(4.5, 21.5), RW=2.6, PAIRS=(12.5, 21.0, 29.5), PT=0.95,
                 ENTR=(0.6, 7.0), DESK=(34.2, 37.6), DESK_Y=(1.0, 2.25), GIFT=(4.2, 12.5), JACK_DX=1.8, SCAN_IN=(3.0, 16.4),
                 BARGE=[(37.4, 11.0), (37.4, 12.8), (39.2, 11.0), (39.2, 12.8)],
                 SCAN_OUT=(35.6, 12.4), KEEPER=(37.4, 6.4), LANE=3.5, FORK=(16.75, 2.6),
                 RUN_E=((24.0, 2.8), (6.0, 24.6)), PUZZLED=((34.5, 4.0), (37.0, 5.5))),
    # v17 phone plate: the same hall plan, narrower and deeper, so it fills a portrait frame
    "tall": dict(X1=32.0, Y1=36.0, DOORS_Y=(14.5, 21.5), RY=(10.5, 28.5), RW=2.2, PAIRS=(9.5, 16.0, 22.5), PT=0.8,
                 ENTR=(2.0, 9.0), DESK=(24.4, 27.8), DESK_Y=(1.0, 2.25), GIFT=(3.6, 14.5), JACK_DX=1.4, SCAN_IN=(3.0, 18.4),
                 BARGE=[(27.4, 13.0), (27.4, 14.8), (29.2, 13.0), (29.2, 14.8)],
                 SCAN_OUT=(25.8, 14.4), KEEPER=(27.6, 7.4), LANE=5.5, FORK=(16.0, 3.4),
                 RUN_E=((18.0, 4.8), (5.0, 30.0)), PUZZLED=((25.0, 6.0), (27.5, 7.5))),
}
P = LAYOUTS[LAYOUT]
X0, Y0 = 0.0, 0.0
X1, Y1 = P["X1"], P["Y1"]
WALL = FZ + 10.6
PEOPLE = 1.6  # v16: a person reads ~0.45 of a rack, as in the v6 illustration
DOORS_Y = P["DOORS_Y"]  # door centres along y, same on both side walls
DX_OUT = X1 - 1.4  # walking line along the dispatch wall
DOOR = 2.6  # half width of the dock doors
DOOR_Z = FZ + 6.4
BLUE, NAVY, ORANGE, YELLOW = "#2A5FA8", "#1E3E6E", "#FF6A13", "#FFC20E"
KRAFT, WHITE = "#D9A866", "#EEF1F4"
LANE = P["LANE"]  # the open cross aisle in front of the docks (not painted)

def tree(x, y, h):
    cyl("trees", "#F3EFE6", (x, y, h * 0.3), 0.3, h * 0.6, seg=8)
    col = random.choice(["#F2C230", "#F0A32A", "#E8892B", "#9BC255", "#F5D046", "#7FB04A"])
    for dx, dy, dz, r in ((0, 0, 0.7, 0.30), (0.2, -0.1, 0.55, 0.22), (-0.18, 0.12, 0.57, 0.21)):
        ball("trees", col, (x + dx * h, y + dy * h, h * dz), h * r, sz=1.15)


# ---- site: the warehouse stands on a real logistics lot, not an island of asphalt.
# A road with a guarded gate, a fenced truck yard with a parked trailer row and
# containers, staff car park, a neighbour warehouse, lamp posts and tree lines.
# Everything outside the hall is muted so the hall stays the subject.
GRASS, ASPH, ASPH_D, KERB, LINE = "#B4D27E", "#A3ACB8", "#939DAA", "#E4E7EB", "#F4F5F7"
aabb("ground", GRASS, -160, -160, -0.3, 240, 220, -0.05, mat="flat", nolines=True)
SX0, SX1, SY0, SY1 = -26.0, X1 + 34.0, -10.0, Y1 + 28.0  # the fenced lot
aabb("ground", ASPH, SX0, SY0, -0.1, SX1, SY1, 0.0, mat="asphalt", nolines=True)
# public road along the front, centre dashes, kerbs, pavement and a tree line
RY_0, RY_1 = SY0 - 13.0, SY0 - 4.0
aabb("ground", ASPH_D, -160, RY_0, -0.1, 240, RY_1, 0.0, mat="asphalt", nolines=True)
for x in range(-160, 240, 6):
    aabb("ground", LINE, x, (RY_0 + RY_1) / 2 - 0.1, 0.0, x + 3, (RY_0 + RY_1) / 2 + 0.1, 0.02, nolines=True)
for y0, y1 in ((RY_1, RY_1 + 0.4), (RY_0 - 0.4, RY_0)):
    aabb("ground", KERB, -160, y0, 0.0, 240, y1, 0.12, nolines=True)
aabb("ground", "#D9D4CA", -160, RY_1 + 0.4, 0.0, 240, SY0 - 0.3, 0.05, nolines=True)
aabb("ground", "#D9D4CA", -160, RY_0 - 3.0, 0.0, 240, RY_0 - 0.4, 0.05, nolines=True)
# perimeter fence with a gate opening on the left, guard booth and a barrier arm
GX0, GX1 = SX0 + 3.0, SX0 + 13.0
aabb("ground", ASPH, GX0, RY_1, -0.1, GX1, SY0, 0.01, mat="asphalt", nolines=True)


def fence(x0, y0, x1, y1):
    n = max(1, round(math.hypot(x1 - x0, y1 - y0) / 3.0))
    for k in range(n + 1):
        x, y = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
        aabb("site", "#7D8894", x - 0.06, y - 0.06, 0, x + 0.06, y + 0.06, 2.0)
    for z in (0.15, 1.9):
        beam("site", "#9BA5B0", (x0, y0, z), (x1, y1, z), 0.05)
    beam("site", "#C3CAD2", (x0, y0, 1.05), (x1, y1, 1.05), 0.02, 1.7, nolines=True)


fence(SX0, SY0, GX0, SY0)
fence(GX1, SY0, SX1, SY0)
fence(SX0, SY0, SX0, SY1)
fence(SX1, SY0, SX1, SY1)
fence(SX0, SY1, SX1, SY1)
BX, BY = GX1 + 0.6, SY0 + 0.6
aabb("site", "#F1E9D8", BX, BY, 0, BX + 2.6, BY + 2.6, 2.6)
aabb("site", "#7FB3E0", BX - 0.02, BY + 0.5, 1.2, BX + 2.62, BY + 2.1, 2.2, mat="glass")
aabb("site", BLUE, BX - 0.2, BY - 0.2, 2.6, BX + 2.8, BY + 2.8, 2.9)
aabb("site", "#E5E8EC", GX1 - 0.3, SY0 - 0.3, 0, GX1 + 0.3, SY0 + 0.3, 1.1)
for k in range(8):
    aabb("site", "#E23B32" if k % 2 == 0 else "#FFFFFF", GX1 - 0.3 - (k + 1) * 1.1, SY0 - 0.08, 0.95, GX1 - 0.3 - k * 1.1, SY0 + 0.08, 1.12, nolines=True)
# staff car park right of the hall: painted bays, a few parked cars
PX0, PX1 = X1 + 20.0, SX1 - 1.0
for k in range(int((Y1 - 4.0) / 3.0) + 1):
    y = 1.0 + k * 3.0
    aabb("ground", LINE, PX0, y - 0.07, 0.0, PX0 + 5.2, y + 0.07, 0.02, nolines=True)
    aabb("ground", LINE, PX1 - 5.2, y - 0.07, 0.0, PX1, y + 0.07, 0.02, nolines=True)
CAR_COLS = ["#E9EDF1", "#C9D0D8", "#5A8CC4", "#E9EDF1", "#3A414B", "#D9534F", "#E9EDF1"]


def car(x, y, rot, col):
    M = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rot, 4, "Z")
    aabb("site", col, -2.1, -0.9, 0.35, 2.1, 0.9, 1.05, M=M)
    aabb("site", col, -1.1, -0.82, 1.05, 1.2, 0.82, 1.6, M=M)
    aabb("site", "#5A8CC4", -1.0, -0.84, 1.1, 1.1, 0.84, 1.5, mat="glass", M=M)
    for dx in (-1.35, 1.35):
        cyl("site", "#2B2F36", (dx, 0, 0.35), 0.35, 1.84, axis="Y", seg=12, M=M)


rc = random.Random(5)
for k in range(int((Y1 - 4.0) / 3.0)):
    y = 2.5 + k * 3.0
    if rc.random() < 0.6:
        car(PX0 + 2.6, y, 0.0, rc.choice(CAR_COLS))
    if rc.random() < 0.5:
        car(PX1 - 2.6, y, math.pi, rc.choice(CAR_COLS))
# containers at the far side of the truck yard
for k, col in enumerate(("#3D7DC8", "#E8892B", "#5E9E5A", "#3D7DC8")):
    x = SX1 - 4.5
    aabb("site", col, x - 1.25, Y1 + 6 + k * 3.0, 0, x + 1.25, Y1 + 8.6 + k * 3.0, 2.6)
    if k < 2:
        aabb("site", ("#E8892B", "#3D7DC8")[k], x - 1.25, Y1 + 6 + k * 3.0, 2.6, x + 1.25, Y1 + 8.6 + k * 3.0, 5.2)
# neighbour warehouse beyond the fence (left), plain and muted
NX1 = SX0 - 8.0
aabb("site", "#E6DFCF", NX1 - 40, -6, 0, NX1, Y1 + 10, 9.0)
aabb("site", "#C9D2DC", NX1 - 40.4, -6.4, 9.0, NX1 + 0.4, Y1 + 10.4, 9.6)
for y in range(-2, int(Y1) + 8, 8):
    aabb("site", "#B8C2CD", NX1 - 0.02, y, 0, NX1 + 0.05, y + 4.5, 5.0)
aabb("ground", ASPH_D, NX1, -6, -0.1, SX0 - 0.5, Y1 + 10, 0.0, mat="asphalt", nolines=True)
# lamp posts along the yard and the road
for x in range(int(SX0) + 8, int(SX1), 16):
    for y in (SY0 + 1.0, SY1 - 1.0):
        cyl("site", "#7D8894", (x, y, 3.5), 0.1, 7.0, seg=8)
        aabb("site", "#7D8894", x - 0.1, y - 0.8, 6.9, x + 0.1, y + 0.1, 7.1)
        aabb("site", "#F4F6F8", x - 0.25, y - 1.0, 6.75, x + 0.25, y - 0.5, 6.95)
# green verges with kerbs and trees break the asphalt: in front of the hall (the
# walk from the gate booth), between the hall and the car park, along the left lane


def verge(x0, y0, x1, y1, trees=True):
    aabb("ground", KERB, x0 - 0.25, y0 - 0.25, 0.0, x1 + 0.25, y1 + 0.25, 0.14, nolines=True)
    aabb("ground", GRASS, x0, y0, 0.0, x1, y1, 0.16, mat="flat", nolines=True)
    if not trees:
        return
    n = max(1, int(max(x1 - x0, y1 - y0) / 6.5))
    for k in range(n):
        t = (k + 0.5) / n
        x, y = x0 + (x1 - x0) * t if x1 - x0 > y1 - y0 else (x0 + x1) / 2, y0 + (y1 - y0) * t if y1 - y0 >= x1 - x0 else (y0 + y1) / 2
        tree(x, y, random.uniform(4.5, 5.5)) if k % 2 == 0 else shrub(x, y)


def shrub(x, y):
    for dx, dy, r in ((0, 0, 0.9), (0.8, 0.3, 0.7), (-0.7, -0.2, 0.65)):
        ball("trees", "#7FB04A", (x + dx, y + dy, 0.5), r, sz=0.8)


verge(GX1 + 4.0, SY0 + 0.8, X1 + 2.0, -2.6)
verge(X1 + 17.0, 1.0, PX0 - 1.4, Y1 - 1.0)
verge(SX0 + 0.8, 2.0, SX0 + 5.0, Y1 - 2.0)
aabb("ground", "#D9D4CA", GX1 + 2.6, -2.4, 0.0, X1 + 1.0, -0.6, 0.06, nolines=True)  # pavement along the hall front
# dock yard markings: bay lines beside each door, both sides
for dy in DOORS_Y:
    for y in (dy - 3.4, dy + 3.4):
        for x0, x1 in ((X0 - 16, X0 - 1), (X1 + 1, X1 + 16)):
            aabb("ground", LINE, x0, y - 0.08, 0.0, x1, y + 0.08, 0.02, nolines=True)


for x in range(-150, 240, 9):  # avenue along the far side of the road
    tree(x + random.uniform(-1, 1), RY_0 - 6.5, random.uniform(7, 9))
for y in range(int(SY0) + 4, int(SY1), 10):  # hedge of trees along the right fence
    tree(SX1 + 4 + random.uniform(-1, 1), y, random.uniform(7, 9))
for k in range(400):
    x, y = random.uniform(-150, 230), random.uniform(-150, 210)
    if NX1 - 46 < x < SX1 + 9 and RY_0 - 10 < y < SY1 + 6:
        continue
    tree(x, y, random.uniform(8, 12))

# ---- building shell: slab; back and both side walls full height, front open ---------
aabb("shell", "#C9D2DC", X0 - 0.4, Y0 - 0.4, 0, X1 + 0.4, Y1 + 0.4, FZ - 0.02)
aabb("floor", "#D6DEE7", X0, Y0, FZ - 0.05, X1, Y1, FZ, mat="floor", nolines=True)
CREAM = "#F1E9D8"
DOORS = [(d - DOOR, d + DOOR) for d in DOORS_Y]
# back wall with blue columns every 6 m and a high window in each bay
aabb("shell", CREAM, X0 - 0.4, Y1, FZ, X1 + 0.4, Y1 + 0.4, WALL)
aabb("shell", BLUE, X0, Y1 - 0.05, FZ, X1, Y1, FZ + 0.9)
XP = [X0 + 0.3] + [X0 + k * (X1 - X0) / 7 for k in range(1, 7)] + [X1 - 0.3]
for x in XP:
    aabb("shell", BLUE, x - 0.3, Y1 - 0.35, FZ, x + 0.3, Y1, WALL - 0.5)
WIN = [((p + q) / 2 - 1.7, (p + q) / 2 + 1.7) for p, q in zip(XP, XP[1:])]
for a, b in WIN:
    aabb("shell", "#FFFFFF", a - 0.2, Y1 - 0.12, FZ + 5.0, b + 0.2, Y1 - 0.02, FZ + 8.4)
    aabb("shell", "#7FB3E0", a, Y1 - 0.16, FZ + 5.2, b, Y1 - 0.1, FZ + 8.2, mat="glass")
# the two side walls are mirror images: two dock doors each, the zone sign above them
for s in (-1, 1):  # -1 = left (receiving), +1 = right (dispatch)
    xw = X0 if s < 0 else X1  # inner face
    xo = xw + s * 0.4  # outer face
    lo_, hi_ = min(xw, xo), max(xw, xo)
    ys = [Y0] + [e for d in DOORS for e in d] + [Y1 + 0.4]
    for a, b in zip(ys[::2], ys[1::2]):
        aabb("shell", CREAM, lo_, a, FZ, hi_, b, WALL)
        aabb("shell", BLUE, xw - s * 0.05, a, FZ, xw, b, FZ + 0.9)
    for a, b in DOORS:
        aabb("shell", CREAM, lo_, a, DOOR_Z, hi_, b, WALL)  # header above the door
        aabb("shell", "#B8C2CD", xw - s * 0.5, a - 0.1, DOOR_Z, xw, b + 0.1, DOOR_Z + 0.6)  # door roll housing
        aabb("shell", "#2F6DC0", xw + s * 0.1, a, FZ, xw + s * 0.2, b, DOOR_Z)  # closed roll-up shutter
        for z in range(1, int((DOOR_Z - FZ) / 0.55)):
            aabb("shell", "#5C8FD6", xw + s * 0.07, a + 0.05, FZ + z * 0.55 - 0.04, xw + s * 0.1, b - 0.05, FZ + z * 0.55 + 0.04, nolines=True)
        for y in (a - 0.35, b):
            aabb("shell", "#2E3742", xw - s * 0.3, y, FZ, xw, y + 0.35, DOOR_Z + 0.6)  # door posts
        aabb("shell", "#7E8894", xw - s * 1.4, a + 0.1, FZ - 0.04, xo, b - 0.1, FZ + 0.03)  # dock leveller
        for y in (a + 0.3, b - 0.7):
            aabb("shell", "#2B2F36", xo, y, FZ - 0.9, xo + s * 0.35, y + 0.4, FZ - 0.2)  # bumpers outside
    for y in (Y0 + 0.3, 7.0, DOORS[0][0] - 0.7, (DOORS[0][1] + DOORS[1][0]) / 2, DOORS[1][1] + 0.7, Y1 - 0.3):
        aabb("shell", BLUE, xw - s * 0.35, y - 0.3, FZ, xw, y + 0.3, WALL - 0.5)
    aabb("shell", BLUE, lo_ - 0.1, Y0, WALL - 0.5, hi_ + 0.1, Y1 + 0.4, WALL)  # top beam
    aabb("shell", BLUE, lo_ - 0.1, Y0 - 0.1, FZ, hi_ + 0.1, Y0 + 0.3, WALL)  # front edge frame
aabb("shell", BLUE, X0 - 0.5, Y1 - 0.1, WALL - 0.5, X1 + 0.5, Y1 + 0.5, WALL)
# open front: a low cut kerb only
CUT = FZ + 0.25
aabb("shell", "#DCE2E8", X0, Y0 - 0.4, FZ, X1, Y0, CUT)
aabb("shell", "#C9D2DC", X0 - 0.4, Y0 - 0.4, 0, X1 + 0.4, Y0, FZ)

# ---- zone signs: boards hinged on each side wall in front of its doors, turned
# towards the camera so the lettering reads (flat on the wall it was a sliver)
SW = 5.2 if LAYOUT == "wide" else 4.6
SIGN_A = math.radians(55)  # 0 = flat on the wall, 90 = square to the camera
SIGN_Z0, SIGN_Z1 = DOOR_Z + 1.2, DOOR_Z + 3.0
SIGNS = {"ПРИЁМКА": (-1, BLUE), "ОТГРУЗКА": (1, ORANGE)}
SIGN_C, SIGN_BOXES = {}, {}
for label, (s, col) in SIGNS.items():
    hinge = Vector(((X0 if s < 0 else X1) - s * 0.4, DOORS[0][0] - 0.8, 0))
    t = Vector((-s * math.sin(SIGN_A), math.cos(SIGN_A), 0))  # along the board, away from the wall
    n = Vector((-s * math.cos(SIGN_A), -math.sin(SIGN_A), 0))  # board face, towards the camera
    c = hinge + t * SW / 2
    phi = math.atan2(n.y, n.x)
    box("signs", col, (c.x, c.y, (SIGN_Z0 + SIGN_Z1) / 2), (0.2, SW, SIGN_Z1 - SIGN_Z0), rot=phi)
    beam("signs", "#3A414B", (hinge.x, hinge.y, SIGN_Z1 - 0.2), (hinge.x + s * 0.4, hinge.y, SIGN_Z1 - 0.2), 0.12)
    tc = c + n * 0.13
    text("signs_text", label, (tc.x, tc.y, (SIGN_Z0 + SIGN_Z1) / 2 - 0.02), 1.0, "#FFFFFF", rot=(math.pi / 2, 0, phi + math.pi / 2))
    SIGN_C[label] = Vector((c.x, c.y, (SIGN_Z0 + SIGN_Z1) / 2))
    e = t * (SW / 2 + 0.1)
    SIGN_BOXES[label] = [c + d + Vector((0, 0, z)) for d in (e, -e) for z in (SIGN_Z0, SIGN_Z1)]


# ---- racks ------------------------------------------------------------------------
LEVELS = [FZ + 0.15 + 1.5 * k for k in range(4)]
RACK_TOP = FZ + 6.0


def carton(group, x0, y0, z0, x1, y1, z1, col=KRAFT, tape=True):
    aabb(group, col, x0, y0, z0, x1, y1, z1)
    if tape and col == KRAFT:
        xm = (x0 + x1) / 2
        aabb(group, "#C08E4E", xm - 0.08, y0 - 0.01, z1 - 0.01, xm + 0.08, y1 + 0.01, z1 + 0.01, nolines=True)


def pallet(group, x, y, z, w=1.2, d=1.2):
    aabb(group, "#C79A5B", x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + 0.15)


def load(group, xc, yc, w, d, z, rng):
    """One pallet of goods: a single calm block of cartons (the hall must read at a glance)."""
    pallet(group, xc, yc, z, w=w, d=d)
    h = rng.choice((0.9, 1.0, 1.1))
    col = WHITE if rng.random() < 0.12 else KRAFT
    carton(group, xc - w / 2 + 0.06, yc - d / 2 + 0.06, z + 0.15, xc + w / 2 - 0.06, yc + d / 2 - 0.06, z + 0.15 + h, col=col)


def rack_row(group, x0, x1, y0, y1, free=(), seed=0):
    """A pallet rack row along y: blue uprights, orange beams on both faces, one
    pallet per bay and level. `free` lists (level, bay) cells left empty."""
    rng = random.Random(seed)
    nb = max(1, round((y1 - y0) / 2.9))
    ys = [y0 + (y1 - y0) * k / nb for k in range(nb + 1)]
    for y in ys:
        for x in (x0, x1):
            aabb(group, BLUE, x - 0.1, y - 0.1, FZ, x + 0.1, y + 0.1, RACK_TOP)
    for z in LEVELS[1:]:
        for x in (x0, x1):
            aabb(group, ORANGE, x - 0.08, y0, z - 0.2, x + 0.08, y1, z)
    for x in (x0, x1):  # orange foot rail, as in the illustration
        aabb(group, ORANGE, x - 0.12, y0 - 0.25, FZ, x + 0.12, y1 + 0.25, FZ + 0.18)
    cells = {}
    for li, z in enumerate(LEVELS):
        for bi, (a, b) in enumerate(zip(ys, ys[1:])):
            cells[(li, bi)] = (a, b, z)
            if (li, bi) in free:
                continue
            load(group, (x0 + x1) / 2, (a + b) / 2, x1 - x0 - 0.25, b - a - 0.5, z, rng)
    return cells


RY0, RY1 = P["RY"]
RW = P["RW"]
RANGES = [("А–Б", "АБ"), ("В–К", "ВГДЕЁЖЗИЙК"), ("Л–М", "ЛМ"), ("Н–У", "НОПРСТУ"), ("Ф–Э", "ФХЦЧШЩЪЫЬЭ"), ("Ю–Я", "ЮЯ")]
# three back-to-back pairs; row x0 left to right, so the alphabet reads left to right
RANGES = [(label, letters, P["PAIRS"][i // 2] + (-RW - 0.15 if i % 2 == 0 else 0.15)) for i, (label, letters) in enumerate(RANGES)]
ALPHA_ROW = {"camera": 4, "socks": 3, "boat": 2}
HOT_ROW = 5
GIFT_CELL = (len(LEVELS) - 1, max(1, round((RY1 - RY0) / 2.9)) - 1)
# Letter plaque: a white board in a navy frame on the row's front end, at eye-catching
# height between the second and third levels; one range per board, e.g. «А–Б».
PLAQUE_Z0, PLAQUE_Z1 = LEVELS[1] + 0.55, LEVELS[2] + 0.75
PW = RW / 2 - 0.2
CELLS = {}
for i, (label, letters, x0) in enumerate(RANGES):
    free = {GIFT_CELL} if i in ALPHA_ROW.values() or i == HOT_ROW else set()
    CELLS[i] = rack_row(f"rack_{i}", x0, x0 + RW, RY0, RY1, free=free, seed=10 + i)
    cx = x0 + RW / 2
    aabb(f"rack_{i}", NAVY, cx - PW, RY0 - 0.36, PLAQUE_Z0, cx + PW, RY0 - 0.2, PLAQUE_Z1)
    aabb(f"rack_{i}", "#FFFFFF", cx - PW + 0.1, RY0 - 0.4, PLAQUE_Z0 + 0.1, cx + PW - 0.1, RY0 - 0.36, PLAQUE_Z1 - 0.1, nolines=True)
    text("plaques", label, (cx, RY0 - 0.42, (PLAQUE_Z0 + PLAQUE_Z1) / 2), P["PT"], NAVY)


def cell_spot(i, cell=GIFT_CELL, inset=0.9):
    """Floor point of a rack cell, near the row's outer (aisle) face."""
    a, b, z = CELLS[i][cell]
    x0 = RANGES[i][2]
    return Vector((x0 + (inset if i % 2 == 0 else RW - inset), (a + b) / 2, z + 0.15))


# Free cells right by receiving: a short rack along the left wall, in front of the doors.
EX0, EX1 = P["ENTR"]  # along y
EY0, EY1 = X0 + 0.4, X0 + 1.7  # depth along x
ELEV = LEVELS[:3]
rng = random.Random(7)
nb = max(3, round((EX1 - EX0) / 1.6))
eys = [EX0 + (EX1 - EX0) * k / nb for k in range(nb + 1)]
for y in eys:
    for x in (EY0, EY1):
        aabb("entrance_rack", BLUE, x - 0.1, y - 0.1, FZ, x + 0.1, y + 0.1, FZ + 4.4)
for z in ELEV[1:]:
    for x in (EY0, EY1):
        aabb("entrance_rack", ORANGE, x - 0.08, EX0, z - 0.2, x + 0.08, EX1, z)
FREE = {(0, 1), (1, nb - 1), (2, 0)}
FREE_CELL = None
for li, z in enumerate(ELEV):
    for k, (a, b) in enumerate(zip(eys, eys[1:])):
        if (li, k) in FREE:
            if (li, k) == (0, 1):
                FREE_CELL = ((EY0 + EY1) / 2 + 0.2, (a + b) / 2, z + 0.15)
            continue
        load("entrance_rack", (EY0 + EY1) / 2, (a + b) / 2, EY1 - EY0 - 0.2, b - a - 0.3, z, rng)


GIFT_SIZE = 1.5


def gift(group, x, y, z, k=GIFT_SIZE, on_pallet=True):
    """A bright red gift box with a white ribbon and bow: it must read as THE gift
    among the brown cartons without any glow or ring around it."""
    if on_pallet:
        aabb(group, "#C79A5B", x - 0.7 * k, y - 0.7 * k, z, x + 0.7 * k, y + 0.7 * k, z + 0.15)
        z += 0.15
    h = 0.8 * k
    aabb(group, "#E23B32", x - 0.55 * k, y - 0.55 * k, z, x + 0.55 * k, y + 0.55 * k, z + h)
    aabb(group, "#FFFFFF", x - 0.09 * k, y - 0.565 * k, z, x + 0.09 * k, y + 0.565 * k, z + h + 0.02)
    aabb(group, "#FFFFFF", x - 0.565 * k, y - 0.09 * k, z, x + 0.565 * k, y + 0.09 * k, z + h + 0.02)
    for a in (0.6, -0.6, math.pi - 0.6, math.pi + 0.6):
        ball(group, "#FFFFFF", (x + 0.2 * k * math.cos(a), y + 0.2 * k * math.sin(a), z + h + 0.08 * k), 0.19 * k, sx=1.0, sy=0.55, sz=0.5)
    ball(group, "#F3F3F3", (x, y, z + h + 0.06 * k), 0.09 * k)
    return Vector((x, y, z + h + 0.2 * k))


GIFT_IN = Vector((*P["GIFT"], FZ))
GIFT_TOP = gift("gift", *GIFT_IN)
STRIPE = "#DCE3EA"  # reflective tape on the Gazpromneft workwear


def person(group, c, facing, cap=BLUE, suit=NAVY, hair=None, mustache=None, s=PEOPLE, pose=None, tsd=False, walk=0.0, tablet=False):
    """Game figure in the company workwear (docs/scenario-assets/image20.png): a navy jacket
    and trousers with reflective stripes, a blue cap or a bare head."""
    M = Matrix.Translation(c) @ Matrix.Rotation(facing, 4, "Z") @ Matrix.Diagonal((s, s, s, 1))
    for dy, sw in ((-0.13, walk), (0.13, -walk)):
        box(group, suit, (sw * 0.3, dy, 0.42), (0.2, 0.18, 0.84), M=M)
        box(group, STRIPE, (sw * 0.3, dy, 0.28), (0.21, 0.19, 0.05), M=M)
        box(group, "#2B2F36", (sw * 0.3 + 0.05, dy, 0.05), (0.3, 0.2, 0.1), M=M)
    base = 0.84
    box(group, suit, (0, 0, base + 0.33), (0.3, 0.46, 0.66), M=M)
    for z in (base + 0.22, base + 0.42):
        box(group, STRIPE, (0, 0, z), (0.31, 0.47, 0.05), M=M)
    arms = pose if pose and isinstance(pose[0], tuple) else (pose or (0, 0),) * 2
    for dy, arm in zip((-0.29, 0.29), arms):
        beam(group, suit, (0, dy, base + 0.62), (0.18 + arm[0], dy * 1.1, base + 0.2 + arm[1]), 0.14, M=M)
        ball(group, "#F2C29B", (0.18 + arm[0], dy * 1.1, base + 0.2 + arm[1]), 0.07, M=M, sub=1)
    if tsd:
        a = arms[1]
        box(group, "#2B2F36", (0.26 + a[0], 0.32, base + 0.26 + a[1]), (0.16, 0.09, 0.05), M=M)
        box(group, "#7FD0F5", (0.26 + a[0], 0.32, base + 0.29 + a[1]), (0.1, 0.06, 0.01), mat="flat", M=M)
    if tablet:  # held in both hands in front of the chest
        box(group, "#2B2F36", (0.3, 0, base + 0.42), (0.04, 0.4, 0.3), M=M)
        box(group, "#7FD0F5", (0.33, 0, base + 0.42), (0.01, 0.34, 0.24), mat="flat", M=M)
    ball(group, "#F2C29B", (0, 0, base + 0.88), 0.21, M=M)
    ball(group, "#2B2F36", (0.2, -0.07, base + 0.92), 0.03, M=M, sub=1)
    ball(group, "#2B2F36", (0.2, 0.07, base + 0.92), 0.03, M=M, sub=1)
    if mustache:
        ball(group, mustache, (0.19, 0, base + 0.83), 0.06, sx=0.7, sy=2.0, sz=0.6, M=M, sub=1)
    if hair:
        ball(group, hair, (-0.03, 0, base + 0.95), 0.21, sx=0.95, sz=0.6, M=M)
    if cap:  # a blue baseball cap, peak forward
        ball(group, cap, (0, 0, base + 0.99), 0.22, sz=0.55, M=M)
        box(group, cap, (0.24, 0, base + 0.97), (0.2, 0.3, 0.03), M=M)
    return Vector(M @ Vector((0, 0, base + 1.1)))



def facing_to(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


def pallet_jack(group, x, y, facing, handle=1.0):
    """Hand pallet jack: two forks under the load, the tow handle pointing along `facing`."""
    M = Matrix.Translation((x, y, FZ)) @ Matrix.Rotation(facing, 4, "Z")
    for dy in (-0.35, 0.35):
        aabb(group, "#E8892B", -0.9, dy - 0.12, 0.03, 0.9, dy + 0.12, 0.13, M=M)
    aabb(group, "#E8892B", 0.9, -0.5, 0.03, 1.2, 0.5, 0.5, M=M)
    cyl(group, "#2B2F36", (1.1, 0, 0.12), 0.12, 0.3, axis="Y", seg=12, M=M)
    beam(group, "#3A414B", (1.1, 0, 0.5), (1.1 + 0.9 * handle, 0, 1.35), 0.09, M=M)
    beam(group, "#2B2F36", (1.1 + 0.9 * handle, -0.25, 1.35), (1.1 + 0.9 * handle, 0.25, 1.35), 0.1, M=M)
    return Vector(M @ Vector((1.1 + 0.9 * handle + 0.5, 0, 0)))


# receiving: the gift has just come off the truck; a worker tows it on a pallet jack
pallet_jack("jack", GIFT_IN.x, GIFT_IN.y, 0.0)
JACK_AT = Vector((GIFT_IN.x + P["JACK_DX"] + 0.4, GIFT_IN.y, FZ))
person("jack", tuple(JACK_AT), math.pi, pose=(0.35, 0.3))
person("workers", (*P["SCAN_IN"], FZ), facing_to(P["SCAN_IN"], P["GIFT"]), tsd=True, pose=((0, 0), (0.25, 0.35)))
for k, (x, y) in enumerate(((3.6, 2.2), (5.2, 2.2), (3.6, 3.8))):  # front-left: unloaded pallets waiting for a cell
    pallet("staging_in", x, y, FZ)
    carton("staging_in", x - 0.5, y - 0.5, FZ + 0.15, x + 0.5, y + 0.5, FZ + 1.1)
    if k != 1:
        carton("staging_in", x - 0.4, y - 0.4, FZ + 1.1, x + 0.4, y + 0.4, FZ + 1.7, col=WHITE)

# dispatch: the barge consignment, stretch-wrapped, staged by the dispatch door
for x, y in P["BARGE"]:
    pallet("staging_out", x, y, FZ, 1.5, 1.5)
    aabb("staging_out", "#CFE3F2", x - 0.65, y - 0.65, FZ + 0.15, x + 0.65, y + 0.65, FZ + 1.6)
    aabb("staging_out", "#E9F2F9", x - 0.66, y - 0.2, FZ + 0.3, x + 0.66, y + 0.2, FZ + 1.45, nolines=True)
person("workers", (*P["SCAN_OUT"], FZ), facing_to(P["SCAN_OUT"], P["BARGE"][2]), tsd=True, pose=((0, 0), (0.25, 0.35)))

# keeper Pavel: grey hair and moustache, bare head, tablet, at the front right by Ю–Я
KEEPER = Vector((*P["KEEPER"], FZ))
KEEPER_HEAD = person("keeper", tuple(KEEPER), math.radians(-115), cap=None, hair="#C9CDD2", mustache="#C9CDD2", pose=((0.12, 0.1), (0.12, 0.1)), tablet=True)
LX, LY = KEEPER.x - 1.3, KEEPER.y - 0.3
aabb("keeper", "#8A5A33", LX - 0.5, LY - 0.4, FZ, LX + 0.5, LY + 0.4, FZ + 1.5)
aabb("keeper", "#F4EBD6", LX - 0.45, LY - 0.36, FZ + 1.5, LX + 0.45, LY + 0.36, FZ + 1.58)

# «Автоподбор»: the warehouse system's desk against the dock wall, monitor facing
# the hall; the six rack rows on the screen, the one by dispatch lit green.
DX0, DX1 = P["DESK"]
DY0, DY1 = P["DESK_Y"]
DTOP = FZ + 1.35
aabb("wms", "#E9EDF1", DX0, DY0, DTOP - 0.12, DX1, DY1, DTOP)
for x in (DX0 + 0.1, DX1 - 0.25):
    aabb("wms", "#3A414B", x, DY0 + 0.1, FZ, x + 0.15, DY1 - 0.1, DTOP - 0.12)
aabb("wms", "#C9D2DC", DX1 - 1.2, DY0 + 0.15, FZ, DX1 - 0.3, DY1 - 0.15, DTOP - 0.15)  # drawer unit
MX = (DX0 + DX1) / 2
aabb("wms", "#3A414B", MX - 0.12, DY1 - 0.45, DTOP, MX + 0.12, DY1 - 0.25, DTOP + 0.5)
SCREEN = (MX - 1.25, DY1 - 0.6, DTOP + 0.45, MX + 1.25, DY1 - 0.45, DTOP + 2.0)
aabb("wms", "#24303F", SCREEN[0] - 0.12, SCREEN[1], SCREEN[2] - 0.12, SCREEN[3] + 0.12, SCREEN[4], SCREEN[5] + 0.12)
aabb("wms", "#16324F", SCREEN[0], SCREEN[1] - 0.03, SCREEN[2], SCREEN[3], SCREEN[1], SCREEN[5], mat="flat", nolines=True)
SW_ = (SCREEN[3] - SCREEN[0]) / 7.4
for i in range(6):
    x = SCREEN[0] + SW_ * (0.75 + i * 1.0)
    aabb("wms", "#5FD38D" if i == 5 else "#7FD0F5", x, SCREEN[1] - 0.05, SCREEN[2] + 0.3, x + SW_ * 0.55, SCREEN[1] - 0.03, SCREEN[5] - 0.25, mat="flat", nolines=True)
aabb("wms", "#2B2F36", MX - 0.6, DY0 + 0.2, DTOP, MX + 0.6, DY0 + 0.6, DTOP + 0.05)  # keyboard
OPERATOR = (DX1 + 0.8, (DY0 + DY1) / 2)
person("wms", (*OPERATOR, FZ), facing_to(OPERATOR, (MX, DY1)), pose=((0.3, 0.45), (0.1, 0.0)))


def forklift(group, x, y, facing, load=True):
    """Driverless forklift (AGV): forks along +x in model space."""
    M = Matrix.Translation((x, y, FZ)) @ Matrix.Rotation(facing, 4, "Z") @ Matrix.Diagonal((1.3, 1.3, 1.3, 1))
    aabb(group, ORANGE, -1.2, -0.7, 0.3, 0.6, 0.7, 1.5, M=M)
    aabb(group, "#3A414B", -1.3, -0.72, 0.3, -0.8, 0.72, 1.6, M=M)
    aabb(group, "#2B2F36", 0.6, -0.55, 0.1, 0.8, 0.55, 3.2, M=M)
    for dy in (-0.35, 0.35):
        aabb(group, "#2B2F36", 0.8, dy - 0.07, 0.1, 2.0, dy + 0.07, 0.2, M=M)
    for dx, dy in ((-0.8, -0.72), (-0.8, 0.72), (0.3, -0.72), (0.3, 0.72)):
        cyl(group, "#2B2F36", (dx, dy, 0.32), 0.32, 0.28, axis="Y", seg=14, M=M)
    cyl(group, "#2B2F36", (-0.3, 0, 1.65), 0.2, 0.3, seg=12, M=M)  # lidar
    cyl(group, YELLOW, (-1.0, 0, 1.75), 0.1, 0.5, seg=10, M=M)
    if load:
        aabb(group, "#C79A5B", 0.9, -0.6, 0.2, 2.1, 0.6, 0.35, M=M)
        aabb(group, KRAFT, 0.95, -0.55, 0.35, 2.05, 0.55, 1.35, M=M)


forklift("agv", *P["FORK"], math.pi / 2)


# ---- outcome-only actors (group names start with o_) -------------------------------
GK = 1.15  # gift scale inside a rack cell
O_GIFT_ENTRANCE = gift("o_gift_entrance", *FREE_CELL, k=GK, on_pallet=False)
O_GIFT_ALPHA = {p: gift(f"o_gift_{p}", *cell_spot(i), k=GK, on_pallet=False) for p, i in ALPHA_ROW.items()}
O_GIFT_HOT = gift("o_gift_hot", *cell_spot(HOT_ROW), k=GK, on_pallet=False)


def aisle(i):
    return RANGES[i][2] - 0.9 if i % 2 == 0 else RANGES[i][2] + RW + 0.9  # the aisle outside rack row i


def to_dispatch(x, y):
    """Walk: down to the cross aisle, along it, into the dispatch door."""
    return [(x, y), (x, LANE), (DX_OUT, LANE), (DX_OUT, DOORS_Y[0]), (X1 - 0.3, DOORS_Y[0])]


ROUTES = {"entrance": to_dispatch(EY1 + 0.6, FREE_CELL[1]),
          **{p: [(cell_spot(i).x, cell_spot(i).y)] + to_dispatch(aisle(i), cell_spot(i).y) for p, i in ALPHA_ROW.items()},
          "hot": [(cell_spot(HOT_ROW).x, cell_spot(HOT_ROW).y)] + to_dispatch(aisle(HOT_ROW), cell_spot(HOT_ROW).y)}
ROUTE_M = {k: round(sum((Vector(b) - Vector(a)).length for a, b in zip(v, v[1:]))) for k, v in ROUTES.items()}
print("ROUTE_M", ROUTE_M)


def carrier(group, x, y, facing, box=True):
    """Worker walking with a carton held in front."""
    head = person(group, (x, y, FZ), facing, walk=0.35, pose=((0.35, 0.35), (0.35, 0.35)))
    if box:
        c, s_ = math.cos(facing), math.sin(facing)
        cx, cy = x + 0.85 * c, y + 0.85 * s_
        carton(group, cx - 0.4, cy - 0.4, FZ + 1.55, cx + 0.4, cy + 0.4, FZ + 2.2)
    return head


# entrance: a worker carries goods from the far free cell all the way to dispatch,
# another walks back for the next box
(a, b) = P["RUN_E"]
carrier("o_runners_entrance", *a, 0.0)
person("o_runners_entrance", (*b, FZ), facing_to(b, FREE_CELL), walk=-0.35)
# alphabet: a picker at the gift's row, another hurrying along the cross aisle
for p, i in ALPHA_ROW.items():
    s_ = cell_spot(i)
    person(f"o_runners_{p}", (aisle(i), s_.y - 0.4, FZ), 0.0, tsd=True, pose=((0, 0), (0.25, 0.35)))
    carrier(f"o_runners_{p}", (aisle(i) + DX_OUT) / 2, LANE, 0.0)
# keeper: Pavel is gone; two new-shift workers (white caps) search with scanners
O_HEADS = []
for k, (x, y) in enumerate(P["PUZZLED"]):
    head = person("o_newshift", (x, y, FZ), math.radians(60 + 50 * k), cap="#FFFFFF", tsd=True, pose=((0.05, 0.75), (0.25, 0.35)))
    O_HEADS.append(head)  # the "?" over each head is lettered by compose.py
# wms: the system pointed to the hot cell, so the gift already rolls into the truck
JX, JY = X1 - 4.0, DOORS_Y[0] - 4.0
pallet_jack("o_jack_out", JX, JY, 0.0)
O_GIFT_OUT = gift("o_jack_out", JX, JY, FZ + 0.13, k=1.0)
person("o_jack_out", (JX + 2.6, JY, FZ), 0.0, walk=0.3, pose=((-0.35, -0.2), (-0.35, -0.2)))

f3 = lambda pts: [Vector((x, y, FZ + 0.05)) for x, y in pts]
STORY = {
    "entrance": (O_GIFT_ENTRANCE, f3(ROUTES["entrance"])),
    **{f"alphabet-{p}": (O_GIFT_ALPHA[p], f3(ROUTES[p])) for p in ALPHA_ROW},
    "keeper": (O_GIFT_HOT, f3(ROUTES["hot"])),
    "wms": (O_GIFT_OUT, f3([(JX, JY), (DX_OUT, JY), (DX_OUT, DOORS_Y[0]), (X1 - 0.3, DOORS_Y[0])])),
}
flush()
# ---- light, world, ink --------------------------------------------------------
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
scene.collection.objects.link(sun)
sun.data.energy = 2.6
sun.data.angle = math.radians(6)
d = Vector((-0.45, -0.7, 1.15)).normalized()
sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = srgb("#DCE8F4")
bg.inputs[1].default_value = 0.22
scene.view_settings.view_transform = "Standard"
scene.render.engine = "BLENDER_EEVEE"
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
ls.collection = NOLINES
ls.collection_negation = "EXCLUSIVE"
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new("ink")
ls.linestyle.color = srgb("#1F2B3C")[:3]
ls.linestyle.alpha = 0.9


# ---- cameras -------------------------------------------------------------------------
FORMATS_SPEC = {
    # name: (res, azimuth, elevation, keep box u0,v0,u1,v1 in y-down screen space)
    # v16: centred perspective (as in the v6 illustration) so both side walls show their inner face
    "desk": ((1536, 1024), float(os.environ.get("DESK_AZ", 0)), float(os.environ.get("DESK_EL", 38)), (0.0, 0.0, 1.0, 1.0)),
    # v17 phone plate (LAYOUT=tall): 4:5, the hall fills the width, yard above and below
    "tall": ((1200, 1500), 0.0, float(os.environ.get("TALL_EL", 46)), (0.0, 0.0, 1.0, 1.0)),
}
PERSP_D = float(os.environ.get("PERSP_D", 62))  # camera distance from the hall centre
OUTCOME_RES = (1960, 840)


def axes(az, el):
    rot = (math.radians(90 - el), 0, math.radians(az))
    m = Euler(rot, "XYZ").to_matrix()
    return rot, m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0)), m @ Vector((0, 0, -1))


def cube(x0, y0, z0, x1, y1, z1):
    return [Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


# Frame the whole hall with both side walls and the back wall, a little yard around.
def play_box():
    return cube(X0 - 0.6, Y0 - 0.6, 0, X1 + 0.6, Y1 + 0.4, WALL)


def camera(name, spec, keep=None, right=False, dist=None):
    (W, H), az, el, (u0, v0, u1, v1) = spec
    if dist:
        return persp_camera(name, spec, keep or play_box(), dist)
    rot, R, U, F = axes(az, el)
    KEEP = keep or play_box()
    xs = [p.dot(R) for p in KEEP]
    ys = [p.dot(U) for p in KEEP]
    aspect = W / H
    S = max((max(xs) - min(xs)) / (u1 - u0), (max(ys) - min(ys)) / (v1 - v0) * aspect)
    Hh = S / aspect
    cx = (min(xs) + max(xs)) / 2 + (0.5 - (u0 + u1) / 2) * S
    if right:  # pin the dispatch side to the right edge; spare width goes to the hall, not the empty yard
        cx = max(xs) - (u1 - 0.5) * S
    cy = (min(ys) + max(ys)) / 2 - (0.5 - (v0 + v1) / 2) * Hh
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.ortho_scale = S
    cam.data.clip_end = 3000
    cam.rotation_euler = rot
    cam.location = R * cx + U * cy - F * 900
    return cam


def persp_camera(name, spec, keep, dist):
    """Perspective camera looking at the hall centre from `dist`; lens and shift fit `keep`."""
    (W, H), az, el, (u0, v0, u1, v1) = spec
    rot, R, U, F = axes(az, el)
    loc = Vector(((X0 + X1) / 2, (Y0 + Y1) / 2, FZ)) - F * dist
    xs, ys = [], []
    for p in keep:
        v = p - loc
        xs.append(v.dot(R) / v.dot(F))
        ys.append(v.dot(U) / v.dot(F))
    aspect = W / H
    S = max((max(xs) - min(xs)) / (u1 - u0), (max(ys) - min(ys)) / (v1 - v0) * aspect)
    cx = (min(xs) + max(xs)) / 2 + (0.5 - (u0 + u1) / 2) * S
    cy = (min(ys) + max(ys)) / 2 - (0.5 - (v0 + v1) / 2) * S / aspect
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    scene.collection.objects.link(cam)
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.sensor_width = 36
    cam.data.lens = 36 / S
    cam.data.shift_x, cam.data.shift_y = cx / S, cy / S
    cam.data.clip_end = 3000
    cam.rotation_euler = rot
    cam.location = loc
    return cam


from bpy_extras.object_utils import world_to_camera_view


def project(cam, p, W, H):
    v = world_to_camera_view(scene, cam, Vector(p))
    return [round(v.x * W, 1), round((1 - v.y) * H, 1)]


def hull(pts):
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


# Interactive regions (3D boxes -> projected hull) and the object point their invisible
# keyboard button sits on (no badges: the player taps the object itself).
PH = PEOPLE * 1.95  # person height
REGIONS = {
    "entrance": (cube(EY0, EX0, FZ, EY1 + 0.2, EX1, FZ + 4.6), Vector((EY1, (EX0 + EX1) / 2, FZ + 2.3))),
    "keeper": (cube(KEEPER.x - 1.9, KEEPER.y - 0.9, FZ, KEEPER.x + 0.6, KEEPER.y + 0.6, FZ + PH), Vector((KEEPER.x, KEEPER.y, FZ + PH * 0.6))),
    "wms": (cube(DX0, DY0 - 0.6, FZ, DX1 + 1.4, DY1, SCREEN[5] + 0.12), Vector((MX, SCREEN[1], (SCREEN[2] + SCREEN[5]) / 2))),
}
for parcel, i in ALPHA_ROW.items():
    x0 = RANGES[i][2]
    REGIONS[f"alphabet-{parcel}"] = (cube(x0, RY0 - 0.4, FZ, x0 + RW, RY0 + 1.2, PLAQUE_Z1), Vector((x0 + RW / 2, RY0 - 0.4, (PLAQUE_Z0 + PLAQUE_Z1) / 2)))
LABELS = {  # text plaques, for required framing and the shelf ranges in the game
    **{label: Vector((x0 + RW / 2, RY0 - 0.16, (PLAQUE_Z0 + PLAQUE_Z1) / 2)) for label, _, x0 in RANGES},
    **SIGN_C,
}


def frame_data(cam, W, H):
    scene.render.resolution_x, scene.render.resolution_y = round(W * SS), round(H * SS)  # projection uses render aspect
    bpy.context.view_layer.update()
    d = {"width": W, "height": H, "regions": {}, "labels": {}, "signs": {}}
    for k, (pts, anchor) in REGIONS.items():
        d["regions"][k] = {"hull": hull([project(cam, p, W, H) for p in pts]), "anchor": project(cam, anchor, W, H)}
    for k, p in LABELS.items():
        d["labels"][k] = project(cam, p, W, H)
    for k, pts in SIGN_BOXES.items():
        q = [project(cam, p, W, H) for p in pts]
        d["signs"][k] = [min(p[0] for p in q), min(p[1] for p in q), max(p[0] for p in q), max(p[1] for p in q)]
    d["gift"] = project(cam, GIFT_TOP, W, H)
    return d


SS = float(os.environ.get("SS", 1.5))
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = int(os.environ.get("SAMPLES", 16))
OUTCOME_ONLY = {g for g in GROUPS if g.startswith("o_")}
ALL = set(GROUPS) - OUTCOME_ONLY
# Lettering and painted routes are composited back crisp after the style pass.
TEXT_GROUPS = {g for g in GROUPS if g.endswith("_text") or g == "plaques"}


def show_only(groups):
    for g, os_ in GROUPS.items():
        for o in os_:
            o.hide_render = g not in groups


def render(path, W, H, transparent=False):
    if os.environ.get("NORENDER"):  # manifest only
        return
    scene.render.resolution_x, scene.render.resolution_y = round(W * SS), round(H * SS)
    ls.linestyle.thickness = 1.5 * SS
    scene.render.film_transparent = transparent
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


manifest = {"formats": {}, "outcomes": {}, "route_m": ROUTE_M}
if MODE in ("test", "plate"):
    for name in FORMATS:
        spec = FORMATS_SPEC[name]
        W, H = spec[0]
        cam = camera(name, spec, dist=PERSP_D)
        scene.camera = cam
        bpy.context.view_layer.update()
        manifest["formats"][name] = frame_data(cam, W, H)
        show_only(ALL)
        render(OUT / f"{name}.png", W, H)
        if MODE == "plate":
            show_only(ALL - TEXT_GROUPS)  # style-pass input: same frame, no lettering
            render(OUT / f"{name}-notext.png", W, H)

# Outcome stills: the same building, other actors, a closer camera.
DISPATCH = cube(X1, DOORS[0][0] - 0.5, FZ, X1, DOORS[1][1] + 0.5, SIGN_Z1)  # every walk ends in the dispatch door


def row_box(i):
    """The gift's bay with its aisle, plus the row's letter plaque."""
    a, b, z = CELLS[i][GIFT_CELL]
    x0 = RANGES[i][2]
    return cube(x0 - 1.8, a, FZ, x0 + RW, b, RACK_TOP) + cube(x0, RY0, PLAQUE_Z0, x0 + RW, RY0, PLAQUE_Z1)


HOT = row_box(HOT_ROW)


OUTCOMES = {
    # name: (extra outcome groups, hidden base groups, keep points)
    "entrance": ({"o_gift_entrance", "o_runners_entrance"}, {"gift", "jack"},
                 cube(EY0, EX0, FZ, EY1, EX1, FZ + 4.6) + cube(*P["RUN_E"][0], FZ, *P["RUN_E"][0], FZ + 3.5) + DISPATCH),
    **{f"alphabet-{p}": ({f"o_gift_{p}", f"o_runners_{p}"}, {"gift", "jack"}, row_box(i) + cube(RANGES[i][2], LANE, FZ, DX_OUT, LANE, FZ + 3.5) + DISPATCH)
       for p, i in ALPHA_ROW.items()},
    "keeper": ({"o_gift_hot", "o_newshift"}, {"gift", "jack", "keeper"},
               cube(P["PUZZLED"][0][0] - 1, P["PUZZLED"][0][1] - 1, FZ, P["PUZZLED"][1][0] + 1, P["PUZZLED"][1][1], FZ + 4) + HOT + DISPATCH),
    "wms": ({"o_jack_out"}, {"gift", "jack"}, cube(DX0, DY0, FZ, DX1, DY1, SCREEN[5]) + HOT + DISPATCH),
}
O_AZ = float(os.environ.get("O_AZ", -30))
if MODE == "outcomes":
    W, H = OUTCOME_RES
    only = os.environ.get("ONLY")
    for name, (extra, hidden, keep) in OUTCOMES.items():
        if only and name not in only.split(","):
            continue
        cam = camera("o_" + name, ((W, H), O_AZ, FORMATS_SPEC["desk"][2], (0.03, 0.04, 0.97, 0.96)), keep)
        scene.camera = cam
        bpy.context.view_layer.update()
        manifest["outcomes"][name] = frame_data(cam, W, H)
        g, route = STORY[name]
        manifest["outcomes"][name]["story"] = {"gift": project(cam, g, W, H), "route": [project(cam, q, W, H) for q in route],
                                               "heads": [project(cam, h, W, H) for h in O_HEADS]}
        show_only((ALL - hidden) | extra)
        render(OUT / f"outcome-{name}.png", W, H)
        show_only(((ALL - hidden) | extra) - TEXT_GROUPS)
        render(OUT / f"outcome-{name}-notext.png", W, H)
(OUT / f"manifest-{LAYOUT}-{MODE}.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
if os.environ.get("SAVE"):
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "warehouse.blend"))
print("WAREHOUSE OK", MODE, FORMATS)
