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
COLS = range(-5, 8)  # road lines x = i * P
ROWS = range(-4, 7)  # road lines y = j * P
TRUCK = (16.5, 2.6, 3.9)
WH_DEPTH = 20.0
WH_H = 8.0

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
X0, X1 = COLS[0] * P - P, COLS[-1] * P + P
Y0, Y1 = ROWS[0] * P - P, ROWS[-1] * P + P
for i in COLS:
    box(f"road_v{i}", i * P - ROAD / 2, Y0, i * P + ROAD / 2, Y1, 0, 0.05, C["road"])
for j in ROWS:
    box(f"road_h{j}", X0, j * P - ROAD / 2, X1, j * P + ROAD / 2, 0, 0.05, C["road"])

# Block plates (sidewalk) and content.
import random

random.seed(4)
SPECIAL = {(0, 0): "warehouse", (2, 1): "park"}
for i in list(COLS)[:-1]:
    for j in list(ROWS)[:-1]:
        bx0, by0 = i * P + ROAD / 2, j * P + ROAD / 2
        bx1, by1 = (i + 1) * P - ROAD / 2, (j + 1) * P - ROAD / 2
        box(f"block_{i}_{j}", bx0, by0, bx1, by1, 0, 0.25, C["walk"])
        ix0, iy0, ix1, iy1 = bx0 + WALK, by0 + WALK, bx1 - WALK, by1 - WALK
        kind = SPECIAL.get((i, j))
        if kind == "warehouse":
            # Warehouse at the back of the block, docks face the south road
            # (towards the camera), office tower in the north-east corner.
            # Warehouse near the back of the block, docks face the south road
            # (towards both cameras). Low enough not to hide the lane behind.
            wf = iy1 - 3 - WH_DEPTH  # front wall (dock side)
            box("warehouse", ix0, wf, ix1 - 13, iy1 - 3, 0.25, WH_H, C["wh"])
            box("warehouse_band", ix0 - 0.05, wf - 0.05, ix1 - 12.95, iy1 - 2.95, WH_H - 2, WH_H - 1.2, C["orange"])
            box("warehouse_base", ix0 - 0.05, wf - 0.05, ix1 - 12.95, iy1 - 2.95, 0.25, 1.6, C["brand"])
            for k in range(3):
                dx = ix0 + 3 + k * 8.5
                box(f"dock_door_{k}", dx, wf - 0.4, dx + 5.5, wf + 0.1, 1.0, 5.2, C["brand"])
            # Office in the front-right corner, beside the yard entrance.
            box("office", ix1 - 11, iy0, ix1, iy0 + 13, 0.25, 11, C["office"])
            box("yard", ix0, iy0, ix1 - 13, wf, 0.25, 0.32, C["yard"])
            for k in range(4):
                lx = ix0 + 1.6 + k * 8.5
                box(f"bay_{k}", lx, wf - 18, lx + 0.3, wf - 1, 0.32, 0.34, (0.95, 0.85, 0.3, 1))
        elif kind == "park":
            box("park", ix0, iy0, ix1, iy1, 0.25, 0.35, C["grass"])
            for _ in range(14):
                tree(random.uniform(ix0 + 3, ix1 - 3), random.uniform(iy0 + 3, iy1 - 3), random.uniform(6, 9), random.choice(["tree", "treeY"]))
        else:
            # L-shaped residential block in the south-west corner: both cameras
            # look north-east, so a building only hides its own block interior.
            h1 = random.choice([12, 15, 18])
            h2 = random.choice([9, 12, 15])
            box(f"house_{i}_{j}_s", ix0, iy0, ix0 + random.uniform(30, 40), iy0 + 11, 0.25, h1, C["house"])
            box(f"house_{i}_{j}_w", ix0, iy0 + 13, ix0 + 11, iy0 + random.uniform(26, 36), 0.25, h2, C["house2"])
            for _ in range(4):
                tree(random.uniform(ix0 + 16, ix1 - 3), random.uniform(iy0 + 16, iy1 - 3), random.uniform(5, 7), random.choice(["tree", "treeY"]))


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
ROUTES = {
    "near": rect_loop(0, 0, P, P, LANE, True, 9),
    "old": rect_loop(0, P, 2 * P, 2 * P, LANE, True, 9),
    "old4": rect_loop(P, 0, 3 * P, P, LANE, True, 9),
    "crew": rect_loop(0, 0, 3 * P, 2 * P, -LANE, False, 13),
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
WH_FRONT = P - ROAD / 2 - WALK - 3 - WH_DEPTH
DOCK = Vector((ROAD / 2 + WALK + 3 + 8.5 + 2.75, WH_FRONT - 4, 0.4))  # middle door
EXPRESS = Vector((DOCK.x, WH_FRONT - TRUCK[0] / 2 - 0.8, 0.4))  # backed up to the door
bpy.ops.mesh.primitive_cube_add(size=1, location=(EXPRESS.x, EXPRESS.y, TRUCK[2] / 2 + 0.3))
ex = bpy.context.object
ex.scale = TRUCK
ex.rotation_euler = (0, 0, math.pi / 2)
ex.color = C["express"]
ex.name = "placeholder_express"
truck_objs.append(ex)
AUTOPICK = Vector((ROAD / 2 + WALK + 24, P - ROAD / 2 - WALK - 3 - WH_DEPTH / 2, WH_H + 0.4))
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
    "wide": dict(az=float(__import__("os").environ.get("WIDE_AZ", -24)), el=48, res=(2800, 1200), keep=(0.16, 0.08, 0.60, 0.92)),
    "tall": dict(az=float(__import__("os").environ.get("TALL_AZ", -76)), el=50, res=(1200, 1800), keep=(0.05, 0.20, 0.95, 0.80)),
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
                if ok and obj.name not in ("ground",) and not obj.name.startswith(("road_", "block_", "yard", "bay_", "park")):
                    hits.setdefault(obj.name, 0)
                    hits[obj.name] += 1
        if rounds == 0:
            report["initialOccluders"] = dict(hits)
        if not hits:
            break
        for nm in hits:
            o = bpy.data.objects[nm]
            if nm.startswith("house_") and o.dimensions.z > 7:
                top = o.location.z + o.dimensions.z / 2
                newh = max(6, (top - 0.25) * 0.75)
                o.scale.z = newh
                o.location.z = 0.25 + newh / 2
            elif nm == "office" and o.dimensions.z > 7:
                o.scale.z = o.dimensions.z - 1.5
                o.location.z = 0.25 + o.scale.z / 2
            elif nm.startswith(("crown", "trunk", "house_")):
                bpy.data.objects.remove(o)
            else:
                report.setdefault("unfixed", set()).add(nm)
    report["remaining"] = hits
    for o in helpers:
        o.hide_viewport = False
    report.pop("unfixed", None)
    return report


def project(cam, res, p):
    from bpy_extras.object_utils import world_to_camera_view

    v = world_to_camera_view(scene, cam, Vector((p[0], p[1], p[2] if len(p) > 2 else 0.4)))
    return [round(v.x, 5), round(1 - v.y, 5)]


occlusion = clear_occluders()
print("OCCLUSION", occlusion)

manifest = {"grid": {"P": P, "road": ROAD, "lane": LANE}, "speedKmh": SPEED_KMH, "occlusion": occlusion, "plates": {}}
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
    }
manifest["routeLengthM"] = {rid: round(length(pts), 1) for rid, pts in ROUTES.items()}
(OUT / "blockout.json").write_text(json.dumps(manifest, indent=1))
if not __import__("os").environ.get("NO_RENDER"):
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "blockout.blend"))
print("OK", manifest["routeLengthM"])
