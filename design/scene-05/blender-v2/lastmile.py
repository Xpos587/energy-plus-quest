# Scene 5 revision 8: rebuilt landing, inland helipad, industrial АБК and vehicles.
# Structural geometry guides gpt-image styling; final interactive bounds are remeasured.
# blender --background --factory-startup --python lastmile.py -- OUTDIR MODE [FORMAT...]
#   MODE: test | variants
# References: docs/scenario-assets image12 (map, АБК), image13 (Mi-8), image14 (РУСАК),
# image15 (robot cart), image16 (pipe carrier).
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
FORMATS = args[2:] or ["wide", "tall"]
OUT.mkdir(parents=True, exist_ok=True)
random.seed(5)

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



def tundra(nt):
    p = pos(nt)
    tc = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(mnode(nt, "MULTIPLY", p.outputs[0], 0.06), tc.inputs[0])
    nt.links.new(mnode(nt, "MULTIPLY", p.outputs[1], 0.06), tc.inputs[1])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.6
    nz.inputs["Detail"].default_value = 2.0
    nt.links.new(tc.outputs[0], nz.inputs["Vector"])
    f = mnode(nt, "GREATER_THAN", nz.outputs[0], 0.55)
    g = mnode(nt, "LESS_THAN", nz.outputs[0], 0.40)
    base = mix(nt, mnode(nt, "MULTIPLY", f, 0.45), object_color(nt), srgb("#9EA466"))
    return mix(nt, mnode(nt, "MULTIPLY", g, 0.35), base, srgb("#C4B784"))


MAT["tundra"] = toon("tundra", tundra, ramp=(0.86, 0.94, 1.0))


def text(group, body, c, size, rot, color, depth=0.08):
    cu = bpy.data.curves.new(f"t{len(GROUPS)}{body}", "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", check_existing=True)
    cu.size = size
    cu.extrude = depth
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    o = bpy.data.objects.new(cu.name, cu)
    o.location = c
    o.rotation_euler = rot
    o.data.materials.append(MAT["flat"])
    o.color = srgb(color)
    NOLINES.objects.link(o)
    GROUPS.setdefault(group, []).append(o)


PEOPLE = 12.0
V = 3.3  # vehicles drawn larger than life so they read as tappable objects
BLUE, NAVY, ORANGE = "#2A5FA8", "#1E3E6E", "#FF6A13"
TYRE, HUB, INK = "#33373D", "#8A929B", "#2B2F36"
FACE = math.radians(-116)  # towards the wide camera

# ---- compact freight landing and separate inland aviation clearing -----------
QX = -72
AX, AY, AK = 100, 52, 2.0
CX, CY = 92, -34
HPX, HPY, PS = -30, 64, 1.75
assert HPX - 13 * PS - QX > 18  # firm bank between the pad and the water
assert HPY - 18 * PS > 22       # no overlap with the freight apron

aabb("water", "#4F9BD9", -400, -300, -2.4, QX, 300, -2.0, mat="water", nolines=True)
aabb("ground", "#B3B07A", QX, -300, -0.6, 400, 300, -0.02, mat="tundra", nolines=True)
aabb("quay", "#8D9395", QX - 1, -88, -2.3, QX, 12, 0.5)
for y in range(-82, 12, 12):
    box("quay", "#343B40", (QX - 1.3, y, -0.6), (1.0, 2.0, 2.8))
    cyl("quay", "#343B40", (QX + 1.8, y, 0.9), 0.6, 1.0, seg=12)
    beam("quay", "#343B40", (QX + 1.8, y - 0.9, 1.3), (QX + 1.8, y + 0.9, 1.3), 0.4)
aabb("paving", "#B2A998", QX, -88, -0.2, -51, 12, 0.12, mat="paving", nolines=True)
aabb("yard", "#B6AB8F", -51, -92, -0.15, -6, 22, 0.04, mat="tundra", nolines=True)
# Gravel access road connects staging area and the helicopter service turnout.
beam("road", "#BEB39A", (-46, -95, 0.02), (-46, 34, 0.02), 9, 0.06, nolines=True)
beam("road", "#BEB39A", (-46, 34, 0.02), (HPX, 40, 0.02), 7, 0.06, nolines=True)
for k in range(20):
    y = 12 + k * 8
    ball("bank", "#969371", (QX + 0.5, y, -1.2), 4, sx=1.15, sy=1.4, sz=0.35, nolines=True)
# Compact grey landing slab; the surrounding grass is kept entirely clear.
aabb("pad", "#9DA4A2", HPX - 13, HPY - 13, -0.3, HPX + 13, HPY + 13, 0.18)
for k in range(64):
    a = k / 64 * math.tau
    box("pad", "#EEE6CF", (HPX + 10.8 * math.cos(a), HPY + 10.8 * math.sin(a), 0.2), (1.1, 0.38, 0.04), rot=a + math.pi / 2, mat="flat", nolines=True)
for c in ((HPX - 2.6, HPY, 0.2, 1.1, 8.0), (HPX + 2.6, HPY, 0.2, 1.1, 8.0), (HPX, HPY, 0.2, 5.2, 1.1)):
    box("pad", "#EEE6CF", c[:3], (c[3], c[4], 0.04), mat="flat", nolines=True)
cyl("pad", "#5B6470", (HPX + 18, HPY - 18, 2), 0.1, 4, seg=8)
for k in range(5):
    cyl("pad", ["#FF6A13", "#F4F5F7"][k % 2], (HPX + 18.4 + k * 0.5, HPY - 18, 3.8), 0.4 - k * 0.05, 0.52, axis="X", r2=0.35 - k * 0.05, seg=12)


