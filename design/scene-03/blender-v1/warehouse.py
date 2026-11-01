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
FORMATS = args[2:] or (["tall"] if LAYOUT == "tall" else ["desk"])
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
# One plan, read like the customer reference (docs/scenario-assets/image7.jpg):
# both dock doors sit in the BACK wall with their signs mounted on the wall above
# them, the trucks stand outside backed into the doors, the rack rows run from the
# front of the hall towards the docks with aisles between them and their letter
# plaques on the front ends. Alphabet reads left to right: А–Б at receiving (left
# door) … Ю–Я at dispatch (right door). The floor stays clean: no painted routes.
LAYOUTS = {
    # DOCKS: two receiving doors (left) and two dispatch doors (right). The gift arrives
    # through the inner receiving door and leaves through the outer dispatch door, the
    # one nearest the Ю–Я row; the barge consignment waits by the inner dispatch door.
    "wide": dict(X1=52.0, Y1=34.0, DOCKS=((11.0, 18.0), (34.0, 41.0)), RY=(2.6, 19.0), RW=2.6, RX=(4.5, 7.4), PW=5.6, PT=2.2,
                 ENTR=(0.6, 7.0), DESK=(23.6, 27.0), GIFT=(17.2, 28.4), JACK_DX=1.6, SCAN_IN=(13.2, 26.6),
                 BARGE=[(32.4, 29.4), (34.0, 29.4), (35.6, 29.4), (32.4, 31.0), (34.0, 31.0), (37.2, 29.4)],
                 SCAN_OUT=(38.0, 27.0), KEEPER=(47.6, 4.6), LANE=23.4,
                 RUN_E=((30.0, 23.4), (6.0, 28.6)), PUZZLED=((31.7, 1.4), (39.1, 3.2))),
    "tall": dict(X1=36.0, Y1=44.0, DOCKS=((9.0, 14.6), (24.2, 29.8)), RY=(2.6, 26.0), RW=2.4, RX=(3.0, 5.4), PW=4.4, PT=1.8,
                 ENTR=(0.6, 6.2), DESK=(17.6, 20.8), GIFT=(13.4, 38.4), JACK_DX=1.5, SCAN_IN=(9.6, 36.8),
                 BARGE=[(22.6, 39.4), (24.2, 39.4), (25.8, 39.4), (22.6, 41.0)],
                 SCAN_OUT=(27.2, 37.4), KEEPER=(34.0, 1.3), LANE=31.0,
                 RUN_E=((21.0, 31.0), (5.0, 38.4)), PUZZLED=((23.1, 1.4), (28.5, 3.2))),
}
P = LAYOUTS[LAYOUT]
X0, Y0 = 0.0, 0.0
X1, Y1 = P["X1"], P["Y1"]
WALL = FZ + 10.6
PEOPLE = 1.6
(DX_IN0, DX_IN), (DX_OUT0, DX_OUT) = P["DOCKS"]
DOCK_X = [DX_IN0, DX_IN, DX_OUT0, DX_OUT]
DOOR = 2.6  # half width of the dock doors
DOOR_Z = FZ + 6.4
TRUCK = 1.45  # trailer as tall as the dock door; people ~2.6 m (readable, racks still tower over them)
TRAILER = 7.0
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
SX0, SX1, SY0, SY1 = -14.0, X1 + 24.0, -10.0, Y1 + 28.0  # the fenced lot
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
PX0, PX1 = X1 + 6.0, SX1 - 1.0
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
# containers and a spare trailer row at the far side of the truck yard
for k, col in enumerate(("#3D7DC8", "#E8892B", "#5E9E5A", "#3D7DC8")):
    x = SX1 - 4.5
    aabb("site", col, x - 1.25, Y1 + 6 + k * 3.0, 0, x + 1.25, Y1 + 8.6 + k * 3.0, 2.6)
    if k < 2:
        aabb("site", ("#E8892B", "#3D7DC8")[k], x - 1.25, Y1 + 6 + k * 3.0, 2.6, x + 1.25, Y1 + 8.6 + k * 3.0, 5.2)
