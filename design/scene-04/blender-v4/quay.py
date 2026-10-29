# Scene 4 (barge) v4: the Ob quay built as geometry, so cranes stand on their
# rails, nothing floats and every format is a camera, not a repaint.
# blender --background --factory-startup --python quay.py -- OUTDIR MODE [FORMAT...]
#   MODE: test | plate | ids
# References: docs/scenario-assets image8 (warehouse), image9 (round ПРУ tower),
# image10 (portal cranes: dark-blue portal, orange boom and cabin), image11 (Ob port).
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
FORMATS = args[2:] or ["wide", "desk", "mid", "tall"]
OUT.mkdir(parents=True, exist_ok=True)
random.seed(4)

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


# ---- layout (metres): x along the quay, y inland, quay top z=0, edge y=0 ----
RAIL_SEA, RAIL_LAND = 2.0, 12.5
PORTAL_Y = (RAIL_SEA + RAIL_LAND) / 2
NEAR_X, FAR_X = 14.0, 46.0
PEOPLE = 3.0  # people read larger than life, as in the rest of the game
BLUE, NAVY, ORANGE, BOOM = "#2A5FA8", "#1E3E6E", "#FF6A13", "#F59A1B"

# ground: water, quay wall, paving, rails, road, grass
aabb("water", "#4F9BD9", -260, -170, -2.4, 330, 0, -2.0, mat="water", nolines=True)
aabb("quay", "#AEB5BD", -260, -0.9, -2.2, 330, 0.0, 0.05)
aabb("quay", "#E3E5E8", -260, -1.1, 0.0, 330, 0.25, 0.28)
for x in range(-250, 330, 9):
    cyl("quay", "#2B2F36", (x, -1.35, -1.0), 0.42, 1.9, seg=12)
for x in range(-246, 330, 18):
    cyl("quay", "#3A414B", (x, -0.45, 0.45), 0.28, 0.45, seg=12)
aabb("paving", "#D9D5CC", -260, 0.25, -0.2, 330, 34, 0.0, mat="paving", nolines=True)
for y in (RAIL_SEA, RAIL_LAND):
    aabb("rails", "#B4AFA6", -260, y - 0.6, 0.0, 330, y + 0.6, 0.03, nolines=True)
    aabb("rails", "#56606B", -260, y - 0.14, 0.0, 330, y + 0.14, 0.2)
aabb("road", "#A3ACB8", -260, 34, -0.2, 330, 42, 0.02, nolines=True)
for x in range(-250, 330, 10):
    aabb("road", "#F4F5F7", x, 37.85, 0.02, x + 5, 38.15, 0.04, nolines=True)
aabb("grass", "#A9CC6E", -260, 42, -0.2, 330, 140, 0.02, nolines=True)
aabb("grass", "#E7E1D2", -260, 33.6, 0.0, 330, 34.2, 0.18)
aabb("grass", "#E7E1D2", -260, 41.8, 0.0, 330, 42.4, 0.18)


def tree(x, y, h):
    cyl("trees", "#F3EFE6", (x, y, h * 0.3), 0.32, h * 0.6, seg=8)  # birch trunk
    col = random.choice(["#F2C230", "#F0A32A", "#E8892B", "#9BC255", "#F5D046", "#7FB04A"])
    for dx, dy, dz, r in ((0, 0, 0.7, 0.30), (0.2, -0.1, 0.55, 0.22), (-0.18, 0.12, 0.57, 0.21)):
        ball("trees", col, (x + dx * h, y + dy * h, h * dz), h * r, sz=1.15)


for k in range(900):
    x, y = random.uniform(-120, 160), random.uniform(45, 150)
    tree(x + random.uniform(-1, 1), y, random.uniform(8, 12))
for k in range(30):
    x = random.uniform(-120, 160)
    if not (-24 < x < 12 or -72 < x < -26):
        tree(x, random.uniform(30.5, 32.5), random.uniform(6, 8))

# ---- digital warehouse (image8): white volume, glazed angled corner -----------
WX0, WX1, WY0, WY1, WH = -70, -28, 18, 40, 15
aabb("warehouse", "#F3F5F7", WX0, WY0, 0, WX1, WY1, WH)
aabb("warehouse", "#DCE2E8", WX0 - 0.3, WY0 - 0.3, WH, WX1 + 0.3, WY1 + 0.3, WH + 0.6)
aabb("warehouse", "#2A5FA8", WX0, WY0 - 0.15, 0, WX1 - 14, WY0, 1.2)
for k in range(4):  # loading doors
    x = WX0 + 5 + k * 8
    aabb("warehouse", "#8E9AA8", x, WY0 - 0.2, 0, x + 5, WY0, 5.2)
    for z in range(1, 5):
        aabb("warehouse", "#7A8796", x, WY0 - 0.25, z * 1.05, x + 5, WY0 - 0.2, z * 1.05 + 0.12)
# glazed corner block, stepping out like the reference facade
for i, (z0, z1, dx) in enumerate(((1.5, 5.5, 0), (5.5, 10, 1.6), (10, 14.4, 0.6))):
    aabb("warehouse", "#F3F5F7", WX1 - 14 - dx, WY0 - 2 - dx, z0 - 0.4, WX1 + dx, WY0 + 8, z0)
    aabb("warehouse", "#5A8CC4", WX1 - 13.6 - dx, WY0 - 1.9 - dx, z0, WX1 - 0.4 + dx, WY0 + 7, z1, mat="glass")
    for x in range(int(WX1 - 13 - dx), int(WX1 + dx), 3):
        aabb("warehouse", "#F3F5F7", x, WY0 - 2 - dx, z0, x + 0.25, WY0 - 1.85 - dx, z1)
aabb("warehouse", "#F3F5F7", WX1 - 14.6, WY0 - 3, 14.4, WX1 + 1.6, WY0 + 8, 15.3)
aabb("warehouse", "#E2E7EC", WX0 - 6, WY0 - 4, -0.05, WX1 + 2, WY0, 0.05, nolines=True)
# a few containers by the warehouse (image11)
for k, (x, y, c) in enumerate(((-22, 30.6, "#D9534F"), (-15.5, 30.6, "#2A5FA8"), (-9, 30.6, "#F0A32A"), (-22, 30.6, "#4C9A5B"))):
    z = 2.6 if k == 3 else 0
    aabb("containers", c, x, y, z, x + 6, y + 2.6, z + 2.6)
    for s in range(1, 6):
        aabb("containers", "#00000020" if False else c, x + s, y - 0.06, z + 0.2, x + s + 0.12, y, z + 2.4)

