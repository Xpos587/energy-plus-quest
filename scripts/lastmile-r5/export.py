"""R5 runtime export from a final build.py scene.blend:
centred overscan around the PERSP cameras, a plate without the main rotor blades, a hard semantic ID
pass and an RGBA main-rotor sprite cycle (5 blades -> 72 deg period) for the runtime animation layer.
blender -b <final>/scene.blend --python-exit-code 1 -t 12 --python scripts/lastmile-r5/export.py -- <final> <out> [draft]
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
args = sys.argv[sys.argv.index('--') + 1:]
src, out = Path(args[0]).resolve(), Path(args[1]).resolve(); out.mkdir(parents=True, exist_ok=True)
DRAFT = 'draft' in args
manifest = json.loads((src / 'manifest.json').read_text())
scene = bpy.context.scene
LAYOUT = {'wide': (2400, 1800), 'tall': (1700, 2100)}       # same logical overscan as R4 (expandedArtwork.ts)
ROTOR_FRAMES = 12

scene.eevee.taa_render_samples = 8 if DRAFT else 64
scene.render.resolution_percentage = 100

# ---- overscan sees past the 700x1150 m terrain: extend land/harbour with flat continuations ----
terrain = next(o for o in scene.objects if o.get('group') == 'tundra')
me = terrain.data; n = len(me.vertices)
col = [0.0] * (4 * n); me.color_attributes['col'].data.foreach_get('color', col)
xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
ytop = max(ys) - 30
edge = [i for i in range(n) if ys[i] > ytop or abs(xs[i]) > 330]
far = tuple(sum(col[4 * i + k] for i in edge) / len(edge) for k in range(3))
edge_z = sum(me.vertices[i].co.z for i in edge) / len(edge)
ax, bx, by = min(xs) + 1, max(xs) - 1, max(ys) - 1       # frame around the terrain: never covers river channels
land = bpy.data.meshes.new('far land'); land.from_pydata([(-4000, -69, 0), (ax, -69, 0), (ax, by, 0), (-4000, 6000, 0), (bx, -69, 0), (4000, -69, 0), (4000, 6000, 0), (bx, by, 0)],
    [], [(0, 1, 2, 3), (4, 5, 6, 7), (2, 7, 6, 3)])
land.materials.append(bpy.data.materials['obj']); land_ob = bpy.data.objects.new('far land', land); scene.collection.objects.link(land_ob)
land_ob.location.z = edge_z - .08; land_ob.color = (*far, 1); land_ob['group'] = 'far_land'
harbour = next(o for o in scene.objects if o.get('group') == 'harbor_water')
for v in harbour.data.vertices: v.co.x *= 12; v.co.y = v.co.y if v.co.y > -100 else -4000

# ---- main rotor: the 5 long loose parts of the dark blade batch --------------------
blade_src = next(o for o in scene.objects if o.get('group') == 'helicopter' and o.name.startswith('helicopter|#3D4651'))
bm = bmesh.new(); bm.from_mesh(blade_src.data); bm.verts.ensure_lookup_table()
islands, seen = [], set()
for v in bm.verts:
    if v.index in seen: continue
    stack, part = [v], []
    seen.add(v.index)
    while stack:
        a = stack.pop(); part.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in seen: seen.add(b.index); stack.append(b)
    islands.append(part)
mw = blade_src.matrix_world
main = [p for p in islands if max((mw @ a.co - mw @ b.co).length for a in p for b in p) > 6]
assert len(main) == 5, [len(p) for p in islands]
main_idx = {v.index for p in main for v in p}
blade_world = [mw @ v.co for p in main for v in p]
hub = sum(blade_world, Vector()) / len(blade_world)      # 5 equal blades at 72 deg: centroid = hub
rot_me = bpy.data.meshes.new('main rotor'); rbm = bmesh.new()
remap = {i: rbm.verts.new(mw @ bm.verts[i].co - hub) for i in sorted(main_idx)}
for f in bm.faces:
    if all(v.index in main_idx for v in f.verts): rbm.faces.new([remap[v.index] for v in f.verts])
rbm.to_mesh(rot_me); rbm.free()
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index in main_idx], context='VERTS')
bm.to_mesh(blade_src.data); bm.free()
rotor = bpy.data.objects.new('main rotor', rot_me); scene.collection.objects.link(rotor)
rot_me.materials.append(blade_src.data.materials[0]); rotor.color = blade_src.color
rotor.location = hub; rotor['group'] = 'rotor'
rotor.hide_render = True                                  # plate: no blades, no blade shadow

# ---- centred overscan for perspective cameras ------------------------------------
def project(cam, W, H, p):
    v = world_to_camera_view(scene, cam, p); return Vector((v.x * W, (1 - v.y) * H))
probe = [o.matrix_world @ Vector(c) for o in scene.objects if o.get('group') in manifest['choices'] for c in o.bound_box] + [hub]
layout = {}
for name, (W, H) in LAYOUT.items():
    cam = bpy.data.objects[name]; cd = cam.data; scene.camera = cam
    w0, h0 = manifest['cameras'][name]['resolution']
    scene.render.resolution_x, scene.render.resolution_y = w0, h0; bpy.context.view_layer.update()
    before = [project(cam, w0, h0, p) for p in probe]
    k0 = max(w0, h0); k1 = max(W, H)
    cd.sensor_fit = 'AUTO'; cd.sensor_width *= k1 / k0; cd.shift_x *= k0 / k1; cd.shift_y *= k0 / k1
    scene.render.resolution_x, scene.render.resolution_y = W, H; bpy.context.view_layer.update()
    dx, dy = (W - w0) / 2, (H - h0) / 2
    err = max((project(cam, W, H, p) - (b + Vector((dx, dy)))).length for p, b in zip(probe, before))
    assert err < .05, (name, err)
    objects = {}
    for g in manifest['choices']:
        pts = [project(cam, W, H, o.matrix_world @ Vector(c)) for o in scene.objects if o.get('group') == g for c in o.bound_box]
        objects[g] = [min(p.x for p in pts), min(p.y for p in pts), max(p.x for p in pts), max(p.y for p in pts)]
    layout[name] = dict(width=W, height=H, original=dict(x=dx, y=dy, width=w0, height=h0), objects=objects,
                        hub=list(project(cam, W, H, hub)), projection_error_px=err)
    scene.render.filepath = str(out / f'{name}-plate.png'); scene.render.film_transparent = False
    scene.render.image_settings.color_mode = 'RGB'; bpy.ops.render.render(write_still=True)
    print('PLATE', name, round(err, 4), flush=True)

# ---- rotor sprite cycle: blades alone, RGBA, same camera -------------------------
hidden = [o for o in scene.objects if o.type in ('MESH', 'FONT', 'CURVE') and not o.hide_render]
for o in hidden: o.hide_render = True
rotor.hide_render = False
scene.render.film_transparent = True; scene.render.image_settings.color_mode = 'RGBA'
scene.eevee.taa_render_samples = 8 if DRAFT else 32
axis = Vector((0, 0, 1))
for name, (W, H) in LAYOUT.items():
    scene.camera = bpy.data.objects[name]; scene.render.resolution_x, scene.render.resolution_y = W, H
    for k in range(ROTOR_FRAMES):
        rotor.rotation_euler = (Matrix.Rotation(math.radians(72) * k / ROTOR_FRAMES, 4, axis)).to_euler()
        scene.render.filepath = str(out / f'{name}-rotor-{k:02d}.png'); bpy.ops.render.render(write_still=True)
for o in hidden: o.hide_render = False
rotor.rotation_euler = (0, 0, 0); rotor.hide_render = True

# ---- hard semantic ID (no lighting, 1 sample) ------------------------------------
PALETTE = {g: (60 + 40 * i, 255 - 30 * i, (90 * i) % 256) for i, g in enumerate(manifest['choices'])}
PALETTE |= {'barge': (255, 0, 255), 'water': (0, 0, 255), 'ice': (0, 255, 255)}
WATER = {'harbor_water', 'river', 'creek'}
def lin(c): c = c / 255; return ((c + .055) / 1.055) ** 2.4 if c > .04045 else c / 12.92
for o in scene.objects:
    g = o.get('group'); g = 'water' if g in WATER else g
    o.color = tuple(lin(c) for c in PALETTE[g]) + (1,) if g in PALETTE else (0, 0, 0, 1)
m = bpy.data.materials.new('semantic ID'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
em = nt.nodes.new('ShaderNodeEmission'); info = nt.nodes.new('ShaderNodeObjectInfo'); mo = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(info.outputs['Color'], em.inputs[0]); nt.links.new(em.outputs[0], mo.inputs[0])
bpy.context.view_layer.material_override = m
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0
scene.render.film_transparent = False; scene.render.image_settings.color_mode = 'RGB'; scene.render.dither_intensity = 0
scene.render.filter_size = 0; scene.eevee.taa_render_samples = 1; scene.view_settings.view_transform = 'Standard'
for name, (W, H) in LAYOUT.items():
    scene.camera = bpy.data.objects[name]; scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.filepath = str(out / f'{name}-id.png'); bpy.ops.render.render(write_still=True)
(out / 'layout.json').write_text(json.dumps(dict(source=str(src), views=layout, id_palette=PALETTE, rotor_frames=ROTOR_FRAMES,
    rotor_period_deg=72), indent=2) + '\n')
print('R5_EXPORT_COMPLETE', flush=True)