def wheel(group, M, x, y, z, r, w):
    # Rounded balloon sidewalls, small recessed hubs, visible chevron tread.
    ball(group, TYRE, (x, y, z), r, sy=w / (2 * r), M=M, sub=3)
    cyl(group, TYRE, (x, y, z), r * 0.92, w * 0.78, axis="Y", seg=32, M=M)
    side = 1 if y > 0 else -1
    cyl(group, "#454A4C", (x, y + side * w * 0.5, z), r * 0.36, 0.08, axis="Y", seg=20, M=M)
    cyl(group, HUB, (x, y + side * w * 0.55, z), r * 0.17, 0.06, axis="Y", seg=12, M=M)
    for k in range(20):
        a = k * math.tau / 20
        for s in (-1, 1):
            beam(group, "#454A4C", (x + r * math.cos(a), y, z + r * math.sin(a)), (x + r * math.cos(a + 0.09), y + s * w * 0.35, z + r * math.sin(a + 0.09)), 0.08, M=M)


# ---- vehicles: local +x = forward, origin on the ground -----------------------
def heli(group, M):
    """Mi-8 (image13): orange body, black engine hump, white swoosh, 5 blades."""
    ball(group, ORANGE, (1.2, 0, 2.4), 1, sx=6.2, sy=1.65, sz=1.7, M=M, sub=3)
    ball(group, "#232629", (0.8, 0, 3.9), 1, sx=3.8, sy=1.3, sz=0.85, M=M, sub=3)
    for y in (-0.65, 0.65):
        cyl(group, "#444A4C", (3.7, y, 4.1), 0.44, 1.3, axis="X", M=M)
        cyl(group, "#101C23", (4.37, y, 4.1), 0.32, 0.04, axis="X", M=M)
    for s in (-1, 1):
        beam(group, "#F4F5F7", (2.0, s * 1.63, 1.5), (3.8, s * 1.5, 3.4), 0.5, M=M)
        ball(group, "#274956", (5.3, s * 0.9, 2.9), 1, sx=1.35, sy=0.65, sz=0.7, M=M, sub=3)
        beam(group, ORANGE, (4.3, s * 1.4, 2.5), (5.2, s * 1.35, 3.5), 0.12, M=M)
        for x in (-2.2, -0.9, 0.4):
            cyl(group, "#4F86BE", (x, s * 1.62, 2.6), 0.32, 0.06, axis="Y", seg=12, mat="glass", M=M)
        beam(group, "#3A414B", (0.8, s * 1.4, 1.0), (0.8, s * 2.4, 0.5), 0.18, M=M)
        cyl(group, TYRE, (0.8, s * 2.4, 0.5), 0.5, 0.35, axis="Y", seg=14, M=M)
    cyl(group, TYRE, (5.0, 0, 0.45), 0.42, 0.3, axis="Y", seg=14, M=M)
    beam(group, "#3A414B", (5.0, 0, 0.9), (5.0, 0, 0.45), 0.16, M=M)
    beam(group, ORANGE, (-3.5, 0, 2.9), (-13.0, 0, 3.6), 1.1, 0.95, M=M)  # tail boom
    beam(group, "#232629", (-3.5, 0, 3.45), (-11.5, 0, 4.0), 0.9, 0.3, M=M)
    beam(group, ORANGE, (-12.6, 0, 3.4), (-14.6, 0, 6.2), 0.9, 0.6, M=M)  # fin
    cyl(group, "#5B6470", (-14.4, -0.7, 5.6), 0.12, 0.6, axis="Y", seg=8, M=M)
    for k in range(3):
        a = k / 3 * math.tau + 0.3
        beam(group, "#3D4651", (-14.4, -1.0, 5.6), (-14.4 + 1.8 * math.cos(a), -1.0, 5.6 + 1.8 * math.sin(a)), 0.4, 0.06, M=M)
    cyl(group, "#3A414B", (0.6, 0, 5.0), 0.35, 1.0, seg=10, M=M)
    for k in range(5):
        a = k / 5 * math.tau + 0.4
        beam(group, "#3D4651", (0.6, 0, 5.5), (0.6 + 10.5 * math.cos(a), 10.5 * math.sin(a), 5.35), 0.55, 0.08, M=M)


def rusak(group, M):
    """РУСАК (image14): boxy orange body, flat panels, huge balloon tyres, 8x8."""
    r, w = 1.12, 1.12
    for x in (3.3, 1.05, -1.2, -3.45):
        for y in (-1.5, 1.5):
            wheel(group, M, x, y, r, r, w)
    aabb(group, INK, -4.2, -0.9, 0.8, 4.1, 0.9, 1.65, M=M)
    aabb(group, ORANGE, -4.3, -1.28, 2.16, 3.7, 1.28, 3.08, M=M)
    aabb(group, ORANGE, -4.3, -1.28, 3.08, 2.7, 1.28, 4.0, M=M)
    beam(group, ORANGE, (2.7, 0, 3.95), (3.7, 0, 3.08), 2.56, 0.2, M=M)
    beam(group, "#274956", (2.76, 0, 3.92), (3.58, 0, 3.19), 2.25, 0.07, M=M)
    beam(group, ORANGE, (2.78, 0, 3.99), (3.63, 0, 3.19), 0.12, M=M)
    for s in (-1, 1):
        for x0, x1 in ((0.5, 2.45), (-1.7, -0.1), (-3.8, -2.3)):
            aabb(group, "#274956", x0, s * 1.29 - 0.02, 3.2, x1, s * 1.29 + 0.02, 3.8, M=M)
        for x in (3.3, 1.05, -1.2, -3.45):
            beam(group, ORANGE, (x - 0.9, s * 1.6, 2.28), (x + 0.9, s * 1.6, 2.28), 0.4, 0.15, M=M)
        beam(group, INK, (2.45, s * 1.3, 3.65), (2.45, s * 1.85, 3.65), 0.1, M=M)
        box(group, INK, (2.45, s * 1.85, 3.5), (0.25, 0.2, 0.55), M=M)
        beam(group, INK, (-4.0, s * 1.1, 4.3), (2.5, s * 1.1, 4.3), 0.1, M=M)
        for x in (-4, -1, 2.5):
            beam(group, INK, (x, s * 1.1, 4.0), (x, s * 1.1, 4.3), 0.08, M=M)
    aabb(group, INK, 3.71, -1.05, 2.55, 3.78, 1.05, 3.0, M=M)
    beam(group, ORANGE, (3.8, -1.1, 2.77), (3.8, 1.1, 2.77), 0.09, M=M)
    for y in (-0.97, 0.97):
        for dy in (-0.13, 0.13):
            cyl(group, "#F7F3DA", (3.8, y + dy, 2.4), 0.10, 0.08, axis="X", M=M)
    beam(group, INK, (4.0, -1.3, 1.65), (4.0, 1.3, 1.65), 0.2, M=M)
    for y in (-0.5, 0.5):
        beam(group, INK, (4.0, y, 1.65), (4.0, y, 2.15), 0.16, M=M)
    beam(group, INK, (4.0, -0.5, 2.15), (4.0, 0.5, 2.15), 0.16, M=M)