# ---- ПРУ (image9): round two-storey modular tower, Ivan behind open glazing ---
PX, PY = -10.0, 20.0
cyl("pru", "#F4F6F8", (PX, PY, 1.9), 5.0, 3.8, seg=40)
cyl("pru", "#2A5FA8", (PX, PY, 0.55), 5.06, 1.1, seg=40)
cyl("pru", ORANGE, (PX, PY, 4.15), 5.7, 0.7, seg=40)
cyl("pru", "#2A5FA8", (PX, PY, 9.5), 5.8, 0.6, seg=40)
cyl("pru", "#3C77C2", (PX, PY, 9.95), 5.2, 0.35, seg=40)
cyl("pru", "#E9EDF1", (PX, PY, 4.6), 5.6, 0.25, seg=40)
# glazing ring with an open bay facing the quay (camera side) so Ivan reads
OPEN = (math.radians(-150), math.radians(-80))  # faces the cameras (az about -30)
for k in range(28):
    a0 = 2 * math.pi * k / 28
    a1 = 2 * math.pi * (k + 1) / 28
    am = (a0 + a1) / 2
    am_s = math.atan2(math.sin(am), math.cos(am))
    if OPEN[0] < am_s < OPEN[1]:
        continue
    r = 5.45
    p0 = Vector((PX + r * math.cos(a0), PY + r * math.sin(a0), 4.75))
    p1 = Vector((PX + r * math.cos(a1), PY + r * math.sin(a1), 4.75))
    mid = (p0 + p1) / 2
    box("pru", "#5A8CC4", (mid.x, mid.y, 7.0), ((p1 - p0).length, 0.12, 4.4), rot=am + math.pi / 2, mat="glass", nolines=True)
for k in range(14):
    a = 2 * math.pi * k / 14
    if OPEN[0] < math.atan2(math.sin(a), math.cos(a)) < OPEN[1]:
        continue
    cyl("pru", "#F4F6F8", (PX + 5.5 * math.cos(a), PY + 5.5 * math.sin(a), 7.0), 0.12, 4.5, seg=6)
for k in range(28):  # dark back wall inside the glazing (not over Ivan)
    a = 2 * math.pi * (k + 0.5) / 28
    a_s = math.atan2(math.sin(a), math.cos(a))
    if OPEN[0] - 0.3 < a_s < OPEN[1] + 0.3:
        continue
    box("pru", "#2C3E55", (PX + 5.1 * math.cos(a), PY + 5.1 * math.sin(a), 7.0), (2 * math.pi * 5.1 / 28 + 0.05, 0.1, 4.4), rot=a + math.pi / 2, nolines=True)
cyl("pru", "#3A4A60", (PX, PY, 9.15), 5.2, 0.1, seg=40, nolines=True)  # ceiling
cyl("pru", "#C9D2DC", (PX, PY, 4.85), 5.35, 0.12, seg=40)  # floor
# entrance porch and stairs on the quay side
aabb("pru", "#2A5FA8", PX - 1.4, PY - 5.8, 0, PX + 1.4, PY - 4.7, 3.0)
aabb("pru", "#5A8CC4", PX - 0.9, PY - 5.85, 0.3, PX + 0.9, PY - 5.75, 2.4, mat="glass")
for s in range(4):
    aabb("pru", "#C9D2DC", PX - 1.6, PY - 7.2 + s * 0.35, 0, PX + 1.6, PY - 5.8, 0.25 + s * 0.2)
# modular annex behind (image9, lower photo)
aabb("pru", "#F4F6F8", PX - 15, PY + 3, 0, PX + 1, PY + 10, 3.4)
aabb("pru", "#2A5FA8", PX - 15.05, PY + 2.95, 0, PX + 1.05, PY + 10.05, 0.9)
aabb("pru", ORANGE, PX - 15.3, PY + 2.7, 3.4, PX + 1.3, PY + 10.3, 4.0)
for x in (PX - 14, PX - 11, PX - 8):
    aabb("pru", "#5A8CC4", x, PY + 2.9, 1.3, x + 2, PY + 3, 2.8, mat="glass")


def person(group, c, facing, hat, beard=False, sitting=False, s=PEOPLE, pose=None):
    """Simple game figure: navy overalls with orange stripes, hard hat."""
    M = Matrix.Translation(c) @ Matrix.Rotation(facing, 4, "Z") @ Matrix.Diagonal((s, s, s, 1))
    if sitting == "ground":  # legs stretched out on the quay
        for dy in (-0.13, 0.13):
            box(group, NAVY, (0.35, dy, 0.1), (0.75, 0.2, 0.2), M=M)
            box(group, "#2B2F36", (0.75, dy, 0.14), (0.12, 0.2, 0.28), M=M)
    if not sitting:
        for dy in (-0.13, 0.13):
            box(group, NAVY, (0, dy, 0.42), (0.2, 0.18, 0.84), M=M)
            box(group, "#2B2F36", (0.05, dy, 0.05), (0.3, 0.2, 0.1), M=M)
        base = 0.84
    else:
        base = 0.0
    box(group, NAVY, (0, 0, base + 0.33), (0.3, 0.46, 0.66), M=M)
    box(group, ORANGE, (0.001, 0, base + 0.28), (0.31, 0.47, 0.06), M=M)
    arms = pose if pose and isinstance(pose[0], tuple) else (pose or (0, 0),) * 2
    for dy, arm in zip((-0.29, 0.29), arms):
        beam(group, NAVY, (0, dy, base + 0.62), (0.18 + arm[0], dy * 1.1, base + 0.2 + arm[1]), 0.14, M=M)
        ball(group, "#F2C29B", (0.18 + arm[0], dy * 1.1, base + 0.2 + arm[1]), 0.07, M=M, sub=1)
    ball(group, "#F2C29B", (0, 0, base + 0.88), 0.21, M=M)
    if beard:
        ball(group, "#4A3426", (0.07, 0, base + 0.79), 0.13, sx=0.8, sz=0.8, M=M)
    ball(group, "#2B2F36", (0.2, -0.07, base + 0.92), 0.03, M=M, sub=1)
    ball(group, "#2B2F36", (0.2, 0.07, base + 0.92), 0.03, M=M, sub=1)
    ball(group, hat, (0, 0, base + 1.0), 0.23, sz=0.7, M=M)
    cyl(group, hat, (0.04, 0, base + 0.99), 0.26, 0.03, M=M, seg=16)