for k in range(3):
    x = SX0 + 6 + k * 4.5
    aabb("site", "#F4F6F8", x - 1.3, Y1 + 14, 1.1, x + 1.3, Y1 + 26, 4.6)
    aabb("site", "#3A414B", x - 0.8, Y1 + 13.6, 0.7, x + 0.8, Y1 + 26, 1.1)
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
verge(X1 + 1.6, 1.0, PX0 - 1.4, Y1 - 1.0)
verge(SX0 + 0.8, 2.0, -3.2, Y1 - 2.0)
aabb("ground", "#D9D4CA", GX1 + 2.6, -2.4, 0.0, X1 + 1.0, -0.6, 0.06, nolines=True)  # pavement along the hall front
# dock yard markings: bay lines behind each door
for dx in DOCK_X:
    for x in (dx - 3.4, dx + 3.4):
        aabb("ground", LINE, x - 0.08, Y1 + 1.0, 0.0, x + 0.08, Y1 + 12, 0.02, nolines=True)


for x in range(-150, 240, 9):  # avenue along the far side of the road
    tree(x + random.uniform(-1, 1), RY_0 - 6.5, random.uniform(7, 9))
for y in range(int(SY0) + 4, int(SY1), 10):  # hedge of trees along the right fence
    tree(SX1 + 4 + random.uniform(-1, 1), y, random.uniform(7, 9))
for k in range(400):
    x, y = random.uniform(-150, 230), random.uniform(-150, 210)
    if NX1 - 46 < x < SX1 + 9 and RY_0 - 10 < y < SY1 + 6:
        continue
    tree(x, y, random.uniform(8, 12))

# ---- building shell: slab; back (dock) and right walls full height, front/left cut low
aabb("shell", "#C9D2DC", X0 - 0.4, Y0 - 0.4, 0, X1 + 0.4, Y1 + 0.4, FZ - 0.02)
aabb("floor", "#D6DEE7", X0, Y0, FZ - 0.05, X1, Y1, FZ, mat="floor", nolines=True)
DOORS = [(d - DOOR, d + DOOR) for d in DOCK_X]
# back wall, cut around the two dock doors
xs = [X0 - 0.4] + [e for d in DOORS for e in d] + [X1 + 0.4]
for a, b in zip(xs[::2], xs[1::2]):
    aabb("shell", "#F1E9D8", a, Y1, FZ, b, Y1 + 0.4, WALL)
    aabb("shell", BLUE, a, Y1 - 0.05, FZ, b, Y1, FZ + 0.9)
for a, b in DOORS:
    aabb("shell", "#F1E9D8", a, Y1, DOOR_Z, b, Y1 + 0.4, WALL)  # header above the door
    aabb("shell", "#B8C2CD", a - 0.1, Y1 - 0.5, DOOR_Z, b + 0.1, Y1, DOOR_Z + 0.6)  # rolled-up door
    for x in (a - 0.35, b):
        aabb("shell", "#2E3742", x, Y1 - 0.3, FZ, x + 0.35, Y1, DOOR_Z + 0.6)  # door posts
    aabb("shell", "#7E8894", a + 0.1, Y1 - 1.4, FZ - 0.04, b - 0.1, Y1 + 0.4, FZ + 0.03)  # dock leveller
    for x in (a + 0.3, b - 0.7):
        aabb("shell", "#2B2F36", x, Y1 + 0.4, FZ - 0.9, x + 0.4, Y1 + 0.75, FZ - 0.2)  # bumpers outside
aabb("shell", "#F1E9D8", X1, Y0 - 0.4, FZ, X1 + 0.4, Y1 + 0.4, WALL)
aabb("shell", BLUE, X1 - 0.05, Y0, FZ, X1, Y1, FZ + 0.9)
aabb("shell", BLUE, X0 - 0.5, Y1 - 0.1, WALL - 0.5, X1 + 0.5, Y1 + 0.5, WALL)
aabb("shell", BLUE, X1 - 0.1, Y0 - 0.5, WALL - 0.5, X1 + 0.5, Y1 + 0.5, WALL)
XP = sorted([X0 + 0.3, X1 - 0.3] + [x for x in range(4, int(X1), 6) if all(x < a - 1.2 or x > b + 1.2 for a, b in DOORS + [P["DESK"]])])
for x in XP:
    aabb("shell", BLUE, x - 0.3, Y1 - 0.35, FZ, x + 0.3, Y1, WALL - 0.5)