def robot(group, M):
    """Robot cart (image15): blue body on two black tracks, flat deck, beacon."""
    for y in (-0.75, 0.75):
        aabb(group, "#24272B", -1.1, y - 0.25, 0.05, 1.1, y + 0.25, 0.65, M=M)
        cyl(group, "#24272B", (1.1, y, 0.35), 0.3, 0.5, axis="Y", seg=14, M=M)
        cyl(group, "#24272B", (-1.1, y, 0.35), 0.3, 0.5, axis="Y", seg=14, M=M)
        s = 1 if y > 0 else -1
        for x in (-0.9, -0.45, 0.0, 0.45, 0.9):
            cyl(group, "#E9EDF1", (x, y + s * 0.26, 0.28), 0.17, 0.05, axis="Y", seg=12, M=M)
        aabb(group, "#2F5FC4", -0.7, y + s * 0.25 - 0.03, 0.4, 0.7, y + s * 0.25 + 0.03, 0.62, M=M)  # side plate
    aabb(group, "#2F5FC4", -0.9, -0.5, 0.35, 0.9, 0.5, 0.95, M=M)  # body
    aabb(group, "#3C6FD8", -1.25, -1.0, 0.95, 1.25, 1.0, 1.12, M=M)  # flat deck
    aabb(group, "#CFD6DE", -1.27, -1.02, 0.95, 1.27, 1.02, 0.99, M=M)
    aabb(group, "#F7F3DA", 1.27, -0.7, 1.0, 1.3, -0.3, 1.07, mat="flat", M=M)  # LED bars
    aabb(group, "#F7F3DA", 1.27, 0.3, 1.0, 1.3, 0.7, 1.07, mat="flat", M=M)
    for x, y in ((1.0, -0.78), (-1.0, 0.78)):  # emergency buttons
        aabb(group, "#F2C230", x - 0.12, y - 0.12, 1.12, x + 0.12, y + 0.12, 1.25, M=M)
        cyl(group, "#E53935", (x, y, 1.3), 0.08, 0.1, seg=10, M=M)
    cyl(group, "#5B6470", (-1.0, -0.78, 1.5), 0.04, 0.7, seg=8, M=M)  # beacon mast
    cyl(group, "#FF8A1E", (-1.0, -0.78, 1.95), 0.13, 0.25, seg=12, mat="flat", M=M)


def pipe_carrier(group, M):
    """Pipe carrier (image16): white cab, slat grille, light bar, blue flatbed."""
    r, w = 1.15, 1.05
    for x in (4.3, 1.9, -2.7, -5.1):
        for y in (-1.5, 1.5):
            wheel(group, M, x, y, r, r, w)
    aabb(group, "#2B2F36", -6.2, -0.9, 0.9, 5.0, 0.9, 1.5, M=M)
    aabb(group, "#F4F5F7", 2.0, -1.25, 1.3, 5.4, 1.25, 2.6, M=M)  # cab lower
    aabb(group, "#F4F5F7", 2.0, -1.2, 2.6, 4.4, 1.2, 3.8, M=M)  # cab upper
    aabb(group, "#F4F5F7", 4.4, -1.2, 2.6, 5.4, 1.2, 2.75, M=M)  # bonnet top
    aabb(group, "#232629", 4.3, -1.15, 2.85, 4.42, 1.15, 3.65, M=M)  # windscreen frame
    aabb(group, "#4F86BE", 4.38, -1.05, 2.9, 4.45, 1.05, 3.6, mat="glass", M=M)
    aabb(group, "#2A5FA8", 4.39, -1.2, 3.62, 4.46, 1.2, 3.8, M=M)  # blue visor band
    for y in [-0.7 + 0.2 * k for k in range(8)]:  # vertical slat grille
        aabb(group, "#232629", 5.4, y - 0.05, 1.5, 5.46, y + 0.05, 2.5, M=M)
    for y in (-1.0, 1.0):
        aabb(group, "#232629", 5.38, y - 0.2, 2.25, 5.45, y + 0.2, 2.5, M=M)
        aabb(group, "#F7F3DA", 5.42, y - 0.13, 2.3, 5.47, y + 0.13, 2.45, mat="flat", M=M)
    aabb(group, "#232629", 5.4, -1.3, 1.1, 5.8, 1.3, 1.35, M=M)  # bumper
    for s in (-1, 1):
        aabb(group, "#4F86BE", 2.6, s * 1.21 - 0.03, 2.8, 4.1, s * 1.21 + 0.03, 3.55, mat="glass", M=M)
        aabb(group, "#2A5FA8", 2.0, s * 1.26 - 0.02, 1.7, 4.0, s * 1.26 + 0.02, 1.95, M=M)
        aabb(group, "#E2573C", 2.0, s * 1.26 - 0.02, 1.95, 3.0, s * 1.26 + 0.02, 2.05, M=M)
        aabb(group, "#232629", 4.3, s * 1.25, 2.9, 4.45, s * 1.6, 3.4, M=M)
    for y in (-1.0, 1.0):  # roof rack + light bar
        beam(group, "#232629", (2.1, y, 4.05), (4.5, y, 4.05), 0.08, M=M)
    aabb(group, "#232629", 4.3, -1.05, 4.0, 4.5, 1.05, 4.2, M=M)
    aabb(group, "#F7F3DA", 4.48, -0.95, 4.05, 4.52, 0.95, 4.15, mat="flat", M=M)
    aabb(group, "#2A5FA8", -6.4, -1.3, 1.3, 1.8, 1.3, 1.6, M=M)  # flatbed
    for s in (-1, 1):
        aabb(group, "#2A5FA8", -6.4, s * 1.3 - 0.05, 1.6, 1.8, s * 1.3 + 0.05, 2.2, M=M)
        for x in (-6.2, -4.1, -2.0, 0.1, 1.7):
            aabb(group, "#1E3E6E", x - 0.08, s * 1.32 - 0.06, 1.6, x + 0.08, s * 1.32 + 0.06, 3.2, M=M)
    aabb(group, "#2A5FA8", 1.7, -1.3, 1.6, 1.85, 1.3, 3.4, M=M)  # headboard
    for row, ys in ((0, (-0.85, -0.28, 0.28, 0.85)), (1, (-0.56, 0.0, 0.56))):
        for y in ys:
            cyl(group, "#9AA3AD", (-2.3, y, 1.88 + row * 0.5), 0.27, 8.0, axis="X", seg=16, M=M)
            cyl(group, "#5B6470", (1.72, y, 1.88 + row * 0.5), 0.17, 0.03, axis="X", seg=12, M=M)
    for x in (-4.5, -0.5):
        beam(group, ORANGE, (x, -1.0, 2.6), (x, 1.0, 2.6), 0.1, M=M)