# Ivan at the remote-control desk right behind the open glazing, facing out
IVA = math.radians(-115)
IV = Vector((PX + 3.6 * math.cos(IVA), PY + 3.6 * math.sin(IVA), 5.0))
IM = Matrix.Translation(IV) @ Matrix.Rotation(IVA, 4, "Z")  # local +x = outwards
person("ivan", tuple(IV), IVA, ORANGE, sitting=True, pose=(0.12, 0.02))
aabb("desk", "#3A414B", -0.9, -0.9, -0.1, -0.5, 0.9, 2.0, M=IM)  # chair back
aabb("desk", "#D3DAE2", 0.75, -2.0, -0.1, 1.3, 2.0, 0.6, M=IM)  # low desk
aabb("desk", "#2A5FA8", 0.8, -0.5, 0.6, 1.25, 0.5, 0.75, M=IM)  # joystick panel
for dy, rot in ((-2.5, -0.5), (2.5, 0.5)):  # screens to the sides, angled in
    box("desk", "#24303F", (0.5, dy, 1.7), (0.15, 1.4, 1.0), rot=rot, M=IM)
    box("desk", "#7FD0F5", (0.42, dy, 1.7), (0.04, 1.2, 0.8), rot=rot, mat="flat", M=IM)

# ---- driverless tractor and the gift on its pallet ---------------------------
R_HOOK = 16.8  # horizontal reach of the near boom head (luff 60)
A_GIFT, A_DECK = math.radians(-234.0), math.radians(-97.5)
GX, GY = 14.0 + R_HOOK * math.cos(A_GIFT), 7.25 + R_HOOK * math.sin(A_GIFT)
aabb("tractor", "#2A5FA8", GX - 13, GY - 1.2, 0.6, GX - 9.5, GY + 1.2, 2.0)
aabb("tractor", "#5A8CC4", GX - 10.4, GY - 1.0, 1.2, GX - 9.45, GY + 1.0, 1.85, mat="glass")
aabb("tractor", "#F4F6F8", GX - 12.8, GY - 1.0, 2.0, GX - 9.7, GY + 1.0, 2.15)
aabb("tractor", "#C9D2DC", GX - 9.4, GY - 1.2, 0.6, GX - 3.5, GY + 1.2, 0.9)
for x in (GX - 12, GX - 10.3, GX - 8.2, GX - 4.8):
    for y in (GY - 1.15, GY + 1.15):
        cyl("tractor", "#2B2F36", (x, y, 0.45), 0.45, 0.4, axis="Y", seg=16)
cyl("tractor", "#7FD0F5", (GX - 11.2, GY, 2.35), 0.25, 0.4, seg=10, mat="flat")
# gift: pallet (stays on the quay) and the box with a red ribbon and bow
aabb("pallet", "#C79A5B", GX - 1.8, GY - 1.8, 0, GX + 1.8, GY + 1.8, 0.3)


def gift(group, k=1.45):
    def gb(x0, y0, z0, x1, y1, z1, c):
        aabb(group, c, GX + x0 * k, GY + y0 * k, 0.3 + (z0 - 0.3) * k, GX + x1 * k, GY + y1 * k, 0.3 + (z1 - 0.3) * k)
    gb(-1.05, -1.05, 0.3, 1.05, 1.05, 2.0, "#E2B977")
    gb(-0.18, -1.08, 0.3, 0.18, 1.08, 2.03, "#D62B2B")
    gb(-1.08, -0.18, 0.3, 1.08, 0.18, 2.03, "#D62B2B")
    zt = 0.3 + 1.73 * k
    for a in (0.6, -0.6, math.pi - 0.6, math.pi + 0.6):
        ball(group, "#E53935", (GX + 0.42 * k * math.cos(a), GY + 0.42 * k * math.sin(a), zt + 0.17 * k), 0.38 * k, sx=1.0, sy=0.55, sz=0.5, sub=2)
    ball(group, "#B71C1C", (GX, GY, zt + 0.12 * k), 0.2 * k)


gift("gift")  # on its pallet, rendered with the quay as holdout
gift("box")  # free-moving copy for the lift