for y in range(0, int(Y1) + 1, 7):
    aabb("shell", BLUE, X1 - 0.35, y - 0.3, FZ, X1, y + 0.3, WALL - 0.5)
# high windows, one centred in each bay between the blue columns: on the dock wall
# between the doors (clear of the signs) and on the right wall
WIN = []
for p, q in zip(XP, XP[1:]):
    lo, hi = max(p + 1.0, DOORS[1][1] + 1.0), min(q - 1.0, DOORS[2][0] - 1.0)
    if hi - lo >= 3.0:
        c, w = (lo + hi) / 2, min(hi - lo, 4.6) / 2
        WIN.append((c - w, c + w))
for a, b in WIN:
    aabb("shell", "#FFFFFF", a - 0.2, Y1 - 0.12, FZ + 5.0, b + 0.2, Y1 - 0.02, FZ + 8.4)
    aabb("shell", "#7FB3E0", a, Y1 - 0.16, FZ + 5.2, b, Y1 - 0.1, FZ + 8.2, mat="glass")
for y in range(0, int(Y1) - 6, 7):
    aabb("shell", "#FFFFFF", X1 - 0.12, y + 1.1, FZ + 4.6, X1 - 0.02, y + 5.9, FZ + 8.0)
    aabb("shell", "#7FB3E0", X1 - 0.16, y + 1.3, FZ + 4.8, X1 - 0.1, y + 5.7, FZ + 7.8, mat="glass")
# left and front walls cut low (section cap)
CUT = FZ + 1.3
aabb("shell", "#F1E9D8", X0 - 0.4, Y0 - 0.4, FZ, X0, Y1 + 0.4, CUT)
aabb("shell", "#DCE2E8", X0 - 0.45, Y0 - 0.45, CUT, X0 + 0.05, Y1 + 0.45, CUT + 0.08)
aabb("shell", "#F1E9D8", X0 - 0.4, Y0 - 0.4, FZ, X1 + 0.4, Y0, CUT)
aabb("shell", "#DCE2E8", X0 - 0.45, Y0 - 0.45, CUT, X1 + 0.45, Y0 + 0.05, CUT + 0.08)
aabb("shell", "#C9D2DC", X0 - 0.4, Y0 - 0.4, 0, X1 + 0.4, Y0, FZ)

# ---- zone signs: boards mounted on the dock wall above each door ------------------
SW = 3.3
SIGN_Y, SIGN_Z0, SIGN_Z1 = Y1 - 0.12, DOOR_Z + 0.9, DOOR_Z + 2.5
SIGNS = {"ПРИЁМКА": ((DX_IN0 + DX_IN) / 2, BLUE), "ОТГРУЗКА": ((DX_OUT0 + DX_OUT) / 2, ORANGE)}
for label, (cx, col) in SIGNS.items():
    aabb("signs", col, cx - SW, SIGN_Y - 0.1, SIGN_Z0, cx + SW, SIGN_Y + 0.1, SIGN_Z1)
    text("signs_text", label, (cx, SIGN_Y - 0.13, (SIGN_Z0 + SIGN_Z1) / 2 - 0.02), 1.12, "#FFFFFF")


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
    """One pallet of goods: a single calm block of cartons (no drums, no crate mix:
    the hall must read at a glance)."""
    pallet(group, xc, yc, z, w=w, d=d)
    h = rng.choice((0.9, 1.0, 1.1))
    carton(group, xc - w / 2 + 0.06, yc - d / 2 + 0.06, z + 0.15, xc + w / 2 - 0.06, yc + d / 2 - 0.06, z + 0.15 + h)