def at(x, y, rot, s=1.0, z=0.0):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Diagonal((s, s, s, 1))


# vehicles on the quay, all heading east towards the route
VEH = {
    "pipe-carrier": (-35, 2, 0.0, V),
    "rover": (-30, -39, 0.0, V),
    "robot": (-27, -74, 0.0, V * 1.9),
}
HEAD = math.radians(-50)  # 3/4 front towards the wide camera, heading down-right
pipe_carrier("pipe-carrier", at(VEH["pipe-carrier"][0], VEH["pipe-carrier"][1], HEAD, VEH["pipe-carrier"][3], 0.12))
rusak("rover", at(VEH["rover"][0], VEH["rover"][1], HEAD, VEH["rover"][3], 0.12))
robot("robot", at(VEH["robot"][0], VEH["robot"][1], HEAD, VEH["robot"][3], 0.12))
heli("helicopter", at(HPX, HPY, math.radians(-10), PS, 0.18))
PIVOTS = {k: Vector((v[0], v[1], 0)) for k, v in VEH.items()} | {"helicopter": Vector((HPX, HPY, 0))}

# ---- broad steel cargo barge, chamfered bow, freeboard and mooring ------------
BX0, BX1, BY0, BY1, BZ = QX - 37, QX - 3, -88, 12, 1.3
assert 2.5 < (BY1 - BY0) / (BX1 - BX0) < 4.0
outline = [(BX0 + 6, BY0), (BX1 - 6, BY0), (BX1, BY0 + 8), (BX1, BY1 - 8), (BX1 - 6, BY1), (BX0 + 6, BY1), (BX0, BY1 - 8), (BX0, BY0 + 8)]

def hull_layer(color, z0, z1):
    bm = _bm("barge", color, "obj", False)
    low = [bm.verts.new((x, y, z0)) for x, y in outline]
    high = [bm.verts.new((x, y, z1)) for x, y in outline]
    bm.faces.new(list(reversed(low)))
    bm.faces.new(high)
    for i in range(len(low)):
        j = (i + 1) % len(low)
        bm.faces.new((low[i], low[j], high[j], high[i]))

hull_layer("#883F32", -3.5, -0.2)
hull_layer("#254E71", -0.2, BZ)
# Cargo hold coaming leaves an unobstructed perimeter walkway.
aabb("barge", "#9D6350", BX0 + 4, BY0 + 20, BZ, BX1 - 4, BY1 - 15, BZ + 0.12)
for x in (BX0 + 3.7, BX1 - 3.7):
    aabb("barge", "#874B3F", x - 0.25, BY0 + 20, BZ, x + 0.25, BY1 - 15, BZ + 2.3)
for y in (BY0 + 20, BY1 - 15):
    beam("barge", "#874B3F", (BX0 + 4, y, BZ + 1.2), (BX1 - 4, y, BZ + 1.2), 0.5, 2.4)
for y in range(BY0 + 12, BY1 - 8, 14):
    for x in (BX0, BX1):
        cyl("barge", INK, (x, y, -0.1), 1.2, 0.55, axis="X", seg=20)
        cyl("barge", "#566069", (x + (0.3 if x == BX1 else -0.3), y, -0.1), 0.5, 0.05, axis="X", seg=16)
for y in (BY0 + 14, BY1 - 12):
    beam("barge", "#C9B98E", (BX1 - 1, y, BZ + 0.3), (QX + 1.8, y + 4, 1.3), 0.18)
    cyl("barge", INK, (BX1 - 2, y, BZ + 0.5), 0.45, 1, seg=12)
# Compact wheelhouse at the stern, not a building as wide as the vessel.
aabb("barge", "#EAE6D9", BX0 + 7, BY0 + 5, BZ, BX0 + 19, BY0 + 16, BZ + 6)
aabb("barge", "#254E71", BX0 + 6.5, BY0 + 4.5, BZ + 6, BX0 + 19.5, BY0 + 16.5, BZ + 6.6)
for x in (BX0 + 9, BX0 + 13, BX0 + 17):
    aabb("barge", "#274956", x - 1.2, BY0 + 16, BZ + 3.5, x + 1.2, BY0 + 16.1, BZ + 5.1)
for y in (BY0 + 8, BY0 + 12):
    aabb("barge", "#274956", BX0 + 19, y - 1, BZ + 3.5, BX0 + 19.1, y + 1, BZ + 5.1)