# ---- portal cranes (image10): bogies on both rails by construction -------------
def portal_crane(group, x, slew, luff=60.0, boom_len=27.0, hook_drop=14.0, ladder=False, hook=True):
    g, top = group, group + "_top"
    zp = 10.5
    legs = []
    for sx in (-1, 1):
        for ry in (RAIL_SEA, RAIL_LAND):
            bx = x + sx * 4.6
            # bogie with two wheels on the rail head (rail top z=0.2)
            aabb(g, NAVY, bx - 1.7, ry - 0.5, 0.75, bx + 1.7, ry + 0.5, 1.45)
            for wx in (-1.0, 1.0):
                cyl(g, "#2B2F36", (bx + wx, ry, 0.68), 0.48, 0.5, axis="Y", seg=18)
            aabb(g, "#FFC20E", bx - 1.75, ry - 0.52, 0.75, bx - 1.55, ry + 0.52, 1.45)
            foot = Vector((bx, ry, 1.45))
            head = Vector((x + sx * 2.6, PORTAL_Y + (2.6 if ry > PORTAL_Y else -2.6), zp))
            beam(g, BLUE, foot, head, 0.95)
            legs.append((foot, head))
    # portal ring beams and bracing between legs on each rail side
    for ry in (RAIL_SEA, RAIL_LAND):
        sgn = 1 if ry > PORTAL_Y else -1
        beam(g, BLUE, (x - 4.0, ry + sgn * -0.3 * 0, 5.0), (x + 4.0, ry, 5.0), 0.6)
    for sx in (-1, 1):
        beam(g, BLUE, (x + sx * 3.9, RAIL_SEA + 0.6, 4.6), (x + sx * 3.9, RAIL_LAND - 0.6, 4.6), 0.6)
    aabb(g, BLUE, x - 3.2, PORTAL_Y - 3.2, zp - 0.4, x + 3.2, PORTAL_Y + 3.2, zp + 0.4)
    aabb(g, "#F4F6F8", x - 3.3, PORTAL_Y - 3.3, zp + 0.4, x + 3.3, PORTAL_Y + 3.3, zp + 0.55)  # walkway
    if ladder:
        # caged yellow ladder from the quay up the west sea-side leg (faces the camera)
        lx = x - 6.6
        y0, y1 = RAIL_SEA + 1.4, RAIL_SEA + 2.4
        for z in [0.4 + i * 0.5 for i in range(int((zp - 0.4) / 0.5))]:
            beam("ladder", "#FFC20E", (lx, y0, z), (lx, y1, z), 0.09)
        for yy in (y0, y1):
            beam("ladder", "#FFC20E", (lx, yy, 0), (lx, yy, zp + 1.6), 0.16)
        for z in [3 + i * 1.3 for i in range(int((zp - 3) / 1.3) + 1)]:
            ring = [(lx - 0.9 * math.sin(a), (y0 + y1) / 2 + 0.9 * math.cos(a), z) for a in [i * math.pi / 8 for i in range(0, 9)]]
            for p0, p1 in zip(ring, ring[1:]):
                beam("ladder", "#FFC20E", p0, p1, 0.09)
        for yy in (y0, y1):
            beam("ladder", "#FFC20E", (lx, yy, zp + 1.6), (x - 3.3, yy, zp + 1.6), 0.12)
        aabb("ladder", "#FFC20E", lx - 0.2, y0, zp + 0.4, x - 3.2, y1, zp + 0.55)
    # slewing upper: turntable, machinery house, cabin, A-frame, lattice boom
    M = Matrix.Translation((x, PORTAL_Y, zp + 0.55)) @ Matrix.Rotation(slew, 4, "Z")
    cyl(top, NAVY, (0, 0, 0.35), 2.7, 0.7, M=M, seg=32)
    aabb(top, NAVY, -5.2, -2.2, 0.7, 1.6, 2.2, 4.6, M=M)
    aabb(top, "#27497F", -5.3, -2.3, 4.6, 1.7, 2.3, 4.9, M=M)
    aabb(top, "#3A414B", -6.4, -1.9, 0.9, -5.2, 1.9, 3.6, M=M)  # counterweight
    for k in range(3):
        aabb(top, "#7FA7D6", -4.6 + k * 1.8, 2.2, 2.4, -3.6 + k * 1.8, 2.25, 3.6, M=M, mat="flat")
    # cabin on the boom side: hollow, with a big open front facing the water and
    # the camera, so whoever sits inside reads (image10: orange cabin)
    cx0, cx1, cy0, cy1, cz0, cz1 = 1.4, 5.4, -4.2, -1.0, 0.9, 5.6
    aabb(top, ORANGE, cx0, cy0, cz0, cx1, cy1, cz0 + 0.3, M=M)  # floor
    aabb(top, "#E55A0E", cx0 - 0.1, cy0 - 0.1, cz1, cx1 + 0.1, cy1 + 0.1, cz1 + 0.35, M=M)  # roof
    aabb(top, "#2C3E55", cx0, cy0, cz0, cx0 + 0.15, cy1, cz1, M=M)  # back wall, dark inside
    aabb(top, ORANGE, cx0 - 0.15, cy0, cz0, cx0, cy1, cz1, M=M)
    for yy in (cy0, cy1 - 0.15):  # side walls with a window
        aabb(top, ORANGE, cx0, yy, cz0, cx1, yy + 0.15, cz0 + 1.6, M=M)
        aabb(top, ORANGE, cx0, yy, cz0, cx0 + 0.9, yy + 0.15, cz1, M=M)
        aabb(top, ORANGE, cx1 - 0.25, yy, cz0, cx1, yy + 0.15, cz1, M=M)
        aabb(top, ORANGE, cx0, yy, cz1 - 0.3, cx1, yy + 0.15, cz1, M=M)
    aabb(top, ORANGE, cx1 - 0.15, cy0, cz0, cx1, cy1, cz0 + 1.3, M=M)  # front sill
    aabb(top, "#2C3E55", cx0 + 0.15, cy0 + 0.15, cz0 + 0.3, cx0 + 0.4, cy1 - 0.15, cz1, M=M)
    aabb(top, "#7FA7D6", cx1 - 0.6, cy0 + 0.6, cz0 + 1.3, cx1 - 0.2, cy1 - 0.6, cz0 + 1.6, M=M)  # control desk
    # A-frame mast
    apex = Vector((-1.5, 0, 12.5))
    for sy in (-1.6, 1.6):
        beam(top, BOOM, (-3.8, sy, 4.9), apex, 0.5, M=M)
        beam(top, BOOM, (0.8, sy, 4.9), apex, 0.5, M=M)
    # lattice boom: four chords and lacing
    piv = Vector((2.4, 0, 2.6))
    a = math.radians(luff)
    tip = piv + Vector((math.cos(a), 0, math.sin(a))) * boom_len
    ax = (tip - piv).normalized()
    up = Vector((-math.sin(a), 0, math.cos(a)))
    def chord(t, oy, oz, taper=True):
        w = (1.0 - 0.55 * t) if taper else 1.0
        return piv + ax * (boom_len * t) + Vector((0, oy * w, 0)) + up * (oz * w)
    corners = [(-0.75, -0.6), (0.75, -0.6), (0.75, 0.6), (-0.75, 0.6)]
    for oy, oz in corners:
        beam(top, BOOM, chord(0, oy, oz), chord(1, oy, oz), 0.26, M=M)
    n = 14
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        for (oy0, oz0), (oy1, oz1) in zip(corners, corners[1:] + corners[:1]):
            beam(top, BOOM, chord(t0, oy0, oz0), chord(t1, oy1, oz1), 0.12, M=M)
    cyl(top, NAVY, tip + Vector((0.4, 0, 0)), 0.75, 0.9, axis="Y", M=M, seg=16)
    # luffing ties from the A-frame to the boom head
    for sy in (-0.5, 0.5):
        beam(top, "#3A414B", apex + Vector((0, sy, 0)), tip + Vector((0, sy * 0.4, 0.3)), 0.09, M=M)
    # hook: cable from the boom head straight down, block and hook
    tip_l = tip + Vector((0.9, 0, -0.6))
    tip_w = M @ tip_l
    if not hook:
        return {"cabin": M @ Vector((3.2, -2.6, 3.4)), "tip": tip_w, "tipLocal": tip_l, "M": M, "pivot": Vector((x, PORTAL_Y, zp + 0.55))}
    hook_z = tip_w.z - hook_drop
    hk = group + "_hook"
    beam(hk, "#2B2F36", tip_w, (tip_w.x, tip_w.y, hook_z + 1.0), 0.09)
    aabb(hk, "#FFC20E", tip_w.x - 0.55, tip_w.y - 0.35, hook_z, tip_w.x + 0.55, tip_w.y + 0.35, hook_z + 1.0)
    for k in range(7):
        a0, a1 = k * math.pi / 6 - math.pi / 2, (k + 1) * math.pi / 6 - math.pi / 2
        beam(hk, "#3A414B", (tip_w.x + 0.45 * math.cos(a0), tip_w.y, hook_z - 0.6 + 0.45 * math.sin(a0)),
             (tip_w.x + 0.45 * math.cos(a1), tip_w.y, hook_z - 0.6 + 0.45 * math.sin(a1)), 0.16)
    cab = M @ Vector((3.2, -2.6, 3.4))
    return {"cabin": cab, "tip": tip_w, "hook": Vector((tip_w.x, tip_w.y, hook_z - 1.2)), "M": M}


