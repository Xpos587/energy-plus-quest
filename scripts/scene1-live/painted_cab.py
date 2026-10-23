"""Render reference-shaped, camera-projected painted cab meshes (Blender 5).
blender -b -t 6 --python scripts/scene1-live/painted_cab.py -- old-cab SOURCE_DIR OUTPUT_DIR preview|render|guides
SOURCE_DIR contains FAMILY.glb and FAMILY-paint-0..3.png registered to the four guides.
"""
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

family, source, output, mode = sys.argv[sys.argv.index('--') + 1:]
source, output = Path(source), Path(output)
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
source_family = 'crew-cab' if family == 'near-cab' else family
bpy.ops.import_scene.gltf(filepath=str(source / f'{source_family}.glb'))
scene = bpy.context.scene
objects = [o for o in scene.objects if o.type == 'MESH']
assert len(objects) == 1, 'Expected a single reconstructed tractor mesh'
obj = objects[0]
# The reference reconstruction's paint is replaced, not merely outlined.
for material in obj.data.materials:
    nodes, links = material.node_tree.nodes, material.node_tree.links
    texture = next(n for n in nodes if n.type == 'TEX_IMAGE')
    coords = nodes.new('ShaderNodeUVMap'); coords.uv_map = obj.data.uv_layers[0].name
    links.new(coords.outputs['UV'],texture.inputs['Vector'])
    emission = nodes.new('ShaderNodeEmission')
    links.new(texture.outputs['Color'], emission.inputs['Color'])
    links.new(emission.outputs[0], next(n for n in nodes if n.type == 'OUTPUT_MATERIAL').inputs[0])
cameras = []
for position in [(-2,-3,3),(-2,3,3),(2,3,3),(2,-3,3)]:
    bpy.ops.object.camera_add(location=position)
    camera = bpy.context.object
    camera.rotation_euler = (-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 2.7
    cameras.append(camera)
scene.render.engine = 'BLENDER_EEVEE'
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.resolution_percentage = 100
scene.render.resolution_x = scene.render.resolution_y = 800
bpy.context.view_layer.update()
if mode == 'guides':
    scene.render.resolution_x = scene.render.resolution_y = 800
    for index,camera in enumerate(cameras):
        scene.camera = camera
        scene.render.filepath = str(output / f'{family}-guide-{index}.png')
        bpy.ops.render.render(write_still=True)
    sys.exit(0)

mesh = obj.data
bounds = [(min(v.co[i] for v in mesh.vertices),max(v.co[i] for v in mesh.vertices)) for i in range(3)]
height = 2.65 if family == 'old-cab' else 2.78 if family == 'near-cab' else 3.08
uv = mesh.uv_layers.new(name='PaintedCamera')
for index in range(4):
    material = bpy.data.materials.new(f'{family} approved painted view {index}')
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    coords = nodes.new('ShaderNodeUVMap'); coords.uv_map = uv.name
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = bpy.data.images.load(str(source / f'{source_family}-paint-{index}.png'))
    texture.extension = 'EXTEND'
    links.new(coords.outputs['UV'],texture.inputs['Vector'])
    emission = nodes.new('ShaderNodeEmission')
    links.new(texture.outputs['Color'],emission.inputs['Color'])
    links.new(emission.outputs[0],nodes.new('ShaderNodeOutputMaterial').inputs[0])
    obj.data.materials.append(material)
# Assign only genuinely visible camera projections. Hidden chassis surfaces keep
# their reconstructed texture instead of receiving a picture of the cab above them.
depsgraph = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(obj,depsgraph)
directions = [c.location.normalized() for c in cameras]
for face in mesh.polygons:
    center, normal = face.center, face.normal
    body_x = 1.65-(center.x-bounds[0][0])/(bounds[0][1]-bounds[0][0])*4.3
    body_z = .06+(center.z-bounds[2][0])/(bounds[2][1]-bounds[2][0])*(height-.06)
    # Camera-painted wheel images do not belong on neighbouring frame triangles.
    # Mechanical surfaces retain the mesh's coherent original UVs; only the cab is projected.
    if body_x < -.2 or body_z < .95:
        continue
    ranked = sorted(range(4),key=lambda i: normal.dot(directions[i]) + (0.025 if i == 0 else 0),reverse=True)
    selected = None
    for index in ranked:
        if normal.dot(directions[index]) < .05:
            continue
        hit = bvh.ray_cast(center + normal*.0003, directions[index], 5)[0]
        if hit is None:
            selected = index
            break
    if selected is None:
        continue
    face.material_index = selected + 1
    for loop in face.loop_indices:
        point = world_to_camera_view(scene,cameras[selected],obj.matrix_world @ mesh.vertices[mesh.loops[loop].vertex_index].co)
        uv.data[loop].uv = (point.x,point.y)

for vertex in mesh.vertices:
    x,y,z = vertex.co
    vertex.co = (1.65-(x-bounds[0][0])/(bounds[0][1]-bounds[0][0])*4.3,
                 -(y-sum(bounds[1])/2)/(bounds[1][1]-bounds[1][0])*2.26,
                 .06+(z-bounds[2][0])/(bounds[2][1]-bounds[2][0])*(height-.06))
# Match the approved compact tractors: the cab occupies more of the same tested
# footprint; compress the exposed rear frame rather than enlarging trucks off-road.
for vertex in mesh.vertices:
    x = vertex.co.x
    vertex.co.x = 1.65-(1.65-x)*(2.4/1.85) if x > -.2 else -2.65+(x+2.65)*(1.9/2.45)
mesh.update()
scene.camera = cameras[0]
scene.camera.location = (8,-100,120)
scene.camera.rotation_euler = (-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale = 7.5
scene.render.resolution_x = scene.render.resolution_y = 256
scene.render.use_freestyle = True
line = scene.view_layers[0].freestyle_settings.linesets[0]
line.select_crease = False
if line.linestyle is None: line.linestyle = bpy.data.linestyles.new("painted contour")
line.linestyle.color = (.025,.035,.04)
line.linestyle.thickness = .7
# A tractor is not one depth layer: its rear frame must remain below the cargo.
chassis = obj.copy(); chassis.data = obj.data.copy(); scene.collection.objects.link(chassis)
for part, rear in [(obj, False), (chassis, True)]:
    bm = bmesh.new(); bm.from_mesh(part.data)
    remove = []
    for face in bm.faces:
        center = face.calc_center_median()
        is_chassis = center.x < -.65 and center.z < 1.5
        if is_chassis != rear: remove.append(face)
    bmesh.ops.delete(bm, geom=remove, context='FACES')
    bm.to_mesh(part.data); bm.free(); part.data.update()
    part.rotation_mode = 'XYZ'
for heading in ([0,18,36,45,54,63] if mode == 'preview' else range(72)):
    for part in [obj, chassis]: part.rotation_euler.z = heading*math.tau/72
    for part, name in [(obj, family), (chassis, family.replace('-cab','-chassis'))]:
        obj.hide_render = part != obj; chassis.hide_render = part != chassis
        scene.render.filepath = str(output / f'{name}-{heading:02}.png')
        bpy.ops.render.render(write_still=True)
obj.hide_render = chassis.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=str(output / f'{family}.blend'))
