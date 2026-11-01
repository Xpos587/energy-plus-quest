# Scene 3 (warehouse) v1: the Inventory warehouse built as geometry, so racks,
# docks, trucks and people share one camera per format and every outcome is
# the same building, not a repaint of a repaint.
# blender --background --factory-startup --python warehouse.py -- OUTDIR MODE [FORMAT...]
#   MODE: test | plate | outcomes
# Reference: docs/scenario-assets/image7.jpg (isometric warehouse, tall blue/orange
# racks with big banners, dock doors with trucks, "зона отгрузки" signs).
# Layout: receiving dock front-left, dispatch dock front-right, alphabet racks
# А–Б … Ю–Я run left to right (receiving -> dispatch), keeper by Ю–Я,
# WMS kiosk at the dispatch zone. Text is real geometry (Roboto) so it stays
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


# ---- layout (metres): x left->right along the docks, y into the building, z up --
FZ = 1.2  # dock-height floor
# Two plans of the same warehouse: the wide one for landscape screens, a
# narrower one for portrait so letters stay readable on a phone. Both docks are
# in the FRONT wall: the trucks stand nose-to-camera in the foreground (cab seen
# from above-front, like scenes 1-2), the goods run a U from the left door, along
# the lane past the alphabet racks, down to the right door.
LAYOUTS = {
    "wide": dict(X1=40.0, Y1=22.0, DX=(4.2, 35.8), LANE=(8.0, 11.4),
                 ZONES=((6.2, 0.6, 19.0, 7.2), (21.0, 0.6, 33.8, 7.2)), SIGNS=(13.6, 27.6), SIGN_W=2.8,
                 RY=(13.5, 20.5), RX=(31.4, 28.8, 21.0, 18.4, 10.6, 8.0), ENTR=(13.6, 18.6, 1.2, 2.6),
                 GIFT=(9.8, 4.0), STAGE_IN=((17.6, 5.2),), SCAN_IN=(8.8, 6.2),
                 BARGE=[(23.4, 2.6), (25.2, 2.6), (27.0, 2.6), (23.4, 4.4), (25.2, 4.4)],
                 SCAN_OUT=(28.6, 4.6), KEEPER=(31.8, 3.4), KIOSK=(20.0, 5.4),
                 HOT=(37.0, 13.4), HOT_VIA=[(37.0, 12.4)],
                 RUN_E=((21.0, 10.3), (24.0, 10.8)), PUZZLED=((26.6, 12.4), (29.8, 12.2))),
    "tall": dict(X1=24.0, Y1=27.8, DX=(3.0, 21.0), LANE=(12.0, 15.2),
                 ZONES=((4.8, 0.6, 11.8, 11.0), (12.2, 0.6, 19.2, 11.0)), SIGNS=(8.3, 15.7), SIGN_W=2.6,
                 RY=(18.0, 25.8), RX=(20.0, 17.4, 13.0, 10.4, 6.0, 3.4), ENTR=(7.0, 11.4, 1.2, 2.6),
                 GIFT=(7.6, 6.0), STAGE_IN=(), SCAN_IN=(7.0, 9.2),
                 BARGE=[(14.0, 3.0), (15.8, 3.0), (14.0, 4.8), (15.8, 4.8)],
                 SCAN_OUT=(17.0, 6.4), KEEPER=(16.8, 8.8), KIOSK=(12.0, 9.4),
                 HOT=(21.6, 16.8), HOT_VIA=[(21.6, 16.0)],
                 RUN_E=((12.0, 14.2), (15.6, 14.7)), PUZZLED=((16.0, 16.6), (19.0, 16.4))),
}
P = LAYOUTS[LAYOUT]
X0, Y0 = 0.0, 0.0
X1, Y1 = P["X1"], P["Y1"]
WALL = FZ + 8.0
PEOPLE = 2.2
LANE0, LANE1 = P["LANE"]
LANE_C = (LANE0 + LANE1) / 2
DX_IN, DX_OUT = P["DX"]
DOOR = 2.6  # half width of the front dock doors (fits the full-size trailers)
TRUCK = 1.8  # trucks to the scale of the people (PEOPLE figures are ~4.3 m tall)
TRAILER = 7.0  # trailer length before scaling; the whole truck stays in frame
TRUCK_FRONT = -0.6 - (TRAILER + 3.6) * TRUCK
BLUE, NAVY, ORANGE, YELLOW = "#2A5FA8", "#1E3E6E", "#FF6A13", "#FFC20E"
KRAFT, WHITE = "#D9A866", "#EEF1F4"

# ground: grass, yard asphalt with truck bays in front of the docks
aabb("ground", "#A9CC6E", -120, -120, -0.3, 200, 160, -0.05, mat="flat", nolines=True)
aabb("ground", "#9AA4B1", -40, -34, -0.1, 104, 0, 0.0, mat="asphalt", nolines=True)
aabb("ground", "#9AA4B1", X1, 0, -0.1, 104, 40, 0.0, mat="asphalt", nolines=True)
aabb("ground", "#9AA4B1", -40, 0, -0.1, 0, 40, 0.0, mat="asphalt", nolines=True)
for dx in (DX_IN, DX_OUT):
    for x in (dx - 3.2, dx + 3.2):
        aabb("ground", "#F4F5F7", x - 0.08, TRUCK_FRONT - 2, 0.0, x + 0.08, -0.6, 0.02, nolines=True)
aabb("ground", "#E7E1D2", -40, -34.6, 0.0, 104, -34.0, 0.15)


def tree(x, y, h):
    cyl("trees", "#F3EFE6", (x, y, h * 0.3), 0.3, h * 0.6, seg=8)
    col = random.choice(["#F2C230", "#F0A32A", "#E8892B", "#9BC255", "#F5D046", "#7FB04A"])
    for dx, dy, dz, r in ((0, 0, 0.7, 0.30), (0.2, -0.1, 0.55, 0.22), (-0.18, 0.12, 0.57, 0.21)):
        ball("trees", col, (x + dx * h, y + dy * h, h * dz), h * r, sz=1.15)


for k in range(500):
    x, y = random.uniform(-110, 190), random.uniform(-110, 150)
    if -44 < x < 108 and -38 < y < 44:
        continue
    tree(x, y, random.uniform(8, 12))