cyl("barge", "#667277", (BX0 + 13, BY0 + 9, BZ + 9), 0.14, 5, seg=8)
for row in range(3):
    for k in range(10 - row):
        x = BX0 + 6.5 + k * 2.0 + row
        for y0, y1 in ((BY0 + 23, BY0 + 49), (BY0 + 52, BY1 - 18)):
            cyl("pipes", "#89979F", (x, (y0 + y1) / 2, BZ + 1.0 + row * 1.7), 0.97, y1 - y0, axis="Y", seg=16)
            cyl("pipes", "#354650", (x, y0 - 0.03, BZ + 1.0 + row * 1.7), 0.70, 0.04, axis="Y", seg=16)
for y in (BY0 + 27, BY0 + 45, BY0 + 56, BY1 - 22):
    beam("pipes", "#C49A58", (BX0 + 5, y, BZ + 5.3), (BX1 - 5, y, BZ + 5.3), 0.55, 0.12)
GX, GY, GZ = BX1 - 10, BY1 - 9, BZ


def gift(group, k=2.0):
    def gb(x0, y0, z0, x1, y1, z1, c):
        aabb(group, c, GX + x0 * k, GY + y0 * k, GZ + z0 * k, GX + x1 * k, GY + y1 * k, GZ + z1 * k)
    gb(-1.05, -1.05, 0.0, 1.05, 1.05, 1.7, "#E2B977")
    gb(-0.18, -1.08, 0.0, 0.18, 1.08, 1.73, "#D62B2B")
    gb(-1.08, -0.18, 0.0, 1.08, 0.18, 1.73, "#D62B2B")
    zt = GZ + 1.73 * k
    for a in (0.6, -0.6, math.pi - 0.6, math.pi + 0.6):
        ball(group, "#E53935", (GX + 0.42 * k * math.cos(a), GY + 0.42 * k * math.sin(a), zt + 0.17 * k), 0.38 * k, sx=1.0, sy=0.55, sz=0.5)
    ball(group, "#B71C1C", (GX, GY, zt + 0.12 * k), 0.2 * k)


gift("gift", 3.2)

# ---- tundra dressing ----------------------------------------------------------
SWAMP = (0, 30)  # zone 1, x range
RIVER = [(44, -110), (38, -60), (48, -15), (41, 30), (50, 75), (44, 120)]  # zone 2 centreline