near = portal_crane("near", NEAR_X, 0.0, luff=60, ladder=True, hook=False)
far = portal_crane("far", FAR_X, math.radians(-75), luff=55, boom_len=24, hook_drop=10)
# Petr in the far cabin, facing out of its glazed front
person("petr", tuple(far["M"] @ Vector((3.0, -2.6, 1.25))), math.radians(-75), "#F4F6F8", beard=True, sitting=True, pose=(0.1, 0.1))
# Petr's own cargo: stacked wooden crates by the far crane
for k, (dx, dy, dz) in enumerate(((0, 0, 0), (2.6, 0, 0), (0, 2.6, 0), (2.6, 2.6, 0), (1.3, 1.3, 2.4), (5.2, 0.4, 0))):
    x0, y0 = FAR_X + 9 + dx, 16 + dy
    aabb("crates", "#C79A5B", x0, y0, dz, x0 + 2.4, y0 + 2.4, dz + 2.4)
    for t in (0.2, 2.0):
        aabb("crates", "#A8773F", x0 - 0.02, y0 - 0.02, dz + t, x0 + 2.42, y0 + 2.42, dz + t + 0.22)

# ---- the barge (moored broadside, stern wheelhouse to the right, pipes on deck)
BX0, BX1, BY0, BY1 = 2.0, 50.0, -13.5, -2.6
BZ = -0.9  # deck height: a laden barge sits low against the quay
hull_bm = None
def hull(group, x0, x1, y0, y1, zb, zd, color, bow=6.0):
    yc = (y0 + y1) / 2
    hw = (y1 - y0) / 2
    pts = [(x0 + bow, y0), (x1 - 1.5, y0), (x1, y0 + 1.2), (x1, y1 - 1.2), (x1 - 1.5, y1), (x0 + bow, y1), (x0, yc + hw * 0.45), (x0, yc - hw * 0.45)]
    bm = _bm(group, color, "obj", False)
    vb = [bm.verts.new((px, py, zb)) for px, py in pts]
    vt = [bm.verts.new((px, py, zd)) for px, py in pts]
    bm.faces.new(list(reversed(vb)))
    bm.faces.new(vt)
    n = len(pts)
    for i in range(n):
        bm.faces.new((vb[i], vb[(i + 1) % n], vt[(i + 1) % n], vt[i]))


hull("barge", BX0, BX1, BY0, BY1, -2.6, BZ - 0.6, "#2B2F36")
hull("barge", BX0, BX1, BY0, BY1, BZ - 0.6, BZ + 0.9, "#C8322B")
hull("barge", BX0 + 0.6, BX1 - 0.6, BY0 + 0.6, BY1 - 0.6, BZ + 0.9, BZ + 0.92, "#8E3A2E")
aabb("barge", "#F4F6F8", BX0 + 4, BY0 - 0.02, BZ + 0.3, BX1 - 1, BY0 + 0.0, BZ + 0.45)  # white boot stripe
# coaming around the cargo well
aabb("barge", "#A72A24", BX0 + 5, BY0 + 0.5, BZ + 0.9, BX1 - 11.5, BY0 + 0.9, BZ + 1.6)
aabb("barge", "#A72A24", BX0 + 5, BY1 - 0.9, BZ + 0.9, BX1 - 11.5, BY1 - 0.5, BZ + 1.6)
# pipe stacks, strapped; a free spot left of them, under the near crane
for sx0, sx1 in ((19, 28.5), (30, 37.5)):
    for row in range(3):
        nrow = 7 - row
        for i in range(nrow):
            y = BY0 + 1.6 + (i + row * 0.5) * 1.1
            z = BZ + 1.45 + row * 0.95
            cyl("barge", "#8C98A5", ((sx0 + sx1) / 2, y, z), 0.52, sx1 - sx0, axis="X", seg=14)
            cyl("barge", "#2B3440", (sx0 - 0.01, y, z), 0.32, 0.04, axis="X", seg=12)
    for sx in (sx0 + 3, (sx0 + sx1) / 2, sx1 - 3):
        aabb("barge", ORANGE, sx - 0.2, BY0 + 0.9, BZ + 0.95, sx + 0.2, BY1 - 0.9, BZ + 4.1)