# ---- building shell: slab, back and right walls full height, front/left cut ----
aabb("shell", "#C9D2DC", X0 - 0.4, Y0 - 0.4, 0, X1 + 0.4, Y1 + 0.4, FZ - 0.02)
aabb("floor", "#D6DEE7", X0, Y0, FZ - 0.05, X1, Y1, FZ, mat="floor", nolines=True)
# back wall (y = Y1) and right wall (x = X1): cream panels, blue columns, windows
aabb("shell", "#F1E9D8", X0 - 0.4, Y1, FZ, X1 + 0.4, Y1 + 0.4, WALL)
DOOR_Z = FZ + 6.4
aabb("shell", "#F1E9D8", X1, Y0 - 0.4, FZ, X1 + 0.4, Y1 + 0.4, WALL)
aabb("shell", BLUE, X0 - 0.4, Y1 - 0.05, FZ, X1, Y1, FZ + 1.0)
aabb("shell", BLUE, X1 - 0.05, Y0, FZ, X1, Y1, FZ + 1.0)
aabb("shell", BLUE, X0 - 0.5, Y1 - 0.1, WALL - 0.5, X1 + 0.5, Y1 + 0.5, WALL)
aabb("shell", BLUE, X1 - 0.1, Y0 - 0.5, WALL - 0.5, X1 + 0.5, Y1 + 0.5, WALL)
for x in range(0, int(X1) + 1, 8):
    aabb("shell", BLUE, x - 0.3, Y1 - 0.35, FZ, x + 0.3, Y1, WALL - 0.5)
for y in range(0, int(Y1) + 1, 8):
    aabb("shell", BLUE, X1 - 0.35, y - 0.3, FZ, X1, y + 0.3, WALL - 0.5)
for x in range(0, int(X1) - 4, 8):
    aabb("shell", "#FFFFFF", x + 1.2, Y1 - 0.12, FZ + 3.6, x + 6.8, Y1 - 0.02, FZ + 7.0)
    aabb("shell", "#7FB3E0", x + 1.4, Y1 - 0.16, FZ + 3.8, x + 6.6, Y1 - 0.1, FZ + 6.8, mat="glass")
    aabb("shell", "#FFFFFF", x + 3.95, Y1 - 0.2, FZ + 3.8, x + 4.05, Y1 - 0.12, FZ + 6.8)
for y in range(8, int(Y1) - 6, 8):
    aabb("shell", "#FFFFFF", X1 - 0.12, y + 1.2, FZ + 3.6, X1 - 0.02, y + 6.8, FZ + 7.0)
    aabb("shell", "#7FB3E0", X1 - 0.16, y + 1.4, FZ + 3.8, X1 - 0.1, y + 6.6, FZ + 6.8, mat="glass")
# left wall and front wall cut low (section cap); two dock doors in the front wall
CUT = FZ + 1.3
aabb("shell", "#F1E9D8", X0 - 0.4, Y0 - 0.4, FZ, X0, Y1 + 0.4, CUT)
aabb("shell", "#DCE2E8", X0 - 0.45, Y0 - 0.45, CUT, X0 + 0.05, Y1 + 0.45, CUT + 0.08)
for a, b in ((X0 - 0.4, DX_IN - DOOR), (DX_IN + DOOR, DX_OUT - DOOR), (DX_OUT + DOOR, X1 + 0.4)):
    aabb("shell", "#F1E9D8", a, Y0 - 0.4, FZ, b, Y0, CUT)
    aabb("shell", "#DCE2E8", a - 0.05, Y0 - 0.45, CUT, b + 0.05, Y0 + 0.05, CUT + 0.08)
for dx in (DX_IN, DX_OUT):
    # dock leveller plate, hazard edge, rubber bumpers, dark door posts
    aabb("shell", "#5E6875", dx - DOOR + 0.2, Y0 - 0.4, FZ - 0.04, dx + DOOR - 0.2, Y0 + 0.9, FZ + 0.02)
    for k in range(round((DOOR - 0.2) * 5)):
        aabb("shell", YELLOW if k % 2 else "#2B2F36", dx - DOOR + 0.2 + k * 0.4, Y0 - 0.45, FZ - 0.05, dx - DOOR + 0.6 + k * 0.4, Y0 - 0.25, FZ + 0.03, nolines=True)
    for ddx in (0.3 - DOOR, DOOR - 0.3):
        aabb("shell", "#2B2F36", dx + ddx - 0.25, Y0 - 0.75, 0.5, dx + ddx + 0.25, Y0 - 0.4, 1.1)
    for ddx in (-DOOR, DOOR - 0.3):
        aabb("shell", "#2E3742", dx + ddx, Y0 - 0.4, FZ, dx + ddx + 0.3, Y0 + 0.05, CUT + 0.3)


def chevron(p, u, col=ORANGE):
    u = Vector(u).normalized()
    n_ = Vector((-u.y, u.x))
    for a in (-1, 1):
        q = Vector(p) + n_ * a * 1.0
        beam("floor", col, (q.x, q.y, FZ + 0.01), (p[0] + u.x * 0.9, p[1] + u.y * 0.9, FZ + 0.01), 0.32, 0.02, nolines=True)


# the lane: a painted U from the receiving door, along the racks, to the dispatch door
LX0, LX1 = DX_IN - 1.8, DX_OUT + 1.8
aabb("floor", "#C3CEDA", LX0, LANE0, FZ, LX1, LANE1, FZ + 0.006, mat="flat", nolines=True)
for dx in (DX_IN, DX_OUT):
    aabb("floor", "#C3CEDA", dx - 1.8, Y0, FZ, dx + 1.8, LANE0, FZ + 0.006, mat="flat", nolines=True)
    for x in (dx - 1.8, dx + 1.58):
        aabb("floor", YELLOW, x, Y0, FZ, x + 0.22, LANE1 if (x < dx) == (dx == DX_IN) else LANE0, FZ + 0.012, mat="flat", nolines=True)
aabb("floor", YELLOW, LX0, LANE1 - 0.22, FZ, LX1, LANE1, FZ + 0.012, mat="flat", nolines=True)
aabb("floor", YELLOW, DX_IN + 1.58, LANE0, FZ, DX_OUT - 1.58, LANE0 + 0.22, FZ + 0.012, mat="flat", nolines=True)
for y in (2.0, 5.0):
    chevron((DX_IN, y), (0, 1))
    chevron((DX_OUT, LANE0 + 0.8 - y), (0, -1))
