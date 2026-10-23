"""Local city-distance successor. No route, camera, vehicle-scale or source edits.

blender -b -t 4 --python scripts/scene1-live/readable_city.py -- SOURCE OUTPUT [--motion]
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:]
source, output = Path(args[0]), Path(args[1])
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s = bpy.context.scene
s.frame_set(1)

def material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = 0.82
    return m

ink = material('READ roof numeral ink', (0.012, 0.035, 0.055))
blue = material('READ loading apron', (0.055, 0.23, 0.34))
yellow = material('READ gate safety yellow', (0.92, 0.60, 0.09))

def box(name, center, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    o.data.materials.append(mat)
    return o

# Road clearance is unchanged: these are flush markings inside the existing yard.
for x in (-44.33, -38.61):
    box('READ dock apron', (x, 4.5, 0.165), (4.35, 11.6, 0.012), blue)
    box('READ dock stop line', (x, 9.5, 0.18), (4.35, 0.24, 0.012), yellow)
for name in ('FIX gate post', 'FIX gate post.001'):
    o = s.objects[name]
    o.data = o.data.copy()
    o.data.materials.clear()
    o.data.materials.append(yellow)
    # Existing bollard geometry and opening stay untouched.
for y in (-18.7, -7.3):
    box('READ gate threshold edge', (-33.4, y, 0.165), (2.8, 0.3, 0.012), yellow)

# Worn paint on existing old cabs and cargo: no added smoke or roof obstacles.
for i in (1, 4):
    for name in (f'FIX cab {i}',):
        m = bpy.data.materials.get(name)
        if not m or not m.use_nodes:
            continue
        nodes, links = m.node_tree.nodes, m.node_tree.links
        shader = nodes.get('Principled BSDF')
        base = tuple(shader.inputs['Base Color'].default_value)
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 5
        noise.inputs['Detail'].default_value = 2
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.28
        ramp.color_ramp.elements[0].color = (*[v * 0.5 for v in base[:3]], 1)
        ramp.color_ramp.elements[1].position = 0.43
        ramp.color_ramp.elements[1].color = base
        links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], shader.inputs['Base Color'])
        shader.inputs['Roughness'].default_value = 0.95

numbers = [s.objects[f'vehicle {i} identification'] for i in range(1, 5)]
font = bpy.data.fonts.load('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf')
font.pack()
for o in numbers:
    o.data = o.data.copy()
    o.data.font = font
    o.data.size = 3.15
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.materials.clear()
    o.data.materials.append(ink)

# Numerals remain flat on their own roofs, upright relative to the camera.
# Bake rotations into the saved file, including the loop endpoint; no handlers.
tracks = []
max_angle_error = 0
for frame in range(1, s.frame_end + 2):
    s.frame_set(frame)
    row = []
    for o in numbers:
        parent_angle = o.parent.matrix_world.to_euler().z
        o.rotation_euler.z = s.camera.rotation_euler.z - parent_angle
        o.keyframe_insert('rotation_euler', frame=frame)
    bpy.context.view_layer.update()
    for o in numbers:
        origin = world_to_camera_view(s, s.camera, o.matrix_world.translation)
        top = world_to_camera_view(s, s.camera, o.matrix_world @ Vector((0, 1, 0)))
        row.append([origin.x, 1-origin.y])
        max_angle_error = max(max_angle_error, abs(top.x-origin.x))
    tracks.append(row)
assert max_angle_error < 0.00001, max_angle_error
s.frame_set(1)
s.render.engine = 'BLENDER_EEVEE'
s.render.resolution_percentage = 100
s.eevee.taa_render_samples = 16
s.render.resolution_x = 1008
s.render.resolution_y = 700
s.render.image_settings.file_format = 'PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'readable-city.blend'))
(output / 'readability.json').write_text(json.dumps({
    'source': str(source), 'fps': s.render.fps, 'frames': s.frame_end,
    'seconds': s.frame_end / s.render.fps, 'size': [1008, 700],
    'numeral_screen_vertical_error': max_angle_error,
    'projected_roof_centers': tracks,
    'preserved': ['camera', 'route keyframes', 'vehicle scale', 'warehouse geometry', 'gate clearance'],
}, indent=2))
s.render.filepath = str(output / 'after.png')
bpy.ops.render.render(write_still=True)
if '--motion' in args:
    frames = output / 'frames'
    frames.mkdir(exist_ok=True)
    s.render.filepath = str(frames / '####')
    bpy.ops.render.render(animation=True)