def river_x(y):
    for (x0, y0), (x1, y1) in zip(RIVER, RIVER[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            t = t * t * (3 - 2 * t)
            return x0 + (x1 - x0) * t
    return RIVER[0][0] if y < RIVER[0][1] else RIVER[-1][0]


def spruce(x, y, h):
    cyl("trees", "#5A4632", (x, y, h * 0.1), 0.25, h * 0.2, seg=6)
    for k, (z, r) in enumerate(((0.18, 0.36), (0.42, 0.28), (0.64, 0.19))):
        cyl("trees", "#3F6B4A" if k % 2 else "#4C7D55", (x, y, h * (z + 0.13)), h * r, h * 0.32, r2=h * 0.04, seg=8)


def shrub(x, y, s):
    col = random.choice(["#E8892B", "#F0A32A", "#D9732B", "#C9A23A", "#B5652E"])
    for dx, dy, r in ((0, 0, 1.0), (0.7, 0.3, 0.7), (-0.6, 0.4, 0.75)):
        ball("trees", col, (x + dx * s, y + dy * s, r * s * 0.55), r * s, sz=0.7, sub=1)


def pool(x, y, rx, ry, rot):
    M = Matrix.Translation((x, y, -0.01)) @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Diagonal((rx, ry, 1, 1))
    cyl("swamp", "#6E8F5A", (0, 0, 0), 1.18, 0.05, seg=20, M=M, mat="flat", nolines=True)
    cyl("swamp", "#5E9BC9", (0, 0, 0.03), 1.0, 0.05, seg=20, M=M, mat="water", nolines=True)


def in_clear(x, y):
    if x < -6 and -96 < y < 26:
        return True  # quay
    if abs(x - HPX) < 20 * PS and abs(y - HPY) < 20 * PS:
        return True
    if abs(x - river_x(y)) < 9:
        return True
    if abs(x - AX) < 21 * AK and abs(y - AY) < 16 * AK:
        return True  # АБК yard
    if abs(x - CX - 2) < 32 and abs(y - CY) < 26:
        return True  # camp clearing
    return False


for k in range(70):  # zone 1: chain of bog pools with tussocks and reeds
    x, y = random.uniform(SWAMP[0], SWAMP[1]), random.uniform(-70, 70)
    pool(x, y, random.uniform(2.5, 6.5), random.uniform(1.5, 3.5), random.uniform(0, math.pi))
for k in range(160):
    x, y = random.uniform(SWAMP[0] - 4, SWAMP[1] + 4), random.uniform(-72, 72)
    ball("swamp", random.choice(["#A8A257", "#9C9A4E", "#BDB062"]), (x, y, 0.1), random.uniform(0.6, 1.1), sz=0.6, sub=1)
for k in range(140):
    x, y = random.uniform(SWAMP[0], SWAMP[1]), random.uniform(-70, 70)
    for j in range(3):
        beam("swamp", "#C9B35A", (x + j * 0.3, y, 0), (x + j * 0.3 + random.uniform(-0.3, 0.3), y + random.uniform(-0.3, 0.3), random.uniform(1.4, 2.2)), 0.12)
for k in range(480):
    x, y = random.uniform(-6, 260), random.uniform(-150, 170)
    if in_clear(x, y) or SWAMP[0] < x < SWAMP[1] and random.random() < 0.6:
        continue
    shrub(x, y, random.uniform(1.2, 2.2))
for k in range(220):
    x, y = random.uniform(-6, 260), random.uniform(-150, 170)
    if in_clear(x, y) or SWAMP[0] < x < SWAMP[1]:
        continue
    h = random.uniform(7, 14)
    if random.random() < 0.45:
        spruce(x, y, h)
    else:
        cyl("trees", "#776148", (x, y, h * 0.35), 0.3, h * 0.7, seg=8)
        for z, dx, dy, s in ((0.65, 0, 0, 0.28), (0.48, 0.2, 0, 0.24), (0.55, -0.17, 0.1, 0.23), (0.85, 0, 0, 0.18)):
            ball("trees", random.choice(["#C8A241", "#CB7F36", "#D49B39"]), (x + dx*h, y + dy*h, z*h), h*s, sz=1.25, sub=2)

# zone 2: continuous natural channel; irregular ice shelves, never tiled rails.
ys = list(range(-300, 303, 3))
left = [(river_x(y) - 6.5 - 1.1 * math.sin(y * 0.17), y) for y in ys]
right = [(river_x(y) + 6.5 + 1.3 * math.sin(y * 0.13), y) for y in ys]
def ribbon(group, color, a, b, z, mat="flat"):
    bm = _bm(group, color, mat, True)
    va = [bm.verts.new((x, y, z)) for x, y in a]
    vb = [bm.verts.new((x, y, z)) for x, y in b]
    for i in range(len(a) - 1):
        bm.faces.new((va[i], vb[i], vb[i+1], va[i+1]))
ribbon("river", "#4F9BD9", left, right, 0.02, "water")
for shore, s in ((left, 1), (right, -1)):
    outer = [(x - s * 1.5, y) for x, y in shore]
    ribbon("river_bank", "#928B6E", outer, shore, 0.025)
    inner = [(x + s * (1.1 + 0.8 * math.sin(y * 0.31)), y) for x, y in shore]
    ribbon("ice", "#D6E9E7", shore, inner, 0.04)
for k in range(24):
    y = random.uniform(-120, 120)
    cyl("ice", "#E2EFEA", (river_x(y) + random.uniform(-3, 3), y, 0.06), random.uniform(0.4, 1.1), 0.05, seg=5, mat="flat", nolines=True)

# ---- АБК: compact tall cream industrial block from image12, not an office ----
aabb("abk_ground", "#B4AA91", AX - 16, AY - 13, -0.3, AX + 13, AY + 12, 0.06, mat="tundra", nolines=True)
aabb("abk", "#D9CDB1", AX - 6.5, AY - 6, 0, AX + 6.5, AY + 6, 14.5)
aabb("abk", "#C2B69A", AX - 6.8, AY - 6.3, 14.5, AX + 6.8, AY + 6.3, 15.0)
aabb("abk", "#777B71", AX - 6.3, AY - 5.8, 15.0, AX + 6.3, AY + 5.8, 15.1)
for y in (AY - 6.15, AY + 6.15):
    beam("abk", "#9D9582", (AX - 6.8, y, 15.5), (AX + 6.8, y, 15.5), 0.35, 0.8)
for x in (AX - 6.65, AX + 6.65):
    beam("abk", "#9D9582", (x, AY - 6.2, 15.5), (x, AY + 6.2, 15.5), 0.35, 0.8)
# Lower left annex and exposed industrial services.
aabb("abk", "#CBBEA2", AX - 11, AY, 0, AX - 6.5, AY + 5, 8)
aabb("abk", "#9D9582", AX - 11.3, AY - 0.3, 8, AX - 6.5, AY + 5.3, 8.5)
for z in (4.8, 10.5):
    for y in (AY - 2.8, AY + 2.8):
        for s in (-1, 1):
            aabb("abk", "#3F4A49", AX + s * 6.5, y - 1.1, z, AX + s * 6.6, y + 1.1, z + 1.7)
            beam("abk", "#AEA58E", (AX + s * 6.66, y, z), (AX + s * 6.66, y, z + 1.7), 0.10)
for x, z, w, h in ((AX - 3.7, 0, 2.1, 3.8), (AX + 3.5, 3.2, 2, 1.7), (AX - 8.7, 4.5, 2.5, 1.4)):
    y = AY - (0.05 if x < AX - 6.5 else 6.05)
    aabb("abk", "#38403C", x - w/2, y - 0.08, z, x + w/2, y, z + h)
text("abk_sign", "АБК", (AX - 1.3, AY - 6.15, 11.6), 2.6, (math.pi / 2, 0, 0), "#343B35")
text("abk_sign", "НЕФТЬ · ГАЗ", (AX - 1.0, AY - 6.15, 9.1), 0.9, (math.pi / 2, 0, 0), "#343B35")
for x, y, h in ((AX - 2, AY + 2, 2.3), (AX + 2, AY, 3), (AX + 4, AY + 3, 1.7)):
    aabb("abk", "#858D8A", x - 0.8, y - 0.8, 15.1, x + 0.8, y + 0.8, 15.1 + h)
    for z in (15.8, 16.2, 16.6):
        beam("abk", "#535C59", (x - 0.7, y - 0.82, z), (x + 0.7, y - 0.82, z), 0.08)
for x in (AX - 8, AX + 5.6):
    cyl("abk", "#777F7C", (x, AY - 6.8, 2.5), 0.6, 5, seg=12)
    cyl("abk", "#777F7C", (x + 0.7, AY - 6.8, 4.7), 0.35, 1.4, axis="X", seg=12)
for y in (AY - 3, AY, AY + 3):
    box("abk", "#7D8581", (AX + 7.5, y, 1.7), (1.6, 1.4, 3.4))
    cyl("abk", "#9BA09A", (AX + 8.5, y, 1), 0.25, 2, axis="X", seg=12)
beam("abk", "#7D8581", (AX + 9.5, AY - 5, 1), (AX + 9.5, AY + 5, 1), 0.5)
# Slender lattice aerial, as in the source map.
for x in (-0.5, 0.5):
    beam("abk", "#515C57", (AX - 2 + x, AY + 2, 15.5), (AX - 2 + x * 0.25, AY + 2, 24), 0.10)
for z in range(16, 24):
    beam("abk", "#515C57", (AX - 2.45, AY + 2, z), (AX - 1.55, AY + 2, z + 1), 0.06)
cyl("abk", "#DB4B32", (AX - 2, AY + 2, 24.1), 0.14, 0.3, seg=8)


# chum camp: dark hide chums on a pale trampled clearing, smoke, sledge, reindeer
aabb("camp_ground", "#DCD3B8", CX - 26, CY - 22, -0.3, CX + 28, CY + 18, 0.05, mat="tundra", nolines=True)


def chum(group, x, y, r, h):
    cyl(group, "#5A3E2B", (x, y, h * 0.42), r, h * 0.84, r2=r * 0.16, seg=12)
    cyl(group, "#7B5638", (x, y, h * 0.2), r * 1.02, h * 0.36, r2=r * 0.66, seg=12)  # lighter lower cover band
    for k in range(7):  # poles out of the top
        a = k / 7 * math.tau
        beam(group, "#3A2A1E", (x + r * 0.12 * math.cos(a), y + r * 0.12 * math.sin(a), h * 0.84), (x + r * 0.28 * math.cos(a), y + r * 0.28 * math.sin(a), h * 1.12), 0.14)
    a = math.radians(-110)  # door flap towards the camera
    box(group, "#2A1D14", (x + r * 0.74 * math.cos(a), y + r * 0.74 * math.sin(a), h * 0.17), (0.3, 1.5, h * 0.33), rot=a)


chum("chums", CX, CY + 3, 9.5, 20.0)
chum("chums", CX + 19, CY - 6, 8.0, 17.0)
for k in range(5):
    ball("smoke", "#E8EAEC", (CX + 0.6 * k, CY + 3 + 0.4 * k, 18 + 2.2 * k), 1.2 + 0.5 * k, mat="flat", nolines=True, sub=1)
# sledge (нарта) with a bundle
for y in (-0.8, 0.8):
    beam("camp", "#7B5638", (CX - 20, CY - 14 + y, 0.25), (CX - 12, CY - 14 + y, 0.25), 0.18)
    beam("camp", "#7B5638", (CX - 12, CY - 14 + y, 0.25), (CX - 11, CY - 14 + y, 0.9), 0.18)
aabb("camp", "#9C7A52", CX - 19.6, CY - 15, 0.8, CX - 12.4, CY - 13, 1.0)
aabb("camp", "#5B6E8C", CX - 18.8, CY - 14.7, 1.0, CX - 15.4, CY - 13.3, 2.0)


def reindeer(group, x, y, rot, s=1.0, col="#8A7058"):
    M = at(x, y, rot, s)
    ball(group, col, (0, 0, 1.55), 0.95, sx=1.45, sy=0.72, sz=0.72, M=M)
    ball(group, "#EDE6DA", (0.9, 0, 1.6), 0.5, sx=0.8, sy=0.95, sz=1.0, M=M)  # pale neck ruff
    beam(group, col, (1.0, 0, 1.8), (1.6, 0, 2.4), 0.42, M=M)
    ball(group, col, (1.9, 0, 2.45), 0.33, sx=1.5, sy=0.85, sz=0.85, M=M)
    for dx, dy in ((0.9, -0.35), (0.9, 0.35), (-0.9, -0.35), (-0.9, 0.35)):
        beam(group, "#5E4A3A", (dx, dy, 1.1), (dx, dy, 0.0), 0.17, M=M)
    for s_ in (-1, 1):
        beam(group, "#CDB894", (1.75, s_ * 0.18, 2.7), (1.45, s_ * 0.6, 3.6), 0.1, M=M)
        beam(group, "#CDB894", (1.45, s_ * 0.6, 3.6), (1.95, s_ * 0.85, 4.2), 0.08, M=M)
        beam(group, "#CDB894", (1.55, s_ * 0.45, 3.2), (2.15, s_ * 0.5, 3.4), 0.07, M=M)


reindeer("reindeer", CX - 18, CY + 10, math.radians(-150), 2.6)
reindeer("reindeer", CX - 22, CY + 1, math.radians(-30), 2.4, "#6E5846")
reindeer("reindeer", CX + 24, CY + 10, math.radians(160), 2.5, "#9A8068")


# ---- recipients (variants): readable big figures -------------------------------
def figure(group, c, facing, coat, trim, hood=None, hat=None, s=PEOPLE, wave=False, beard=False):
    M = Matrix.Translation(c) @ Matrix.Rotation(facing, 4, "Z") @ Matrix.Diagonal((s, s, s, 1))
    for dy in (-0.13, 0.13):
        box(group, "#3A2A1E" if hood else NAVY, (0, dy, 0.25), (0.2, 0.18, 0.5), M=M)
    cyl(group, coat, (0, 0, 0.85), 0.36, 0.8, r2=0.24, seg=14, M=M)  # parka / overalls
    cyl(group, trim, (0, 0, 0.5), 0.37, 0.1, seg=14, M=M)
    if hood:
        cyl(group, trim, (0, 0, 0.92), 0.33, 0.07, r2=0.32, seg=14, M=M)
    arm_l = (0.1, 0.62, 1.55) if wave else (0.12, 0.3, 0.6)
    for dy, end in ((-0.3, (0.12, -0.33, 0.62)), (0.3, arm_l)):
        beam(group, coat, (0, dy, 1.15), end, 0.15, M=M)
        ball(group, "#F2C29B" if not hood else trim, end, 0.08, M=M, sub=1)
    ball(group, "#E9B88F", (0, 0, 1.45), 0.21, M=M)
    ball(group, INK, (0.2, -0.07, 1.48), 0.03, M=M, sub=1)
    ball(group, INK, (0.2, 0.07, 1.48), 0.03, M=M, sub=1)
    if beard:
        ball(group, "#4A3426", (0.08, 0, 1.36), 0.13, sx=0.8, sz=0.8, M=M)
    if hood:  # fur hood ring around the face
        ball(group, hood, (-0.05, 0, 1.5), 0.27, sx=0.9, sz=1.05, M=M)
        ball(group, "#F1EBDD", (0.06, 0, 1.47), 0.25, sx=0.55, sz=1.0, M=M)
        ball(group, "#E9B88F", (0.14, 0, 1.45), 0.18, sx=0.6, M=M)
        ball(group, INK, (0.25, -0.06, 1.48), 0.025, M=M, sub=1)
        ball(group, INK, (0.25, 0.06, 1.48), 0.025, M=M, sub=1)
    if hat:
        ball(group, hat, (0, 0, 1.6), 0.23, sz=0.7, M=M)
        cyl(group, hat, (0.04, 0, 1.59), 0.26, 0.03, M=M, seg=16)


FIG_FACE = math.radians(-112)
RECIP = {
    # Майма: girl in a light malitsa with ornament trim, waving beside the big chum
    "alva": dict(c=(CX - 5, CY - 9, 0.05), coat="#235CA2", trim="#C0392B", hood="#F1EBDD", wave=True, s=PEOPLE * 0.9),
    # Хабт: reindeer herder in a dark malitsa next to his reindeer
    "khor": dict(c=(CX - 12, CY - 9, 0.05), coat="#2F6DB5", trim="#F2C230", hood="#8C7A62", wave=True),
    # Арсений: oil worker in navy overalls and an orange hard hat at the АБК door
    "arseniy": dict(c=(AX - 8, AY - 20, 0.05), coat=NAVY, trim=ORANGE, hat=NAVY, wave=True, beard=True),
}
for k, kw in RECIP.items():
    c = kw.pop("c")
    figure("r_" + k, c, FIG_FACE, **kw)
flush()
# static landmarks drawn larger than life around their own centre
bpy.context.view_layer.update()  # text objects need a valid matrix_world first
for g, (x, y, k) in {"pad": (HPX, HPY, PS), "abk": (AX, AY, AK), "abk_sign": (AX, AY, AK), "abk_ground": (AX, AY, AK)}.items():
    for o in GROUPS[g]:
        o.matrix_world = Matrix.Translation((x, y, 0)) @ Matrix.Diagonal((k, k, k, 1)) @ Matrix.Translation((-x, -y, 0)) @ o.matrix_world

# ---- light, world, ink (as scene 4) --------------------------------------------
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

# ---- cameras -------------------------------------------------------------------
FORMATS_SPEC = {
    # name: (res, azimuth, elevation, vehicle turn, keep box)
    "wide": ((1942, 809), float(os.environ.get("WIDE_AZ", -25)), float(os.environ.get("WIDE_EL", 40)), 0, (0.01, 0.03, 0.99, 0.99)),
    "tall": ((948, 1659), float(os.environ.get("TALL_AZ", -62)), float(os.environ.get("TALL_EL", 48)), -50, (0.02, 0.04, 0.98, 0.98)),
}
KEEP = [Vector(p) for p in (
    (BX0, BY0, -3.5), (BX1, BY0, -3.5), (BX0, BY1, -3.5), (BX1, BY1, -3.5), (QX, -94, 0), (-8, -94, 0), (HPX - 14 * PS, HPY + 14 * PS, 0), (HPX + 16 * PS, HPY + 13 * PS, 7 * PS),
    (AX - 16 * AK, AY + 13 * AK, 0), (AX + 19 * AK, AY + 13 * AK, 0), (AX - 2 * AK, AY + 2 * AK, 25 * AK), (AX + 19 * AK, AY - 13 * AK, 0),
    (CX + 28, CY - 22, 0), (CX - 26, CY - 22, 0), (40, 80, 0), (40, -96, 0),
)]


def axes(az, el):
    rot = (math.radians(90 - el), 0, math.radians(az))
    m = Euler(rot, "XYZ").to_matrix()
    return rot, m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0)), m @ Vector((0, 0, -1))