for k in range(int((DX_OUT - DX_IN - 4) // 4)):
    chevron((DX_IN + 3.0 + k * 4.0, LANE_C), (1, 0))
# zone floor markings
for (x0, y0, x1, y1) in P["ZONES"]:
    for (a, b, c_, d) in ((x0, y0, x1, y0 + 0.18), (x0, y1 - 0.18, x1, y1), (x0, y0, x0 + 0.18, y1), (x1 - 0.18, y0, x1, y1)):
        aabb("floor", YELLOW, a, b, FZ, c_, d, FZ + 0.012, mat="flat", nolines=True)

# ---- zone sign gantries (text added below as geometry) ---------------------------
SIGNS = {"ПРИЁМКА": (P["SIGNS"][0], BLUE), "ОТГРУЗКА": (P["SIGNS"][1], ORANGE)}
SW = P["SIGN_W"]
SIGN_Y, SIGN_Z0, SIGN_Z1 = LANE0 - 0.25, FZ + 2.7, FZ + 4.1  # low boards at the back of each zone: they never hide the rack fronts
for label, (cx, col) in SIGNS.items():
    for dx in (-SW - 0.1, SW + 0.1):
        aabb("signs", NAVY, cx + dx - 0.12, SIGN_Y - 0.12, FZ, cx + dx + 0.12, SIGN_Y + 0.12, SIGN_Z1)
    aabb("signs", col, cx - SW, SIGN_Y - 0.1, SIGN_Z0, cx + SW, SIGN_Y + 0.1, SIGN_Z1)
    aabb("signs", "#FFFFFF", cx - SW + 0.2, SIGN_Y - 0.13, SIGN_Z0 + 0.12, cx + SW - 0.2, SIGN_Y - 0.1, SIGN_Z0 + 0.16, nolines=True)
    text("signs_text", label, (cx, SIGN_Y - 0.14, (SIGN_Z0 + SIGN_Z1) / 2 + 0.06), min(1.0, SW * 0.34), "#FFFFFF")


# ---- racks ------------------------------------------------------------------------
LEVELS = [FZ + 0.15, FZ + 1.75, FZ + 3.35]
RACK_TOP = FZ + 4.9


def carton(group, x0, y0, z0, x1, y1, z1, col=KRAFT, tape=True):
    aabb(group, col, x0, y0, z0, x1, y1, z1)
    if tape and col == KRAFT:
        xm = (x0 + x1) / 2
        aabb(group, "#C08E4E", xm - 0.08, y0 - 0.01, z1 - 0.01, xm + 0.08, y1 + 0.01, z1 + 0.01, nolines=True)


def pallet(group, x, y, z, w=1.2, d=1.2):
    aabb(group, "#C79A5B", x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + 0.15)


def bay_load(group, x0, x1, y0, y1, z, rng, empty=0.0):
    """Pallets of cartons on one rack level (x0..x1 across the row, y0..y1 along it)."""
    n = max(1, round((y1 - y0) / 1.35))
    step = (y1 - y0) / n
    for k in range(n):
        if rng.random() < empty:
            continue
        yc = y0 + step * (k + 0.5)
        xc = (x0 + x1) / 2
        pallet(group, xc, yc, z, w=x1 - x0 - 0.2, d=step - 0.2)
        kind = rng.random()
        h = rng.choice((0.9, 1.05, 1.2))
        if kind < 0.6:
            for i in (0, 1):
                for j in (0, 1):
                    carton(group, xc - (x1 - x0) / 2 + 0.15 + i * (x1 - x0 - 0.3) / 2, yc - step / 2 + 0.15 + j * (step - 0.3) / 2, z + 0.15,
                           xc - (x1 - x0) / 2 + 0.12 + (i + 1) * (x1 - x0 - 0.3) / 2, yc - step / 2 + 0.12 + (j + 1) * (step - 0.3) / 2, z + 0.15 + h)
        elif kind < 0.82:
            carton(group, xc - (x1 - x0) / 2 + 0.15, yc - step / 2 + 0.15, z + 0.15, xc + (x1 - x0) / 2 - 0.15, yc + step / 2 - 0.15, z + 0.15 + h, col=WHITE)
        else:
            for j in range(3):
                aabb(group, BLUE, xc - (x1 - x0) / 2 + 0.15, yc - step / 2 + 0.15 + j * (step - 0.3) / 3, z + 0.15,
                     xc + (x1 - x0) / 2 - 0.15, yc - step / 2 + 0.1 + (j + 1) * (step - 0.3) / 3, z + 0.15 + 0.7)


def rack_row(group, x0, x1, y0, y1, levels=LEVELS, top=RACK_TOP, seed=0, empty=0.0):
    rng = random.Random(seed)
    nb = max(1, round((y1 - y0) / 2.8))
    ys = [y0 + (y1 - y0) * k / nb for k in range(nb + 1)]
    for y in ys:
        for x in (x0, x1):
            aabb(group, BLUE, x - 0.09 if x == x0 else x - 0.18, y - 0.09, FZ, x + 0.18 if x == x0 else x + 0.09, y + 0.09, top)
        aabb(group, BLUE, x0, y - 0.04, FZ + 0.3, x1, y + 0.04, FZ + 0.4, nolines=True)
    for z in levels[1:]:
        for x in (x0 + 0.05, x1 - 0.05):
            aabb(group, ORANGE, x - 0.07, y0, z - 0.22, x + 0.07, y1, z)
    for z in levels:
        for a, b in zip(ys, ys[1:]):
            bay_load(group, x0 + 0.1, x1 - 0.1, a + 0.1, b - 0.1, z, rng, empty)


# Alphabet reads left to right like a page: А–Б by receiving … Ю–Я at dispatch.
# P["RX"] lists the physical rows right to left; rows run into the building,
# pairs stand back to back, plaques on the front ends.
RY0, RY1 = P["RY"]
RW = 2.6
RANGES = [  # label, letters, x0 of row
    ("А–Б", "АБ", P["RX"][5]), ("В–К", "ВГДЕЁЖЗИЙК", P["RX"][4]),
    ("Л–М", "ЛМ", P["RX"][3]), ("Н–У", "НОПРСТУ", P["RX"][2]),
    ("Ф–Э", "ФХЦЧШЩЪЫЬЭ", P["RX"][1]), ("Ю–Я", "ЮЯ", P["RX"][0]),
]
PLAQUE_Z0, PLAQUE_Z1 = RACK_TOP + 0.2, RACK_TOP + 2.4
for i, (label, letters, x0) in enumerate(RANGES):
    rack_row(f"rack_{i}", x0, x0 + RW, RY0, RY1, seed=10 + P["RX"].index(x0))  # seed per physical row
    cx = x0 + RW / 2
    aabb(f"rack_{i}", NAVY, cx - 0.08, RY0 - 0.05, RACK_TOP - 0.2, cx + 0.08, RY0 + 0.1, PLAQUE_Z0)
    aabb(f"rack_{i}", "#FFFFFF", x0 + 0.06, RY0 - 0.12, PLAQUE_Z0, x0 + RW - 0.06, RY0 + 0.0, PLAQUE_Z1)
    aabb(f"rack_{i}", BLUE, x0 + 0.06, RY0 - 0.14, PLAQUE_Z0, x0 + RW - 0.06, RY0 - 0.1, PLAQUE_Z0 + 0.14, nolines=True)
    text("plaques", label, (cx, RY0 - 0.16, (PLAQUE_Z0 + PLAQUE_Z1) / 2 + 0.08), 1.05, NAVY)

# Free cells right by receiving: a short, half-empty rack facing the dock.
EX0, EX1, EY0, EY1 = P["ENTR"]
ELEV = LEVELS[:3]
rng = random.Random(7)
nb = max(3, round((EX1 - EX0) / 1.25))
eys = [EX0 + (EX1 - EX0) * k / nb for k in range(nb + 1)]
for x in eys:
    for y in (EY0, EY1):
        aabb("entrance_rack", BLUE, x - 0.09, y - 0.09, FZ, x + 0.09, y + 0.09, FZ + 4.6)
for z in ELEV[1:]:
    for y in (EY0 + 0.05, EY1 - 0.05):
        aabb("entrance_rack", ORANGE, EX0, y - 0.07, z - 0.22, EX1, y + 0.07, z)
FREE_CELL = None
for li, z in enumerate(ELEV):
    for k, (a, b) in enumerate(zip(eys, eys[1:])):
        if (li, k) in ((0, 1), (1, 3), (2, 0), (1, 1)):
            # free cell: yellow outline on the beam front
            aabb("entrance_rack", YELLOW, a + 0.2, EY0 - 0.12, z + 0.02, b - 0.2, EY0 - 0.06, z + 0.1, nolines=True)
            if (li, k) == (0, 1):
                FREE_CELL = ((a + b) / 2, (EY0 + EY1) / 2, z + 0.15)
            continue
        xc = (a + b) / 2
        pallet("entrance_rack", xc, (EY0 + EY1) / 2, z, w=b - a - 0.3, d=EY1 - EY0 - 0.2)
        carton("entrance_rack", a + 0.3, EY0 + 0.2, z + 0.15, b - 0.3, EY1 - 0.2, z + 0.15 + rng.choice((0.9, 1.1)), col=rng.choice((KRAFT, KRAFT, WHITE)))


# ---- trucks ----------------------------------------------------------------------
TRUCK_BLUE = "#1E63D0"


def truck(group, dx, logo=None):
    """The scene-2 truck: blue cab-over tractor (flat front, black grille, roof
    deflector, mirrors, silver tanks) and a white ribbed trailer with a blue base
    rail and corner posts on three axles. Rear against the front-wall dock at
    x = dx, nose towards the camera (-y)."""
    M = Matrix.Translation((dx, Y0 - 0.6, 0)) @ Matrix.Diagonal((TRUCK, TRUCK, TRUCK, 1))
    L = TRAILER
    aabb(group, "#3A414B", -0.8, -L - 3.4, 0.75, 0.8, -0.2, 1.05, M=M)  # chassis
    # trailer
    aabb(group, "#F4F6F8", -1.3, -L, 1.1, 1.3, 0.0, 4.4, M=M)
    for s_ in (-1, 1):
        aabb(group, TRUCK_BLUE, s_ * 1.3 - 0.04, -L, 1.05, s_ * 1.3 + 0.04, 0.0, 1.38, M=M)  # base rail
        for y in (-L, -0.15):
            aabb(group, TRUCK_BLUE, s_ * 1.3 - 0.05, y, 1.05, s_ * 1.3 + 0.05, y + 0.15, 4.4, M=M)  # corner posts
        k = 1
        while -L + k * 0.85 < -0.3:  # ribs
            aabb(group, "#DDE3EA", s_ * 1.31 - 0.02, -L + k * 0.85 - 0.04, 1.4, s_ * 1.31 + 0.02, -L + k * 0.85 + 0.04, 4.3, nolines=True, M=M)
            k += 1
    aabb(group, "#DDE3EA", -1.25, -L - 0.03, 1.4, 1.25, -L, 4.35, nolines=True, M=M)
    for s_ in (-1, 1):
        aabb(group, "#3A414B", s_ * 0.7 - 0.06, -L + 1.6, 0.25, s_ * 0.7 + 0.06, -L + 1.75, 1.1, M=M)  # landing legs
    for yy in (-3.6, -2.45, -1.3):
        for s_ in (-1, 1):
            cyl(group, "#2B2F36", (s_ * 1.0, yy, 0.5), 0.5, 0.5, axis="X", seg=16, M=M)
            cyl(group, "#C9D0D8", (s_ * 1.26, yy, 0.5), 0.22, 0.03, axis="X", seg=12, M=M)
    # tractor
    cy0, cy1 = -L - 3.45, -L - 1.25  # cab front / back
    aabb(group, TRUCK_BLUE, -1.25, cy0, 1.0, 1.25, cy1, 3.75, M=M)
    beam(group, TRUCK_BLUE, (0, cy0 + 0.5, 3.7), (0, cy1 + 0.25, 4.3), 2.3, 0.3, M=M)  # roof deflector
    aabb(group, TRUCK_BLUE, -1.1, cy1, 3.45, 1.1, cy1 + 0.4, 4.3, M=M)
    aabb(group, "#5A8CC4", -1.12, cy0 - 0.04, 2.45, 1.12, cy0 + 0.02, 3.45, mat="glass", M=M)  # windscreen
    aabb(group, "#22272E", -0.85, cy0 - 0.05, 1.35, 0.85, cy0 + 0.02, 2.25, M=M)  # grille
    for z in (1.6, 1.95):
        aabb(group, "#4A525C", -0.8, cy0 - 0.07, z, 0.8, cy0 - 0.04, z + 0.06, nolines=True, M=M)
    aabb(group, "#D7DDE4", -1.28, cy0 - 0.12, 0.7, 1.28, cy0 + 0.3, 1.15, M=M)  # bumper
    for s_ in (-1, 1):
        aabb(group, "#FFFFFF", s_ * 1.0 - 0.2, cy0 - 0.08, 1.2, s_ * 1.0 + 0.2, cy0 - 0.02, 1.45, mat="flat", M=M)  # headlights
        aabb(group, "#5A8CC4", s_ * 1.25 - 0.03, cy0 + 0.25, 2.45, s_ * 1.25 + 0.03, cy0 + 1.2, 3.4, mat="glass", M=M)  # side windows
        aabb(group, "#22272E", s_ * 1.45 - 0.06, cy0 + 0.15, 2.5, s_ * 1.45 + 0.06, cy0 + 0.35, 3.3, M=M)  # mirrors
        beam(group, "#22272E", (s_ * 1.25, cy0 + 0.3, 3.3), (s_ * 1.45, cy0 + 0.25, 3.25), 0.05, M=M)
        cyl(group, "#C9D0D8", (s_ * 1.0, cy1 + 0.75, 0.75), 0.32, 1.1, axis="Y", seg=16, M=M)  # fuel tanks
        aabb(group, "#22272E", s_ * 1.25 - 0.03, cy0 + 1.4, 1.0, s_ * 1.25 + 0.03, cy0 + 1.5, 2.6, nolines=True, M=M)  # door line
        for yy in (cy0 + 0.9, -L + 0.5):
            cyl(group, "#2B2F36", (s_ * 1.05, yy, 0.55), 0.55, 0.45, axis="X", seg=16, M=M)
            cyl(group, "#C9D0D8", (s_ * 1.29, yy, 0.55), 0.25, 0.03, axis="X", seg=12, M=M)
    if logo:  # on the roof deflector, which faces the camera
        t = math.atan2(0.6, cy1 - cy0 - 0.25)  # deflector slope
        p = M @ Vector((0, (cy0 + 0.5 + cy1 + 0.25) / 2 - 0.17 * math.sin(t), 4.0 + 0.17 * math.cos(t)))
        text(group + "_text", logo, tuple(p), 0.36 * TRUCK, "#FFFFFF", rot=(t, 0, 0))


GIFT_SIZE = 1.8


def gift(group, x, y, z, k=GIFT_SIZE, on_pallet=True):
    if on_pallet:
        aabb(group, "#C79A5B", x - 0.75 * k, y - 0.75 * k, z, x + 0.75 * k, y + 0.75 * k, z + 0.15)
        z += 0.15
    h = 0.85 * k
    aabb(group, "#E2B977", x - 0.55 * k, y - 0.55 * k, z, x + 0.55 * k, y + 0.55 * k, z + h)
    aabb(group, "#D62B2B", x - 0.1 * k, y - 0.57 * k, z, x + 0.1 * k, y + 0.57 * k, z + h + 0.02)
    aabb(group, "#D62B2B", x - 0.57 * k, y - 0.1 * k, z, x + 0.57 * k, y + 0.1 * k, z + h + 0.02)
    for a in (0.6, -0.6, math.pi - 0.6, math.pi + 0.6):
        ball(group, "#E53935", (x + 0.22 * k * math.cos(a), y + 0.22 * k * math.sin(a), z + h + 0.09 * k), 0.2 * k, sx=1.0, sy=0.55, sz=0.5)
    ball(group, "#B71C1C", (x, y, z + h + 0.06 * k), 0.1 * k)
    return Vector((x, y, z + h + 0.2 * k))


# our truck backed into receiving dock 1, the gift just rolled off it
truck("our_truck", DX_IN, logo="ЭНЕРГИЯ+")
truck("trucks", DX_OUT, logo="ЭНЕРГИЯ+")
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


def to_cam():
    return math.radians(-90 - 30)  # local +x points towards the camera side


# receiving: worker with a pallet jack under the gift, another scanning
jack = Vector((GIFT_IN.x + 1.6, GIFT_IN.y, FZ))
aabb("jack", "#E8892B", jack.x - 0.2, jack.y - 0.3, FZ + 0.05, jack.x + 0.3, jack.y + 0.3, FZ + 0.25)
beam("jack", "#3A414B", (jack.x + 0.2, jack.y, FZ + 0.25), (jack.x + 1.0, jack.y, FZ + 1.2), 0.08)
person("workers", (jack.x + 1.5, jack.y - 0.1, FZ), math.radians(180), pose=(0.3, 0.25))
person("workers", (*P["SCAN_IN"], FZ), math.radians(-160), tsd=True, pose=((0, 0), (0.25, 0.35)))
for k, (x, y) in enumerate(P["STAGE_IN"]):
    pallet("staging_in", x, y, FZ)
    carton("staging_in", x - 0.5, y - 0.5, FZ + 0.15, x + 0.5, y + 0.5, FZ + 1.1)
    if k:
        carton("staging_in", x - 0.4, y - 0.4, FZ + 1.1, x + 0.4, y + 0.4, FZ + 1.7, col=WHITE)

# dispatch: the barge consignment staged by the Ю–Я racks, worker scanning
BARGE_PALLETS = P["BARGE"]
for x, y in BARGE_PALLETS:
    pallet("staging_out", x, y, FZ, 1.5, 1.5)
    aabb("staging_out", "#CFE3F2", x - 0.65, y - 0.65, FZ + 0.15, x + 0.65, y + 0.65, FZ + 1.6)
    aabb("staging_out", "#E9F2F9", x - 0.66, y - 0.2, FZ + 0.3, x + 0.66, y + 0.2, FZ + 1.45, nolines=True)
person("workers", (*P["SCAN_OUT"], FZ), math.radians(-120), tsd=True, pose=((0, 0), (0.25, 0.35)))

# keeper Pavel: grey hair and moustache, cap-less, clipboard, by the dispatch rows
KEEPER = Vector((*P["KEEPER"], FZ))
KEEPER_HEAD = person("keeper", tuple(KEEPER), math.radians(-115), hat=None, vest="#F7B731", suit="#3D5A80", hair="#C9CDD2", mustache="#C9CDD2", pose=((0.15, 0.3), (0.05, 0.0)))
aabb("keeper", "#7A5230", KEEPER.x - 0.05 - 0.35, KEEPER.y - 0.75, FZ + 1.6, KEEPER.x + 0.25 - 0.35, KEEPER.y - 0.35, FZ + 2.05)
LX, LY = KEEPER.x - 1.4, KEEPER.y - 0.3
aabb("keeper", "#8A5A33", LX - 0.55, LY - 0.4, FZ, LX + 0.55, LY + 0.4, FZ + 1.5)
aabb("keeper", "#F4EBD6", LX - 0.5, LY - 0.36, FZ + 1.5, LX + 0.5, LY + 0.36, FZ + 1.58)
aabb("keeper", "#B23A3A", LX - 0.04, LY - 0.38, FZ + 1.5, LX + 0.04, LY + 0.38, FZ + 1.6, nolines=True)

# WMS kiosk at the dispatch zone: screen with the warehouse map, hot zone lit
KX, KY = P["KIOSK"]
WK = 1.5  # kiosk scale: it is a choice on the map, so it must read at phone size
def kbox(col, x0, y0, z0, x1, y1, z1, **kw):
    aabb("wms", col, KX + x0 * WK, KY + y0 * WK, FZ + z0 * WK, KX + x1 * WK, KY + y1 * WK, FZ + z1 * WK, **kw)
kbox("#3A414B", -0.6, -0.4, 0, 0.6, 0.4, 0.1)
kbox("#E9EDF1", -0.25, -0.15, 0.1, 0.25, 0.15, 1.2)
kbox(BLUE, -0.4, -0.3, 1.0, 0.4, 0.3, 1.15)
SCREEN = (KX - 1.0 * WK, KY - 0.12 * WK, FZ + 1.25 * WK, KX + 1.0 * WK, KY, FZ + 2.55 * WK)
aabb("wms", "#24303F", SCREEN[0] - 0.12, SCREEN[1], SCREEN[2] - 0.12, SCREEN[3] + 0.12, SCREEN[4] + 0.12, SCREEN[5] + 0.12)
aabb("wms", "#16324F", SCREEN[0], SCREEN[1] - 0.03, SCREEN[2], SCREEN[3], SCREEN[1], SCREEN[5], mat="flat", nolines=True)
SW_ = (SCREEN[3] - SCREEN[0]) / 7.4
for i in range(6):  # rack rows on the map, right-most (by dispatch) glowing green
    x = SCREEN[0] + SW_ * (0.75 + i * 1.0)
    aabb("wms", "#5FD38D" if i == 5 else "#7FD0F5", x, SCREEN[1] - 0.05, SCREEN[2] + 0.35, x + SW_ * 0.55, SCREEN[1] - 0.03, SCREEN[5] - 0.45, mat="flat", nolines=True)
aabb("wms", "#FF6A13", SCREEN[0] + 0.3, SCREEN[1] - 0.05, SCREEN[2] + 0.1, SCREEN[3] - 0.3, SCREEN[1] - 0.03, SCREEN[2] + 0.22, mat="flat", nolines=True)


# driverless forklift in the lane
def forklift(group, x, y, facing, load=True):
    M = Matrix.Translation((x, y, FZ)) @ Matrix.Rotation(facing, 4, "Z")
    aabb(group, ORANGE, -1.2, -0.7, 0.3, 0.6, 0.7, 1.5, M=M)
    aabb(group, "#3A414B", -1.3, -0.72, 0.3, -0.8, 0.72, 1.6, M=M)
    aabb(group, "#2B2F36", 0.6, -0.55, 0.1, 0.8, 0.55, 3.2, M=M)
    for dy in (-0.35, 0.35):
        aabb(group, "#2B2F36", 0.8, dy - 0.07, 0.1, 2.0, dy + 0.07, 0.2, M=M)
    for dx, dy in ((-0.8, -0.72), (-0.8, 0.72), (0.3, -0.72), (0.3, 0.72)):
        cyl(group, "#2B2F36", (dx, dy, 0.32), 0.32, 0.28, axis="Y", seg=14, M=M)
    cyl(group, "#2B2F36", (-0.3, 0, 1.65), 0.2, 0.3, seg=12, M=M)  # lidar
    cyl(group, "#7FD0F5", (-0.3, 0, 1.85), 0.12, 0.12, seg=10, mat="flat", M=M)
    cyl(group, YELLOW, (-1.0, 0, 1.75), 0.1, 0.5, seg=10, M=M)
    if load:
        aabb(group, "#C79A5B", 0.9, -0.6, 0.2, 2.1, 0.6, 0.35, M=M)
        aabb(group, KRAFT, 0.95, -0.55, 0.35, 2.05, 0.55, 1.35, M=M)



# ---- outcome-only figures (group names start with o_) ------------------------------
# entrance: the gift sits in the free cell by receiving
O_GIFT_ENTRANCE = gift("o_gift_entrance", FREE_CELL[0], FREE_CELL[1], FREE_CELL[2], k=1.25, on_pallet=False)
# alphabet: the gift on the bottom level at the front of its letter row
ALPHA_ROW = {"camera": 4, "socks": 3, "boat": 2}
O_GIFT_ALPHA = {}
for parcel, i in ALPHA_ROW.items():
    x0 = RANGES[i][2]
    O_GIFT_ALPHA[parcel] = gift(f"o_gift_{parcel}", x0 + RW / 2, RY0 + 0.9, LEVELS[0] + 0.15, k=1.25, on_pallet=False)
# keeper / wms: the gift in the hot zone, front of the right row by dispatch
O_GIFT_HOT = gift("o_gift_hot", *P["HOT"], FZ, k=1.25)
# dashed walking routes on the floor (orange), from the barge pallets to the gift


RED, GREEN = "#E8402A", "#2FB86A"


def dashes(group, pts, col=RED, w=0.7, dash=1.2, gap=0.8):
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        d = (b - a)
        n = int(d.length // (dash + gap))
        for k in range(n + 1):
            p0 = a + d.normalized() * k * (dash + gap)
            p1 = a + d.normalized() * min(d.length, k * (dash + gap) + dash)
            if (p1 - p0).length < 0.05:
                continue
            beam(group, col, (p0.x, p0.y, FZ + 0.02), (p1.x, p1.y, FZ + 0.02), w, 0.03, nolines=True)
    # arrowhead at the end, painted like the lane chevrons
    a, b = Vector(pts[-2]), Vector(pts[-1])
    u = (b - a).normalized()
    n_ = Vector((-u.y, u.x))
    for sgn in (-1, 1):
        q = b - u * 1.3 + n_ * sgn * 1.1
        beam(group, col, (q.x, q.y, FZ + 0.025), (b.x + u.x * 0.25, b.y + u.y * 0.25, FZ + 0.025), w, 0.03, nolines=True)


DOCK_OUT = [(DX_OUT, LANE_C), (DX_OUT, Y0 + 0.8)]  # every route ends in the dispatch truck
ROUTES = {"entrance": [(FREE_CELL[0], EY1 + 0.5), (FREE_CELL[0], LANE_C)] + DOCK_OUT,
          **{p: [(RANGES[i][2] + RW / 2, RY0 - 0.6), (RANGES[i][2] + RW / 2, LANE_C)] + DOCK_OUT for p, i in ALPHA_ROW.items()},
          "hot": P["HOT_VIA"] + DOCK_OUT}
ROUTE_M = {k: round(sum((Vector(b) - Vector(a)).length for a, b in zip(v, v[1:]))) for k, v in ROUTES.items()}
print("ROUTE_M", ROUTE_M)


def route_label(group, pts, col):
    """Distance painted on the floor beside the longest run of the route."""
    segs = list(zip(pts, pts[1:]))[:-1]  # the last leg runs behind the dispatch truck
    a, b = max(segs, key=lambda s_: (Vector(s_[1]) - Vector(s_[0])).length)
    m = ROUTE_M[group.removeprefix("o_route_")]
    x = (a[0] + b[0]) / 2
    for sx in P["SIGNS"]:  # keep the number clear of the zone signs (the raised board hides floor to its right)
        lo, hi = sx - P["SIGN_W"] / 2 - 1.8, sx + P["SIGN_W"] / 2 + 3.0
        if lo < x < hi:
            x = lo if x - lo < hi - x else hi
    # front half of the lane; runners walk the back half so they never cover the number
    # the hot route hugs the dispatch wall: its number goes on the wall side, clear of the forklift
    at = (x, LANE0 + 0.6) if abs(a[1] - b[1]) < 0.1 else (x + 2.2, (a[1] + b[1]) / 2)
    text(group + "_text", f"{m} м", (*at, FZ + 0.04), 1.5, col, rot=(0, 0, 0))


dashes("o_route_entrance", ROUTES["entrance"])
route_label("o_route_entrance", ROUTES["entrance"], RED)
for parcel, i in ALPHA_ROW.items():
    dashes(f"o_route_{parcel}", ROUTES[parcel])
    route_label(f"o_route_{parcel}", ROUTES[parcel], RED)
dashes("o_route_hot", ROUTES["hot"], col=GREEN)
route_label("o_route_hot", ROUTES["hot"], GREEN)
# runners carrying boxes on the long routes
person("o_runners_entrance", (*P["RUN_E"][0], FZ), math.radians(180), walk=0.35, pose=((0.35, 0.35), (0.35, 0.35)))
carton("o_runners_entrance", P["RUN_E"][0][0] - 1.0, P["RUN_E"][0][1] - 0.3, FZ + 1.6, P["RUN_E"][0][0] - 0.3, P["RUN_E"][0][1] + 0.3, FZ + 2.2)
person("o_runners_entrance", (*P["RUN_E"][1], FZ), math.radians(0), walk=-0.35)
for parcel, i in ALPHA_ROW.items():
    x = RANGES[i][2] + RW / 2
    person(f"o_runners_{parcel}", (x + 2.6, LANE_C + 0.6, FZ), math.radians(170), walk=0.35, pose=((0.35, 0.35), (0.35, 0.35)))
    person(f"o_runners_{parcel}", (x + 5.4, LANE_C + 1.1, FZ), math.radians(-10), walk=-0.35, tsd=True, pose=((0, 0), (0.25, 0.35)))
# keeper outcome: Pavel has left; two new-shift workers puzzled by the racks
O_PUZZLED = [Vector((x, y, FZ)) for x, y in P["PUZZLED"]]
O_HEADS = []
for k, p in enumerate(O_PUZZLED):
    head = person("o_newshift", tuple(p), math.radians(-60 - 70 * k), hat="#5FD38D", tsd=True, pose=((0.05, 0.75), (0.25, 0.35)))
    O_HEADS.append(head)
    text("o_newshift_text", "?", (head.x, head.y - 0.1, head.z + 0.75), 1.1, ORANGE, rot=(math.pi / 2, 0, -math.radians(30)))
# wms outcome: forklift takes the gift straight onto the first truck
FX = DX_OUT - 3.6  # right of the dispatch sign, so the board never covers it
forklift("o_agv_hot", FX, LANE_C, 0, load=False)
aabb("o_agv_hot", "#C79A5B", FX + 0.9, LANE_C - 0.6, FZ + 0.2, FX + 2.1, LANE_C + 0.6, FZ + 0.35)
O_GIFT_FORK = gift("o_gift_fork", FX + 1.5, LANE_C, FZ + 0.35, k=1.0, on_pallet=False)
# Story overlay for the outcome stills (drawn by v10/compose.py): the gift to
# spotlight and the floor path it travels (or is searched along).
f3 = lambda pts: [Vector((x, y, FZ + 0.05)) for x, y in pts]
PX = O_PUZZLED[0]
STORY = {
    "entrance": (O_GIFT_ENTRANCE, f3(ROUTES["entrance"])),
    **{f"alphabet-{p}": (O_GIFT_ALPHA[p], f3(ROUTES[p])) for p in ALPHA_ROW},
    "keeper": (O_GIFT_HOT, f3([(PX.x, PX.y), (PX.x - 3, RY0 - 1.6), (PX.x - 9, RY0 - 1.2), (PX.x - 11, LANE1), (PX.x - 4, LANE_C), (PX.x + 1, LANE1 + 0.6), (P["HOT"][0] - 1.0, P["HOT"][1] - 0.8)])),
    "wms": (O_GIFT_FORK, f3(ROUTES["hot"])),
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
    "desk": ((1536, 1024), float(os.environ.get("DESK_AZ", -12)), float(os.environ.get("DESK_EL", 50)), (0.0, 0.02, 1.0, 0.99)),
    "tall": ((1024, 1536), float(os.environ.get("TALL_AZ", -10)), float(os.environ.get("TALL_EL", 54)), (0.0, 0.08, 1.0, 0.99)),
}
OUTCOME_RES = (1960, 840)


def axes(az, el):
    rot = (math.radians(90 - el), 0, math.radians(az))
    m = Euler(rot, "XYZ").to_matrix()
    return rot, m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0)), m @ Vector((0, 0, -1))


def cube(x0, y0, z0, x1, y1, z1):
    return [Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


BUILDING = [Vector(p) for p in (
    (X0 - 0.4, Y0 - 0.4, 0), (X1 + 0.4, Y0 - 0.4, 0), (X0 - 0.4, Y1 + 0.4, WALL), (X1 + 0.4, Y1 + 0.4, WALL),
    (X1 + 0.4, Y0 - 0.4, WALL), (X0 - 0.4, Y1 + 0.4, 0),
)]
# Frame the playable floor (choices, signs, docks) and both whole trucks; the
# back wall tops may run out of frame.
PLAY = None  # filled after RACK_TOP is known below
KEEP_BY = {}


def play_box():
    return cube(X0 - 1.0, TRUCK_FRONT - 0.4, 0, X1 + 1.0, RY1 - 1.0, PLAQUE_Z1 + 0.3)


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
    "entrance": (cube(EX0, EY0 - 0.2, FZ, EX1, EY1, FZ + 4.6), Vector(((EX0 + EX1) / 2, EY0, FZ + 6.0))),
    "keeper": (cube(KEEPER.x - 2.0, KEEPER.y - 0.9, FZ, KEEPER.x + 0.5, KEEPER.y + 0.5, FZ + 2.3), Vector((KEEPER.x + 2.1, KEEPER.y, FZ + 2.1))),
    "wms": (cube(KX - 1.15, KY - 0.45, FZ, KX + 1.15, KY + 0.45, SCREEN[5] + 0.12), Vector((KX, KY, SCREEN[5] + 1.2))),
}
for parcel, i in ALPHA_ROW.items():
    x0 = RANGES[i][2]
    REGIONS[f"alphabet-{parcel}"] = (cube(x0, RY0 - 0.2, FZ, x0 + RW, RY0 + 1.2, PLAQUE_Z1), Vector((x0 + RW / 2, RY0, PLAQUE_Z1 + 1.0)))
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
TEXT_GROUPS = {g for g in GROUPS if g.endswith("_text") or g == "plaques" or g.startswith("o_route")}


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
GX = P["GIFT"][0]
DISPATCH = cube(DX_OUT - DOOR, -3.5 * TRUCK, 0, DX_OUT + DOOR, 0, 4.4 * TRUCK)  # rear of the dispatch truck: where every route ends
OUTCOMES = {
    # name: (extra outcome groups, hidden base groups, keep points)
    "entrance": ({"o_gift_entrance", "o_route_entrance", "o_route_entrance_text", "o_runners_entrance"}, {"gift", "jack"},
                 cube(EX0 - 3, Y0, FZ, EX1, EY1, FZ + 4.6) + cube(EX0, LANE0, FZ, DX_OUT, LANE1, FZ + 1) + DISPATCH),
    **{f"alphabet-{p}": ({f"o_gift_{p}", f"o_route_{p}", f"o_route_{p}_text", f"o_runners_{p}"}, {"gift", "jack"},
                         cube(RANGES[i][2] - 3, RY0 - 1, FZ, RANGES[i][2] + RW + 3, RY0 + 2, PLAQUE_Z1) + cube(RANGES[i][2], LANE0, FZ, DX_OUT, LANE1, FZ + 1) + DISPATCH)
       for p, i in ALPHA_ROW.items()},
    "keeper": ({"o_gift_hot", "o_newshift", "o_newshift_text", "o_route_hot", "o_route_hot_text"}, {"gift", "jack", "keeper"},
               cube(P["PUZZLED"][0][0] - 6, LANE0, FZ, X1 - 0.5, RY0, FZ + 3) + cube(P["RX"][1], RY0, FZ, P["RX"][0] + RW, RY0, PLAQUE_Z1) + DISPATCH),
    "wms": ({"o_agv_hot", "o_gift_fork", "o_route_hot", "o_route_hot_text"}, {"gift", "jack"},
            cube(KX - 1.2, KY - 0.5, FZ, X1 - 0.5, RY0, SCREEN[5]) + cube(P["RX"][1], RY0, FZ, P["RX"][0] + RW, RY0, PLAQUE_Z1) + DISPATCH),
}
if MODE == "outcomes":
    W, H = OUTCOME_RES
    only = os.environ.get("ONLY")
    for name, (extra, hidden, keep) in OUTCOMES.items():
        if only and name not in only.split(","):
            continue
        cam = camera("o_" + name, ((W, H), FORMATS_SPEC["desk"][1], FORMATS_SPEC["desk"][2], (0.04, 0.05, 0.96, 0.95)), keep, right=True)
        scene.camera = cam
        bpy.context.view_layer.update()
        manifest["outcomes"][name] = frame_data(cam, W, H)
        g, route = STORY[name]
        manifest["outcomes"][name]["story"] = {"gift": project(cam, g, W, H), "route": [project(cam, q, W, H) for q in route],
                                               "hot": [project(cam, q, W, H) for q in f3(ROUTES["hot"])],
                                               "heads": [project(cam, h, W, H) for h in O_HEADS]}
        show_only((ALL - hidden) | extra)
        render(OUT / f"outcome-{name}.png", W, H)
        show_only(((ALL - hidden) | extra) - TEXT_GROUPS)
        render(OUT / f"outcome-{name}-notext.png", W, H)
(OUT / f"manifest-{LAYOUT}-{MODE}.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
if os.environ.get("SAVE"):
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "warehouse.blend"))
print("WAREHOUSE OK", MODE, FORMATS)