# wheelhouse at the stern (right), funnel
aabb("barge", "#F4F6F8", BX1 - 11, BY0 + 1.2, BZ + 0.9, BX1 - 2, BY1 - 1.2, BZ + 4.2)
aabb("barge", "#F4F6F8", BX1 - 9, BY0 + 2.2, BZ + 4.2, BX1 - 3.2, BY1 - 2.2, BZ + 6.8)
aabb("barge", "#2C3E55", BX1 - 9.05, BY0 + 2.6, BZ + 5.4, BX1 - 8.95, BY1 - 2.6, BZ + 6.4)
aabb("barge", "#5A8CC4", BX1 - 11.05, BY0 + 1.6, BZ + 2.4, BX1 - 10.95, BY1 - 1.6, BZ + 3.4, mat="glass")
aabb("barge", "#2A5FA8", BX1 - 9.3, BY0 + 1.9, BZ + 6.8, BX1 - 2.9, BY1 - 1.9, BZ + 7.2)
cyl("barge", "#2B2F36", (BX1 - 4.5, (BY0 + BY1) / 2, BZ + 8.2), 0.6, 2.4, seg=16)
cyl("barge", ORANGE, (BX1 - 4.5, (BY0 + BY1) / 2, BZ + 8.6), 0.62, 0.4, seg=16)
for k in range(4):
    ball("smoke", "#F4F6F8", (BX1 - 4.5 + k * 1.6, (BY0 + BY1) / 2 + k * 0.6, BZ + 10 + k * 1.4), 0.9 + k * 0.35, nolines=True)
# bow fittings and mooring ropes to quay bollards
cyl("barge", "#3A414B", (BX0 + 3.5, (BY0 + BY1) / 2, BZ + 1.3), 0.35, 0.8, seg=10)
for x in range(int(BX0 + 8), int(BX1 - 2), 7):  # tyre fenders on the hull side
    cyl("barge", "#2B2F36", (x, BY1 + 0.05, BZ + 0.2), 0.45, 0.35, axis="Y", seg=14)

# sprites that move: an empty hook block, and the gift slung under the hook
def hook_block(group, c):
    c = Vector(c)  # c = cable attach point (top of the block)
    aabb(group, "#FFC20E", c.x - 0.6, c.y - 0.4, c.z - 1.1, c.x + 0.6, c.y + 0.4, c.z)
    aabb(group, "#3A414B", c.x - 0.15, c.y - 0.15, c.z - 1.5, c.x + 0.15, c.y + 0.15, c.z - 1.1)
    for k in range(7):
        a0, a1 = k * math.pi / 6 - math.pi / 2, (k + 1) * math.pi / 6 - math.pi / 2
        beam(group, "#3A414B", (c.x + 0.45 * math.cos(a0), c.y, c.z - 2.0 + 0.45 * math.sin(a0)),
             (c.x + 0.45 * math.cos(a1), c.y, c.z - 2.0 + 0.45 * math.sin(a1)), 0.16)


GIFT_TOP = 0.3 + 1.73 * 1.45
SLING = 4.2  # from the gift's top to the cable attach point of the block
hook_block("hook", (GX, GY, GIFT_TOP + SLING + 1.5))
hook_block("slings", (GX, GY, GIFT_TOP + SLING + 1.5))
for sx in (-1, 1):
    for sy in (-1, 1):
        beam("slings", "#2B2F36", (GX + sx * 1.45, GY + sy * 1.45, 0.4), (GX, GY, GIFT_TOP + SLING - 0.4), 0.07)
HOOK_ATTACH = GIFT_TOP + SLING + 1.5  # block top above the quay when the gift sits on its pallet

# ---- outcome-only figures (group names start with o_) ---------------------------
OUT_REST = Matrix.Translation(near["pivot"]) @ Matrix.Rotation(A_DECK, 4, "Z") @ Matrix.Translation(-near["pivot"])
# rush: Ivan sits on the quay by the ladder foot, a hand to his brow, tired but pleased
person("o_ivan_ground", (NEAR_X - 9.2, RAIL_SEA - 0.9, 0.0), math.radians(-95), ORANGE, sitting="ground",
       pose=((0.15, 0.72), (0.25, -0.05)))
# wait: the crane operator stands by the gift and looks at his watch
person("o_operator", (GX + 3.2, GY - 2.6, 0.0), math.radians(-110), ORANGE, pose=((0.32, 0.5), (0.0, 0.0)))
# petr: Petr in the near cabin; Ivan on the quay below with both arms up
person("o_petr_near", tuple(OUT_REST @ near["M"] @ Vector((3.0, -2.6, 1.25))), A_DECK, "#F4F6F8", beard=True, sitting=True, pose=(0.1, 0.1))
person("o_ivan_wave", (NEAR_X - 9.0, RAIL_SEA - 0.9, 0.0), math.radians(-100), ORANGE, pose=((0.05, 1.05), (0.05, 1.05)))
OUT_DECK = Vector((NEAR_X + R_HOOK * math.cos(A_DECK), PORTAL_Y + R_HOOK * math.sin(A_DECK), BZ + 0.92))
OUT_GIFT_DELTA = OUT_DECK - Vector((GX, GY, 0.3))
beam("o_cable", "#2B2F36", OUT_REST @ near["tip"], Vector((GX, GY, GIFT_TOP + SLING + 1.5)) + OUT_GIFT_DELTA, 0.09)

# quay lamps
for x in range(-40, 90, 24):
    cyl("lamps", "#5A6676", (x + 7, 30, 3.5), 0.14, 7.0, seg=8)
    aabb("lamps", "#5A6676", x + 6.0, 29.6, 6.9, x + 8.0, 30.4, 7.2)

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

# ---- cameras: one per format, framed on the story strip ------------------------
FORMATS_SPEC = {
    # name: (res, azimuth, elevation, keep box u0,v0,u1,v1 in y-down screen space)
    "wide": ((1942, 809), -26, 34, (0.02, 0.04, 0.98, 0.98)),
    "desk": ((1536, 1024), -30, 36, (0.02, 0.05, 0.98, 0.97)),
    "mid": ((1402, 1122), -32, 37, (0.02, 0.06, 0.98, 0.96)),
    "tall": ((1024, 1536), float(os.environ.get("TALL_AZ", -58)), float(os.environ.get("TALL_EL", 48)), (0.04, 0.06, 0.96, 0.96)),
}


