import bpy
import json
import math
import pathlib
from mathutils import Vector

P = pathlib.Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(P / 'green-tractor.glb'))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
points = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector([min(p[i] for p in points) for i in range(3)])
hi = Vector([max(p[i] for p in points) for i in range(3)])
centre = (lo + hi) / 2
extent = max(hi - lo)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = True
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.6

for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    nodes, links = m.node_tree.nodes, m.node_tree.links
    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if bsdf is None or output is None:
        continue
    colour = bsdf.inputs['Base Color']
    pigment = nodes.new('ShaderNodeEmission')
    pigment.inputs['Color'].default_value = colour.default_value
    pigment.inputs['Strength'].default_value = 1
    if colour.is_linked:
        links.new(colour.links[0].from_socket, pigment.inputs['Color'])
    # Use the generated painted texture directly, without metallic relighting.
    links.new(pigment.outputs[0], output.inputs['Surface'])

bpy.ops.object.camera_add()
camera = bpy.context.object
camera.name = 'Fixed map test camera'
camera.data.type = 'ORTHO'
camera.data.ortho_scale = extent * 1.27
scene.camera = camera
for i, angle in enumerate([0, 60, 120, 180, 240, 300]):
    a = math.radians(angle)
    camera.location = centre + Vector((math.cos(a), math.sin(a), 0.82)) * extent * 2
    camera.rotation_euler = (centre - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(P / ('view-%03d.png' % angle))
    bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=str(P / 'green-tractor-textured.blend'))
(P / 'geometry-receipt.json').write_text(json.dumps({
    'input': 'green-tractor.glb',
    'bounds': {'minimum': list(lo), 'maximum': list(hi)},
    'mesh_objects': [o.name for o in meshes],
    'triangles': sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),
    'resolution': [900, 900],
    'texture_render': 'unlit original generated texture',
    'animation': False,
}, indent=2))