def camera(name, spec):
    (W, H), az, el, _, (u0, v0, u1, v1) = spec
    rot, R, U, F = axes(az, el)
    xs = [p.dot(R) for p in KEEP]
    ys = [p.dot(U) for p in KEEP]
    aspect = W / H
    S = max((max(xs) - min(xs)) / (u1 - u0), (max(ys) - min(ys)) / (v1 - v0) * aspect)
    Hh = S / aspect
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


def turn(deg):
    for g, p in PIVOTS.items():
        m = Matrix.Translation(p) @ Matrix.Rotation(math.radians(deg), 4, "Z") @ Matrix.Translation(-p)
        for o in GROUPS[g]:
            o.matrix_world = m


SS = float(os.environ.get("SS", 1.0))
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = int(os.environ.get("SAMPLES", 16))
VARIANTS = [v for v in os.environ.get("VARIANTS", "alva,khor,arseniy,none").split(",") if v]
manifest = {}
for name in FORMATS:
    spec = FORMATS_SPEC[name]
    cam = camera(name, spec)
    W, H = spec[0]
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = round(W * SS), round(H * SS)
    ls.linestyle.thickness = 1.3 * SS
    turn(spec[3])
    bpy.context.view_layer.update()
    pts = {}
    for g in list(PIVOTS) + ["gift", "chums", "abk", "barge"] + ["r_" + k for k in RECIP]:
        vs = [o.matrix_world @ Vector(c) for o in GROUPS[g] if o.type == "MESH" for c in o.bound_box]
        px = [project(cam, v, W, H) for v in vs]
        pts[g] = [min(p[0] for p in px), min(p[1] for p in px), max(p[0] for p in px), max(p[1] for p in px)]
    manifest[name] = {"width": W, "height": H, "boxes": pts}
    for var in VARIANTS:
        for k in RECIP:
            for o in GROUPS["r_" + k]:
                o.hide_render = k != var
        scene.render.filepath = str(OUT / f"{name}-{var}.png")
        bpy.ops.render.render(write_still=True)
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "lastmile.blend"))
print("LASTMILE OK", FORMATS)