def axes(az, el):
    rot = (math.radians(90 - el), 0, math.radians(az))
    m = Euler(rot, "XYZ").to_matrix()
    return rot, m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0)), m @ Vector((0, 0, -1))


# story points that must be in frame (ПРУ, gift, both cranes incl. boom heads, barge)
CORE = [Vector(p) for p in (
    *[(PX + dx, PY + dy, z) for dx in (-6, 6) for dy in (-7, 6) for z in (0, 10.5)],
    (GX - 13, GY - 2, 0), (GX + 2, GY + 2, 2),
    (NEAR_X - 6, 0, 0), (NEAR_X + 6, 14, 0), (NEAR_X - 17, 8, 26), (NEAR_X + 17, 8, 26),
    (FAR_X - 6, 0, 0), (FAR_X + 6, 14, 0), tuple(far["tip"]), tuple(far["hook"]), tuple(far["cabin"]) ,
    (BX0, BY0, BZ), (BX1 - 6, BY0, BZ),
)]
KEEP_BY = {
    "wide": CORE + [Vector((WX1 - 8, WY0 - 4, 15)), Vector((FAR_X + 14, 20, 5)), Vector((BX1, BY0, BZ))],
    "desk": CORE + [Vector((WX1 - 4, WY0 - 4, 15)), Vector((FAR_X + 12, 20, 5))],
    "mid": CORE + [Vector((WX1 - 2, WY0 - 4, 15))],
    "tall": CORE,
}


def camera(name, spec, keep=None):
    (W, H), az, el, (u0, v0, u1, v1) = spec
    rot, R, U, F = axes(az, el)
    KEEP = keep or KEEP_BY[name]
    xs = [p.dot(R) for p in KEEP]
    ys = [p.dot(U) for p in KEEP]
    aspect = W / H
    S = max((max(xs) - min(xs)) / (u1 - u0), (max(ys) - min(ys)) / (v1 - v0) * aspect)
    Hh = S / aspect
    # centre the content box inside the keep box
    cx = (min(xs) + max(xs)) / 2 + (0.5 - (u0 + u1) / 2) * S
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


REST = Matrix.Translation(near["pivot"]) @ Matrix.Rotation(A_DECK, 4, "Z") @ Matrix.Translation(-near["pivot"])
ANCHORS = {
    "ivan": Vector((IV.x, IV.y, 5.0 + 0.85 * PEOPLE)),
    "pru": Vector((PX, PY, 10)),
    "gift": Vector((GX, GY, GIFT_TOP + 0.6)),
    "nearCabin": REST @ near["cabin"],
    "nearTip": REST @ near["tip"],
    "ladderFoot": Vector((NEAR_X - 6.6, RAIL_SEA + 1.9, 0)),
    "ladderTop": Vector((NEAR_X - 6.6, RAIL_SEA + 1.9, 11)),
    "farCabin": far["cabin"],
    "petr": Vector(far["M"] @ Vector((3.0, -2.6, 1.25 + 0.85 * PEOPLE))),
    "deckSpot": Vector((12, (BY0 + BY1) / 2, BZ + 1)),
    "bargeMid": Vector(((BX0 + BX1) / 2, (BY0 + BY1) / 2, BZ)),
    "crates": Vector((FAR_X + 12, 18, 3)),
    "quayFootNear": Vector((NEAR_X, PORTAL_Y, 0)),
}

SS = float(os.environ.get("SS", 1.5))
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = int(os.environ.get("SAMPLES", 16))

# Layers. Static story actors are separate so the game can outline them; moving
# parts (barge, near crane top, hook, gift) are separate so they can move.
MOVING = {"barge", "smoke", "near_top", "hook", "box", "slings", "gift"}
ACTORS = {"ivan": {"ivan", "desk"}, "ladder": {"ladder"}, "far": {"far_top", "petr"}}
SLEW_GIFT = math.degrees(A_GIFT) % 360  # boom over the gift
SLEW_DECK = math.degrees(A_DECK) % 360  # boom over the free spot on the deck
if SLEW_DECK < SLEW_GIFT:
    SLEW_DECK += 360
FRAMES = int(os.environ.get("FRAMES", 16))
SLEWS = [SLEW_GIFT + (SLEW_DECK - SLEW_GIFT) * k / (FRAMES - 1) for k in range(FRAMES)]
PIVOT = near["pivot"]


def objs(groups):
    return [o for g in groups for o in GROUPS.get(g, [])]


def set_slew(deg):
    m = Matrix.Translation(PIVOT) @ Matrix.Rotation(math.radians(deg), 4, "Z") @ Matrix.Translation(-PIVOT)
    for o in GROUPS["near_top"]:
        o.matrix_world = m


def layer(path, show, holdout=(), transparent=True):
    """Render only `show`; `holdout` groups still occlude (cut alpha, no ink)."""
    show, holdout = set(show), set(holdout)
    for g, os_ in GROUPS.items():
        for o in os_:
            o.hide_render = g not in show and g not in holdout
            o.is_holdout = g in holdout
            in_nolines = NOLINES in o.users_collection
            if g in holdout and not in_nolines:
                NOLINES.objects.link(o)
                o["tmp_nolines"] = True
    scene.render.film_transparent = transparent
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    for o in objs(GROUPS):
        if o.get("tmp_nolines"):
            NOLINES.objects.unlink(o)
            del o["tmp_nolines"]
        o.is_holdout = False
        o.hide_render = False


def affine(cam, W, H):
    """Ortho camera as an affine map world -> image px: [u, v] = A @ [x, y, z, 1]."""
    o = project(cam, (0, 0, 0), W, H)
    ex = project(cam, (1, 0, 0), W, H)
    ey = project(cam, (0, 1, 0), W, H)
    ez = project(cam, (0, 0, 1), W, H)
    return [[round(ex[0] - o[0], 4), round(ey[0] - o[0], 4), round(ez[0] - o[0], 4), o[0]],
            [round(ex[1] - o[1], 4), round(ey[1] - o[1], 4), round(ez[1] - o[1], 4), o[1]]]