def rack_row(group, x0, x1, y0, y1, free=(), seed=0):
    """A pallet rack row along y: blue uprights, orange beams on both faces, two
    pallets per bay and level. `free` lists (level, bay) cells left empty."""
    rng = random.Random(seed)
    nb = max(1, round((y1 - y0) / 3.1))
    ys = [y0 + (y1 - y0) * k / nb for k in range(nb + 1)]
    for y in ys:
        for x in (x0, x1):
            aabb(group, BLUE, x - 0.1, y - 0.1, FZ, x + 0.1, y + 0.1, RACK_TOP)
    for z in LEVELS[1:]:
        for x in (x0, x1):
            aabb(group, ORANGE, x - 0.08, y0, z - 0.2, x + 0.08, y1, z)
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
RANGES = [(label, letters, P["RX"][0] + i * P["RX"][1]) for i, (label, letters) in enumerate(RANGES)]
ALPHA_ROW = {"camera": 4, "socks": 3, "boat": 2}
HOT_ROW = 5
GIFT_CELL = (len(LEVELS) - 1, max(1, round((RY1 - RY0) / 3.1)) - 1)  # top level, back bay (nearest the docks): the gift reads from above
PLAQUE_Z0, PLAQUE_Z1 = RACK_TOP + 0.5, RACK_TOP + 3.3
PW = P["PW"] / 2  # half width of the aisle banner, wider than the rack: it must read on a phone
CELLS = {}
for i, (label, letters, x0) in enumerate(RANGES):
    free = {GIFT_CELL} if i in ALPHA_ROW.values() or i == HOT_ROW else set()
    CELLS[i] = rack_row(f"rack_{i}", x0, x0 + RW, RY0, RY1, free=free, seed=10 + i)
    cx = x0 + RW / 2
    for x in (x0 + 0.25, x0 + RW - 0.25):
        aabb(f"rack_{i}", NAVY, x - 0.07, RY0 - 0.07, RACK_TOP, x + 0.07, RY0 + 0.07, PLAQUE_Z0)
    aabb(f"rack_{i}", NAVY, cx - PW, RY0 - 0.1, PLAQUE_Z0, cx + PW, RY0 + 0.1, PLAQUE_Z1)
    aabb(f"rack_{i}", "#FFFFFF", cx - PW + 0.18, RY0 - 0.14, PLAQUE_Z0 + 0.18, cx + PW - 0.18, RY0 - 0.1, PLAQUE_Z1 - 0.18, nolines=True)
    text("plaques", label, (cx, RY0 - 0.17, (PLAQUE_Z0 + PLAQUE_Z1) / 2), P["PT"], NAVY)


def cell_spot(i, cell=GIFT_CELL, inset=0.9):
    """Floor point of a rack cell, near the aisle face the camera sees (left face)."""
    a, b, z = CELLS[i][cell]
    return Vector((RANGES[i][2] + inset, (a + b) / 2, z + 0.15))


# Free cells right by receiving: a short rack against the dock wall, left of the door.
EX0, EX1 = P["ENTR"]
EY0, EY1 = Y1 - 1.7, Y1 - 0.4
ELEV = LEVELS[:3]
rng = random.Random(7)
nb = max(3, round((EX1 - EX0) / 1.6))
eys = [EX0 + (EX1 - EX0) * k / nb for k in range(nb + 1)]
for x in eys:
    for y in (EY0, EY1):
        aabb("entrance_rack", BLUE, x - 0.1, y - 0.1, FZ, x + 0.1, y + 0.1, FZ + 4.4)
for z in ELEV[1:]:
    for y in (EY0, EY1):
        aabb("entrance_rack", ORANGE, EX0, y - 0.08, z - 0.2, EX1, y + 0.08, z)
FREE = {(0, 1), (1, nb - 1), (2, 0)}
FREE_CELL = None
for li, z in enumerate(ELEV):
    for k, (a, b) in enumerate(zip(eys, eys[1:])):
        if (li, k) in FREE:
            if (li, k) == (0, 1):
                FREE_CELL = ((a + b) / 2, (EY0 + EY1) / 2 - 0.2, z + 0.15)
            continue
        load("entrance_rack", (a + b) / 2, (EY0 + EY1) / 2, b - a - 0.3, EY1 - EY0 - 0.2, z, rng)


