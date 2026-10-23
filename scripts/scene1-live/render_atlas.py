"""Blender 5: heading views from repaired source meshes, never rotated flat artwork.
Run: blender -b -t 6 --python scripts/scene1-live/render_atlas.py -- /tmp/scene1-atlas [preview]
"""
import bpy
import bmesh
import math
import sys
from pathlib import Path
from mathutils import Vector

SOURCE = Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-12/city-repaired.blend')
args = sys.argv[sys.argv.index('--') + 1:]
OUT = Path(args[0]); OUT.mkdir(parents=True, exist_ok=True)
preview = 'preview' in args
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
roots = [o for o in s.objects if o.name.startswith('truck-')]
keep = set(roots)
for root in roots:
    keep.update(root.children_recursive)
for obj in list(s.objects):
    if obj not in keep:
        bpy.data.objects.remove(obj, do_unlink=True)
for root in roots:
    root.animation_data_clear(); root.location = (0, 0, 0); root.rotation_euler = (0, 0, 0); root.scale = (1, 1, 1)
for obj in list(s.objects):
    if obj.type == 'FONT' or obj.name.startswith('FX'):
        bpy.data.objects.remove(obj, do_unlink=True)

# The archived blockout's boxes have inward face winding. Correct the source
# normals before lighting/roof classification, rather than painting over them.
for obj in s.objects:
    if obj.type != 'MESH': continue
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data); bm.free(); obj.data.update()