OUTCOME_ONLY = {g for g in GROUPS if g.startswith("o_")}
ALL = set(GROUPS) - OUTCOME_ONLY
STATIC = ALL - MOVING
manifest = {
    "scene": {
        "pivot": list(PIVOT), "boomReach": R_HOOK, "tip": [round(v, 3) for v in near["tipLocal"]],
        "slews": [round(v, 2) for v in SLEWS], "restSlew": round(SLEW_DECK, 2),
        # boom head (cable start) in world space for every top-NN frame
        "tips": [[round(c, 3) for c in Matrix.Translation(PIVOT) @ Matrix.Rotation(math.radians(d), 4, "Z") @ Matrix.Translation(-PIVOT) @ near["tip"]] for d in SLEWS],
        "gift": [GX, GY, 0.3], "giftTop": GIFT_TOP, "hookAttach": HOOK_ATTACH,
        "deck": [NEAR_X + R_HOOK * math.cos(A_DECK), PORTAL_Y + R_HOOK * math.sin(A_DECK), BZ + 0.92],
        "funnel": [BX1 - 4.5, (BY0 + BY1) / 2, BZ + 9.4],
        "barge": [BX0, BX1, BY0, BY1, BZ],
    }
}
for name in FORMATS:
    spec = FORMATS_SPEC[name]
    cam = camera(name, spec)
    W, H = spec[0]
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = round(W * SS), round(H * SS)
    ls.linestyle.thickness = 1.5 * SS
    bpy.context.view_layer.update()
    manifest[name] = {"width": W, "height": H, "affine": affine(cam, W, H),
                      "anchors": {k: project(cam, v, W, H) for k, v in ANCHORS.items()}}
    if MODE == "test":
        set_slew(SLEW_DECK)
        for o in objs({"box", "slings", "hook"} | OUTCOME_ONLY):
            o.hide_render = True
        scene.render.filepath = str(OUT / f"test-{name}.png")
        bpy.ops.render.render(write_still=True)
    elif MODE == "layers":
        D = OUT / name
        D.mkdir(exist_ok=True)
        set_slew(SLEW_DECK)
        actors = set().union(*ACTORS.values())
        layer(D / "plate.png", STATIC - actors, transparent=False)
        for k, groups in ACTORS.items():
            layer(D / f"{k}.png", groups, holdout=STATIC - groups)
        layer(D / "barge.png", {"barge"})
        layer(D / "smoke.png", {"smoke"})
        layer(D / "gift.png", {"gift"}, holdout=STATIC)
        for i, deg in enumerate(SLEWS):
            set_slew(deg)
            layer(D / f"top-{i:02d}.png", {"near_top"})
        set_slew(SLEW_DECK)
        layer(D / "hook.png", {"hook"})
        layer(D / "box.png", {"box", "slings"})
if MODE == "outcomes":
    SAIL = Vector((-9, -3.5, 0))  # the barge has cast off and heads downstream (bow left)
    PRU_BOX = [Vector((PX + dx, PY + dy, z)) for dx in (-6, 6) for dy in (-7, 6) for z in (0, 10.5)]
    NEAR_BOX = [Vector((NEAR_X + dx, PORTAL_Y + dy, z)) for dx in (-7, 7) for dy in (-5, 5) for z in (0, 16)]
    DECK = [OUT_DECK + Vector((dx, dy, 0)) for dx in (-6, 8) for dy in (-3, 3)]
    OUTCOMES = {
        # name: (visible extra groups, hidden base groups, moves {group: delta}, keep points)
        "remote": ({"slings", "o_cable"}, set(), {"gift": OUT_GIFT_DELTA, "slings": OUT_GIFT_DELTA},
                   PRU_BOX + NEAR_BOX + DECK),
        "petr": ({"slings", "o_cable", "o_petr_near", "o_ivan_wave"}, {"ivan", "petr"}, {"gift": OUT_GIFT_DELTA, "slings": OUT_GIFT_DELTA},
                 NEAR_BOX + DECK + [Vector((NEAR_X - 12, 0, 0)), Vector((FAR_X + 14, 20, 4)), Vector((FAR_X, PORTAL_Y, 16))]),
        "rush": ({"o_ivan_ground"}, {"ivan"}, {"gift": OUT_GIFT_DELTA + SAIL, "barge": SAIL, "smoke": SAIL},
                 NEAR_BOX + [p + SAIL for p in DECK] + [Vector((NEAR_X - 14, -2, 0)), Vector((BX1 - 6 + SAIL.x, BY0 + SAIL.y, 6))]),
        "wait": ({"o_operator"}, {"ivan"}, {"barge": SAIL * 1.6, "smoke": SAIL * 1.6},
                 [Vector((GX + dx, GY + dy, z)) for dx in (-3, 6) for dy in (-5, 3) for z in (0, 6)] + NEAR_BOX
                 + [Vector((BX0 + 10 + SAIL.x * 1.6, BY0 + SAIL.y * 1.6, 0)), Vector((BX1 - 4 + SAIL.x * 1.6, BY0 + SAIL.y * 1.6, 8))]),
    }
    spec = FORMATS_SPEC["wide"]
    W, H = spec[0]
    scene.render.resolution_x, scene.render.resolution_y = round(W * SS), round(H * SS)
    ls.linestyle.thickness = 1.5 * SS
    scene.render.film_transparent = False
    set_slew(SLEW_DECK)
    manifest["outcomes"] = {}
    for name, (extra, hidden, moves, keep) in OUTCOMES.items():
        cam = camera("o_" + name, (spec[0], spec[1], spec[2], (0.03, 0.05, 0.97, 0.95)), keep)
        scene.camera = cam
        bpy.context.view_layer.update()
        manifest["outcomes"][name] = {"affine": affine(cam, W, H), "anchors": {k: project(cam, v, W, H) for k, v in ANCHORS.items()}}
        for g, os_ in GROUPS.items():
            show = (g in ALL and g not in {"box", "hook", "slings"} and g not in hidden) or g in extra
            for o in os_:
                o.hide_render = not show
                if g != "near_top":
                    o.matrix_world = Matrix.Translation(moves.get(g, Vector()))
        scene.render.filepath = str(OUT / f"outcome-{name}.png")
        bpy.ops.render.render(write_still=True)
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "quay.blend"))
print("QUAY OK", MODE, FORMATS)