# ---- trucks: outside, backed into the dock doors --------------------------------
TRUCK_BLUE = "#1E63D0"


def truck(group, dx, cargo=KRAFT):
    """The scene-2 truck: blue cab-over tractor and a white ribbed trailer with a
    blue base rail and corner posts. Model space: rear at y = 0, cab towards -y;
    placed behind the dock wall with its open rear in the door."""
    M = Matrix.Translation((dx, Y1 + 0.75, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Diagonal((TRUCK, TRUCK, TRUCK, 1))
    L = TRAILER
    aabb(group, "#3A414B", -0.8, -L - 3.4, 0.75, 0.8, -0.2, 1.05, M=M)  # chassis
    aabb(group, "#F4F6F8", -1.3, -L, 1.1, 1.3, 0.0, 4.4, M=M)
    for s_ in (-1, 1):
        aabb(group, TRUCK_BLUE, s_ * 1.3 - 0.04, -L, 1.05, s_ * 1.3 + 0.04, 0.0, 1.38, M=M)
        for y in (-L, -0.15):
            aabb(group, TRUCK_BLUE, s_ * 1.3 - 0.05, y, 1.05, s_ * 1.3 + 0.05, y + 0.15, 4.4, M=M)
        k = 1
        while -L + k * 0.85 < -0.3:
            aabb(group, "#DDE3EA", s_ * 1.31 - 0.02, -L + k * 0.85 - 0.04, 1.4, s_ * 1.31 + 0.02, -L + k * 0.85 + 0.04, 4.3, nolines=True, M=M)
            k += 1
    # open rear: dark load space with the cargo inside
    aabb(group, "#39424E", -1.15, -0.4, 1.25, 1.15, 0.03, 4.25, M=M)
    for i in (-1, 0, 1):
        for zz in ((1.25, 2.25), (2.3, 3.2)):
            aabb(group, cargo, i * 0.72 - 0.33, -0.9, zz[0], i * 0.72 + 0.33, -0.3, zz[1], M=M)
    for yy in (-3.6, -2.45, -1.3):
        for s_ in (-1, 1):
            cyl(group, "#2B2F36", (s_ * 1.0, yy, 0.5), 0.5, 0.5, axis="X", seg=16, M=M)
    cy0, cy1 = -L - 3.45, -L - 1.25
    aabb(group, TRUCK_BLUE, -1.25, cy0, 1.0, 1.25, cy1, 3.75, M=M)
    beam(group, TRUCK_BLUE, (0, cy0 + 0.5, 3.7), (0, cy1 + 0.25, 4.3), 2.3, 0.3, M=M)
    aabb(group, TRUCK_BLUE, -1.1, cy1, 3.45, 1.1, cy1 + 0.4, 4.3, M=M)
    aabb(group, "#5A8CC4", -1.12, cy0 - 0.04, 2.45, 1.12, cy0 + 0.02, 3.45, mat="glass", M=M)
    aabb(group, "#D7DDE4", -1.28, cy0 - 0.12, 0.7, 1.28, cy0 + 0.3, 1.15, M=M)
    for s_ in (-1, 1):
        aabb(group, "#5A8CC4", s_ * 1.25 - 0.03, cy0 + 0.25, 2.45, s_ * 1.25 + 0.03, cy0 + 1.2, 3.4, mat="glass", M=M)
        aabb(group, "#22272E", s_ * 1.45 - 0.06, cy0 + 0.15, 2.5, s_ * 1.45 + 0.06, cy0 + 0.35, 3.3, M=M)
        cyl(group, "#C9D0D8", (s_ * 1.0, cy1 + 0.75, 0.75), 0.32, 1.1, axis="Y", seg=16, M=M)
        for yy in (cy0 + 0.9, -L + 0.5):
            cyl(group, "#2B2F36", (s_ * 1.05, yy, 0.55), 0.55, 0.45, axis="X", seg=16, M=M)


for d in (DX_IN0, DX_IN):
    truck("trucks", d)
for d in (DX_OUT0, DX_OUT):
    truck("trucks", d, cargo="#CFE3F2")


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
def person(group, c, facing, hat=ORANGE, vest=ORANGE, suit=NAVY, hair=None, mustache=None, s=PEOPLE, pose=None, tsd=False, walk=0.0):
    """Game figure: overalls with a hi-vis vest, hard hat or bare grey head."""
    M = Matrix.Translation(c) @ Matrix.Rotation(facing, 4, "Z") @ Matrix.Diagonal((s, s, s, 1))
    for dy, sw in ((-0.13, walk), (0.13, -walk)):
        box(group, suit, (sw * 0.3, dy, 0.42), (0.2, 0.18, 0.84), M=M)
        box(group, "#2B2F36", (sw * 0.3 + 0.05, dy, 0.05), (0.3, 0.2, 0.1), M=M)
    base = 0.84
    box(group, suit, (0, 0, base + 0.33), (0.3, 0.46, 0.66), M=M)
    box(group, vest, (0.01, 0, base + 0.36), (0.32, 0.48, 0.5), M=M)
    box(group, "#F4F6F8", (0.02, 0, base + 0.3), (0.33, 0.49, 0.05), M=M)
    arms = pose if pose and isinstance(pose[0], tuple) else (pose or (0, 0),) * 2
    for dy, arm in zip((-0.29, 0.29), arms):
        beam(group, suit, (0, dy, base + 0.62), (0.18 + arm[0], dy * 1.1, base + 0.2 + arm[1]), 0.14, M=M)
        ball(group, "#F2C29B", (0.18 + arm[0], dy * 1.1, base + 0.2 + arm[1]), 0.07, M=M, sub=1)
    if tsd:
        a = arms[1]
        box(group, "#2B2F36", (0.26 + a[0], 0.32, base + 0.26 + a[1]), (0.16, 0.09, 0.05), M=M)
        box(group, "#7FD0F5", (0.26 + a[0], 0.32, base + 0.29 + a[1]), (0.1, 0.06, 0.01), mat="flat", M=M)
    ball(group, "#F2C29B", (0, 0, base + 0.88), 0.21, M=M)
    ball(group, "#2B2F36", (0.2, -0.07, base + 0.92), 0.03, M=M, sub=1)
    ball(group, "#2B2F36", (0.2, 0.07, base + 0.92), 0.03, M=M, sub=1)
    if mustache:
        ball(group, mustache, (0.19, 0, base + 0.83), 0.06, sx=0.7, sy=2.0, sz=0.6, M=M, sub=1)
    if hair:
        ball(group, hair, (-0.03, 0, base + 0.95), 0.21, sx=0.95, sz=0.6, M=M)
    if hat:
        ball(group, hat, (0, 0, base + 1.0), 0.23, sz=0.7, M=M)
        cyl(group, hat, (0.04, 0, base + 0.99), 0.26, 0.03, M=M, seg=16)
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
for k, (x, y) in enumerate(((3.2, Y1 - 6.0), (5.0, Y1 - 6.0), (3.2, Y1 - 4.2))):  # unloaded pallets waiting for a cell
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

# keeper Pavel: grey hair and moustache, no hard hat, clipboard, in the aisle by Ю–Я
KEEPER = Vector((*P["KEEPER"], FZ))
KEEPER_HEAD = person("keeper", tuple(KEEPER), math.radians(-115), hat=None, vest="#F7B731", suit="#3D5A80", hair="#C9CDD2", mustache="#C9CDD2", pose=((0.15, 0.3), (0.05, 0.0)))
aabb("keeper", "#7A5230", KEEPER.x - 0.4, KEEPER.y - 0.75, FZ + 1.6, KEEPER.x - 0.1, KEEPER.y - 0.35, FZ + 2.05)
LX, LY = KEEPER.x - 1.3, KEEPER.y - 0.3
aabb("keeper", "#8A5A33", LX - 0.5, LY - 0.4, FZ, LX + 0.5, LY + 0.4, FZ + 1.5)
aabb("keeper", "#F4EBD6", LX - 0.45, LY - 0.36, FZ + 1.5, LX + 0.45, LY + 0.36, FZ + 1.58)

# «Автоподбор»: the warehouse system's desk against the dock wall, monitor facing
# the hall; the six rack rows on the screen, the one by dispatch lit green.
DX0, DX1 = P["DESK"]
DY0, DY1 = Y1 - 1.6, Y1 - 0.35
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
OPERATOR = (DX1 + 0.7, DY0 - 0.2)
person("wms", (*OPERATOR, FZ), facing_to(OPERATOR, (MX, DY1)), vest="#3D9BE9", pose=((0.3, 0.45), (0.1, 0.0)))


# ---- outcome-only actors (group names start with o_) -------------------------------
GK = 1.15  # gift scale inside a rack cell
O_GIFT_ENTRANCE = gift("o_gift_entrance", *FREE_CELL, k=GK, on_pallet=False)
O_GIFT_ALPHA = {p: gift(f"o_gift_{p}", *cell_spot(i), k=GK, on_pallet=False) for p, i in ALPHA_ROW.items()}
O_GIFT_HOT = gift("o_gift_hot", *cell_spot(HOT_ROW), k=GK, on_pallet=False)


def aisle(i):
    return RANGES[i][2] - (P["RX"][1] - RW) / 2  # the aisle left of rack row i


def to_dispatch(x, y):
    """Walk: down to the cross aisle, along it, into the dispatch door."""
    return [(x, y), (x, LANE), (DX_OUT, LANE), (DX_OUT, Y1 - 0.5)]


ROUTES = {"entrance": to_dispatch(FREE_CELL[0], EY0 - 0.6),
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
# keeper: Pavel is gone; two new-shift workers (green hats) search with scanners
O_HEADS = []
for k, (x, y) in enumerate(P["PUZZLED"]):
    head = person("o_newshift", (x, y, FZ), math.radians(60 + 50 * k), hat="#5FD38D", tsd=True, pose=((0.05, 0.75), (0.25, 0.35)))
    O_HEADS.append(head)  # the "?" over each head is lettered by compose.py
# wms: the system pointed to the hot cell, so the gift already rolls into the truck
JX, JY = DX_OUT - 0.4, Y1 - 4.2
pallet_jack("o_jack_out", JX, JY, math.pi / 2)
O_GIFT_OUT = gift("o_jack_out", JX, JY, FZ + 0.13, k=1.0)
person("o_jack_out", (JX, JY + 2.6, FZ), math.pi / 2, walk=0.3, pose=((-0.35, -0.2), (-0.35, -0.2)))

f3 = lambda pts: [Vector((x, y, FZ + 0.05)) for x, y in pts]
STORY = {
    "entrance": (O_GIFT_ENTRANCE, f3(ROUTES["entrance"])),
    **{f"alphabet-{p}": (O_GIFT_ALPHA[p], f3(ROUTES[p])) for p in ALPHA_ROW},
    "keeper": (O_GIFT_HOT, f3(ROUTES["hot"])),
    "wms": (O_GIFT_OUT, f3([(JX, JY), (DX_OUT, Y1 - 0.5)])),
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
    "desk": ((1536, 1024), float(os.environ.get("DESK_AZ", -26)), float(os.environ.get("DESK_EL", 48)), (0.0, 0.02, 1.0, 0.99)),
    "tall": ((1024, 1536), float(os.environ.get("TALL_AZ", -24)), float(os.environ.get("TALL_EL", 52)), (0.0, 0.08, 1.0, 0.99)),
}
OUTCOME_RES = (1960, 840)


def axes(az, el):
    rot = (math.radians(90 - el), 0, math.radians(az))
    m = Euler(rot, "XYZ").to_matrix()
    return rot, m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0)), m @ Vector((0, 0, -1))


def cube(x0, y0, z0, x1, y1, z1):
    return [Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


# Frame the whole hall, the dock wall with its signs and the rear of both trucks.
def play_box():
    return cube(X0 - 0.5, Y0 - 0.5, 0, X1 + 0.5, Y1 + 0.4, SIGN_Z1 + 0.4) + cube(DX_IN0 - 3, Y1, 0, DX_OUT + 3, Y1 + 3, 4.4 * TRUCK)


def camera(name, spec, keep=None, right=False):
    (W, H), az, el, (u0, v0, u1, v1) = spec
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


# Interactive regions (3D boxes -> projected hull) and their badge anchors.
REGIONS = {
    "entrance": (cube(EX0, EY0 - 0.2, FZ, EX1, EY1, FZ + 4.6), Vector(((EX0 + EX1) / 2, EY0, FZ + 5.6))),
    "keeper": (cube(KEEPER.x - 2.0, KEEPER.y - 0.9, FZ, KEEPER.x + 0.5, KEEPER.y + 0.5, FZ + 2.3), Vector((KEEPER.x - 2.2, KEEPER.y - 1.4, FZ))),  # badge on the floor in front of him: its caption stays below the Ю–Я banner
    "wms": (cube(DX0, DY0 - 0.6, FZ, DX1 + 1.2, DY1, SCREEN[5] + 0.12), Vector((MX, SCREEN[1], SCREEN[5] + 1.1))),
}
for parcel, i in ALPHA_ROW.items():
    x0 = RANGES[i][2]
    REGIONS[f"alphabet-{parcel}"] = (cube(x0, RY0 - 0.2, FZ, x0 + RW, RY0 + 1.2, PLAQUE_Z1), Vector((x0 + RW / 2, RY0, PLAQUE_Z1 + 1.1)))
LABELS = {  # text plaques, for required framing and the shelf ranges in the game
    **{label: Vector((x0 + RW / 2, RY0 - 0.16, (PLAQUE_Z0 + PLAQUE_Z1) / 2)) for label, _, x0 in RANGES},
    **{label: Vector((cx, SIGN_Y, (SIGN_Z0 + SIGN_Z1) / 2)) for label, (cx, _) in SIGNS.items()},
}
SIGN_BOXES = {label: cube(cx - SW - 0.2, SIGN_Y - 0.15, SIGN_Z0, cx + SW + 0.2, SIGN_Y + 0.15, SIGN_Z1) for label, (cx, _) in SIGNS.items()}


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
        cam = camera(name, spec)
        scene.camera = cam
        bpy.context.view_layer.update()
        manifest["formats"][name] = frame_data(cam, W, H)
        show_only(ALL)
        render(OUT / f"{name}.png", W, H)
        if MODE == "plate":
            show_only(ALL - TEXT_GROUPS)  # style-pass input: same frame, no lettering
            render(OUT / f"{name}-notext.png", W, H)

# Outcome stills: the same building, other actors, a closer camera.
DISPATCH = cube(DX_OUT - DOOR - 0.5, Y1, FZ, DX_OUT + DOOR + 0.5, Y1, SIGN_Z1)  # every walk ends in the dispatch door


def row_box(i):
    """The gift's bay with its aisle, plus the row's letter plaque."""
    a, b, z = CELLS[i][GIFT_CELL]
    x0 = RANGES[i][2]
    return cube(x0 - 1.8, a, FZ, x0 + RW, b, RACK_TOP) + cube(x0, RY0, PLAQUE_Z0, x0 + RW, RY0, PLAQUE_Z1)


HOT = row_box(HOT_ROW)


OUTCOMES = {
    # name: (extra outcome groups, hidden base groups, keep points)
    "entrance": ({"o_gift_entrance", "o_runners_entrance"}, {"gift", "jack"},
                 cube(EX0, LANE - 1.0, FZ, EX1, EY1, FZ + 4.6) + cube(*P["RUN_E"][0], FZ, *P["RUN_E"][0], FZ + 3.5) + DISPATCH),
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