def material(name, color, worn=False, paint=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = m.node_tree.nodes; l = m.node_tree.links; n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    diffuse = n.new('ShaderNodeBsdfDiffuse'); diffuse.inputs['Color'].default_value = (1, 1, 1, 1)
    rgb = n.new('ShaderNodeShaderToRGB'); l.new(diffuse.outputs[0], rgb.inputs[0])
    ramp = n.new('ShaderNodeValToRGB'); ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    for index, (position, factor) in enumerate(([(0, .72), (.45, .88), (1.05, 1)] if paint else [(0, .52), (.45, .80), (1.05, 1)])):
        e = ramp.color_ramp.elements[0] if index == 0 else ramp.color_ramp.elements.new(position)
        e.position = position; e.color = tuple(c * factor for c in color) + (1,)
    l.new(rgb.outputs[0], ramp.inputs[0])
    final = ramp.outputs[0]
    if paint:
        texture = n.new('ShaderNodeTexImage')
        texture.image = bpy.data.images.load(str(Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-22-live') / f'{paint}-trailer-paint.png'))
        texture.projection = 'FLAT'
        coords = n.new('ShaderNodeUVMap'); coords.uv_map = 'PaintedPanels'
        l.new(coords.outputs['UV'],texture.inputs['Vector'])
        mix = n.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1
        l.new(final,mix.inputs[1]); l.new(texture.outputs['Color'],mix.inputs[2]); final = mix.outputs[0]
    if worn:
        tex = n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = 95; tex.inputs['Detail'].default_value = 2
        mix = n.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = .28
        l.new(final, mix.inputs[1]); l.new(tex.outputs['Fac'], mix.inputs[2]); final = mix.outputs[0]
    emission = n.new('ShaderNodeEmission'); l.new(final, emission.inputs[0]); l.new(emission.outputs[0], out.inputs[0])
    return m

# Linear RGB; Standard display keeps the approved slate/blue and cream family.
old = material('slate worn enamel', (.19, .35, .47), True)
blue = material('blue enamel', (.035, .26, .48))
cream = material('cream trailer', (1, 1, 1), paint='new')
worn = material('maintained old cream trailer', (1, 1, 1), paint='old')
old_roof = material('old ivory painted roof',(1,1,1),paint='old-roof')
new_roof = material('new ivory painted roof',(1,1,1),paint='new-roof')
metal = material('ink gray metal', (.18, .23, .25))
rubber = material('charcoal rubber', (.019, .026, .032))
glass = material('blue reflected glass', (.045, .085, .105))
lamp = material('warm headlight', (.86, .82, .65))
skin = material('warm natural skin', (.72, .43, .25))
shirt = material('crew blue shirts', (.03, .13, .24))
hair = material('crew brown hair', (.08, .045, .027))
for obj in s.objects:
    if obj.type != 'MESH': continue
    root = obj
    while root.parent: root = root.parent
    number = int(root.name.split('-')[1])
    previous = obj.data.materials[0].name if obj.data.materials else ''
    chosen = old if number in (1, 4) else blue
    if 'cargo' in previous: chosen = worn if number in (1, 4) else cream
    elif 'rubber' in previous: chosen = rubber
    elif 'glass' in previous: chosen = glass
    elif 'headlamp' in previous: chosen = lamp
    elif 'metal' in previous: chosen = metal
    if 'bumper' in obj.name: chosen = metal
    elif 'skin' in previous: chosen = skin
    elif 'workwear' in previous: chosen = shirt
    elif 'hair' in previous: chosen = hair
    for slot in obj.material_slots: slot.link = 'OBJECT'; slot.material = chosen
    if 'long semitrailer' in obj.name:
        obj.data = obj.data.copy()
        obj.data.materials.append(old_roof if number in (1,4) else new_roof)
        uv = obj.data.uv_layers.new(name='PaintedPanels')
        bounds=[(min(v.co[i] for v in obj.data.vertices),max(v.co[i] for v in obj.data.vertices)) for i in range(3)]
        for polygon in obj.data.polygons:
            axes = (0,1) if abs(polygon.normal.z) > .5 else (0,2) if abs(polygon.normal.y) > .5 else (1,2)
            if polygon.normal.z > .5: polygon.material_index = len(obj.data.materials)-1
            for loop in polygon.loop_indices:
                vertex=obj.data.vertices[obj.data.loops[loop].vertex_index].co
                uv.data[loop].uv=tuple((vertex[i]-bounds[i][0])/(bounds[i][1]-bounds[i][0]) for i in axes)
    if obj.name.startswith(('3 windshield', '3 side window')):
        # Genuine cavity already exists in repaired source; transparent front glass reveals seated figures.
        m = bpy.data.materials.new('transparent crew glass'); m.use_nodes = True
        nodes = m.node_tree.nodes; nodes.clear(); links = m.node_tree.links
        out = nodes.new('ShaderNodeOutputMaterial'); transparent = nodes.new('ShaderNodeBsdfTransparent')
        tint = nodes.new('ShaderNodeEmission'); tint.inputs[0].default_value = (.16, .30, .38, 1)
        mix = nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value = .15
        links.new(transparent.outputs[0], mix.inputs[1]); links.new(tint.outputs[0], mix.inputs[2]); links.new(mix.outputs[0], out.inputs[0])
        m.surface_render_method = 'DITHERED'
        for slot in obj.material_slots: slot.material = m

# Readable truck fittings and panel ink are source geometry, so they remain correct in every view.
def detail(name, root, location, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj=bpy.context.object; obj.name=name; obj.parent=root; obj.location=location
    obj.scale=size; obj.data.materials.append(mat)
    return obj
for number in (2,3,4):
    root=bpy.data.objects[f'truck-{number}-tractor']
    roof=2.52 if number==4 else 3.08 if number==3 else 2.95
    detail(f'{number} roof hatch rim',root,(-.12,0,roof+.025),(.65,.75,.04),metal)
    detail(f'{number} roof hatch enamel',root,(-.12,0,roof+.05),(.57,.67,.025),old if number==4 else blue)
    for side in (-1,1):
        detail(f'{number} roof gutter',root,(.08,side*.83,roof+.004),(1.7,.018,.018),metal)
    for side in (-1,1):
        detail(f'{number} lower door crease',root,(.08,side*.912,1.35),(1.25,.017,.023),rubber)
        detail(f'{number} front wiper',root,(1.45,side*.37,1.58 if number==4 else 1.9),(.024,.55,.035),rubber)
        detail(f'{number} front amber signal',root,(1.535,side*.74,1.47 if number==4 else 1.57),(.035,.16,.08),lamp)
# Small physical fittings and glazing highlights survive every heading; they
# are not photos of wheels, doors or people projected onto adjacent triangles.
reflection = material('painted sky reflection',(.24,.39,.44))
for number in (2,3,4):
    root=bpy.data.objects[f'truck-{number}-tractor']
    detail(f'{number} cream number plate',root,(1.64,0,.67),(.012,.48,.13),lamp)
    detail(f'{number} bumper upper trim',root,(1.637,0,.81),(.015,1.70,.04),rubber)
    for side in (-1,1):
        detail(f'{number} door lower moulding',root,(.15,side*.917,1.12),(1.33,.025,.038),metal)
        if number != 4: continue
        # Old low cab windshield lies on x=1.441 at z=1.5, raking back .053/.81.
        verts=[]
        for y,z in [(side*.08,2.27),(side*.35,2.27),(side*.69,1.77),(side*.69,1.61)]:
            verts.append((1.446-(z-1.5)*.053/.81,y,z))
        mesh=bpy.data.meshes.new('windshield reflection'); mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.update()
        obj=bpy.data.objects.new(f'{number} reflected sky {side}',mesh);s.collection.objects.link(obj);obj.parent=root;mesh.materials.append(reflection)
bpy.ops.object.camera_add(location=(8, -100, 120))
cam = bpy.context.object; cam.name = 'atlas camera'
cam.rotation_euler = (-cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 12; s.camera = cam
bpy.ops.object.light_add(type='SUN', location=(-30, -20, 70))
sun = bpy.context.object; sun.rotation_euler = (math.radians(28), math.radians(-25), math.radians(-30)); sun.data.energy = 1.6
s.world.color = (.25, .25, .25)
s.render.engine = 'BLENDER_EEVEE'
s.render.resolution_x = s.render.resolution_y = 512; s.render.resolution_percentage = 100
s.render.film_transparent = True; s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
s.view_settings.view_transform = 'Standard'; s.view_settings.look = 'None'; s.view_settings.exposure = 0; s.view_settings.gamma = 1
s.render.use_freestyle = True; s.render.line_thickness = 1
line = s.view_layers[0].freestyle_settings.linesets[0]
line.linestyle.color = (.008, .012, .014); line.linestyle.thickness = 2.2
s.render.fps = 24
# Keep authored cab/glass/driver/wheel geometry, not camera-painted copies of it.
# Each front wheel turns about its own kingpin; rims stay attached to the tire.
wheel_pivots = {}
for number in (2,3,4):
    root = bpy.data.objects[f'truck-{number}-tractor']
    pivots = []
    for side in (-1,1):
        pivot = bpy.data.objects.new(f'{number} front steering {side}',None)
        s.collection.objects.link(pivot); pivot.parent = root
        pivot.location = (.77,side*.73,.44)
        for obj in list(root.children):
            if any(word in obj.name for word in ('tire','hub','rim recess')) and obj.location.x > .4 and obj.location.y*side > 0:
                position = obj.location.copy()
                obj.parent = pivot; obj.location = position - pivot.location
        pivots.append(pivot)
    wheel_pivots[number] = pivots
families = [('old',4),('near',2),('crew',3)]
passes = [(f'{name}-{part}',number,part) for name,number in families for part in ('cab','cab-turn','chassis')]
passes += [('old-trailer',4,'trailer'),('new-trailer',3,'trailer')]
for family, number, role in passes:
    if "trailers" in args and role != 'trailer': continue
    cam.location = (8,-100,121.7 if role == 'trailer' else 120)
    cam.data.ortho_scale = 8.4 if role == 'trailer' else 7.5
    selected = bpy.data.objects[f'truck-{number}-{"trailer" if role == "trailer" else "tractor"}']
    for root in roots:
        for obj in [root,*root.children_recursive]:
            obj.hide_render = root != selected
            if root == selected and role != 'trailer' and obj.type == 'MESH':
                rear = ('ladder frame' in obj.name or 'fifth wheel' in obj.name or
                    'fuel tank' in obj.name or 'rear mudguard' in obj.name or
                    (obj.parent == root and obj.location.x < -.8 and obj.location.z < 1.5))
                obj.hide_render = rear != (role == 'chassis')
    if role != 'trailer':
        for pivot in wheel_pivots[number]: pivot.rotation_euler.z = -.5 if role == 'cab-turn' else 0
    for angle in ([0,18,36,45,54,63] if preview else range(72)):
        selected.rotation_euler.z = angle * math.tau / 72
        center = Vector((3.05,0,0)) if role == 'trailer' else Vector((0,0,0))
        selected.location = selected.rotation_euler.to_matrix() @ center
        s.render.filepath = str(OUT / f'{family}-{angle:02d}.png')
        bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'atlas.blend'))
