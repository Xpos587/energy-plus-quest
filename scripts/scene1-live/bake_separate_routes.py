"""Bake certified motion into the readable city; preserve camera and static art.

blender -b -t 4 --python SCRIPT -- SOURCE OUTPUT ARCHIVE [--motion]
"""
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

args = sys.argv[sys.argv.index('--')+1:]
source, output, archive = map(Path, args[:3])
report = json.loads((output/'route-check.json').read_text())
assert report['passed']
motion = np.load(output/'motion.npy')
bpy.ops.wm.open_mainfile(filepath=str(source))
s = bpy.context.scene
roots = [s.objects[f'truck-{i}-{part}'] for i in range(1, 5) for part in ('tractor', 'trailer')]
numbers = [s.objects[f'vehicle {i} identification'] for i in range(1, 5)]
moving = {o.name for root in roots for o in [root, *root.children_recursive]}


def static_snapshot():
    return {o.name: ([tuple(v.co) for v in o.data.vertices], [tuple(row) for row in o.matrix_world])
            for o in s.objects if o.type == 'MESH' and o.name not in moving}


original_static = static_snapshot()
original_camera = (tuple(s.camera.location), tuple(s.camera.rotation_euler), s.camera.data.ortho_scale)
for o in roots+numbers:
    o.animation_data_clear()
for o in numbers:
    # Move the roof marking toward the cab, away from roofline occlusion in turns.
    o.location.x = -1.8
for frame, poses in enumerate(motion, 1):
    for o, pose in zip(roots, poses):
        o.location = pose[:3]
        o.rotation_euler.z = pose[3]
        o.keyframe_insert('location', frame=frame)
        o.keyframe_insert('rotation_euler', frame=frame)
for o in roots:
    for layer in o.animation_data.action.layers:
        for strip in layer.strips:
            channelbag = strip.channelbag(o.animation_data.action_slot)
            if channelbag:
                for curve in channelbag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation = 'LINEAR'
tracks = []
max_vertical_error = 0
for frame in range(1, len(motion)+1):
    s.frame_set(frame)
    for o in numbers:
        o.rotation_euler.z = s.camera.rotation_euler.z-o.parent.matrix_world.to_euler().z
        o.keyframe_insert('rotation_euler', frame=frame)
    bpy.context.view_layer.update()
    row = []
    for o in numbers:
        origin = world_to_camera_view(s, s.camera, o.matrix_world.translation)
        top = world_to_camera_view(s, s.camera, o.matrix_world @ Vector((0, 1, 0)))
        row.append([origin.x, 1-origin.y])
        max_vertical_error = max(max_vertical_error, abs(top.x-origin.x))
    tracks.append(row)
s.frame_set(1)
assert static_snapshot() == original_static
assert original_camera == (tuple(s.camera.location), tuple(s.camera.rotation_euler), s.camera.data.ortho_scale)
assert max_vertical_error < .00001
s.frame_end = report['frames']
s.render.fps = 24
s.render.resolution_x, s.render.resolution_y = 1008, 700
s.render.resolution_percentage = 100
s.render.engine = 'BLENDER_EEVEE'
s.eevee.taa_render_samples = 16
s.render.image_settings.file_format = 'PNG'
candidate = output/'separated-city.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(candidate))

# Read back the saved keys before rendering or certifying visibility.
bpy.ops.wm.open_mainfile(filepath=str(candidate))
s = bpy.context.scene
max_pose_error = 0
for frame, poses in enumerate(motion, 1):
    s.frame_set(frame)
    for i, pose in enumerate(poses):
        o = s.objects[f'truck-{i//2+1}-'+('tractor' if i % 2 == 0 else 'trailer')]
        max_pose_error = max(max_pose_error, float(np.abs(np.array([*o.location, o.rotation_euler.z])-pose).max()))
assert max_pose_error < .00002, max_pose_error
assert static_snapshot() == original_static

sys.path.insert(0, str(archive))
from validate_visibility import templates, build, coverage, semantic_groups
groups = semantic_groups(s)
all_templates = templates(s)
moving_meshes = set().union(*(names for label, names in groups.items() if label.startswith('truck')))
static = build(s, [t for t in all_templates if t[0] not in moving_meshes])
records = []
for frame in range(1, len(motion)+1, 12):
    s.frame_set(frame)
    bpy.context.view_layer.update()
    dynamic = build(s, [t for t in all_templates if t[0] in moving_meshes])
    fractions = []
    for i in range(1, 5):
        glyph = build(s, [t for t in all_templates if t[0] in groups[f'number-{i}']])
        fractions.append(coverage(glyph, [static, dynamic], s.camera, s, 32)['visible'])
    records.append({'frame': frame, 'visible': fractions})
minimum = [min(r['visible'][i] for r in records) for i in range(4)]
verification = {
    'source': str(source), 'candidate': str(candidate),
    'saved_pose_max_error': max_pose_error, 'static_meshes_preserved': len(original_static),
    'camera_preserved': True, 'numeral_screen_vertical_error': max_vertical_error,
    'projected_roof_centers': tracks, 'number_visibility_minimum': minimum,
    'visibility_samples': records,
    'limits': '32x32 projected glyph ray grid every 0.5 seconds; not OCR or human recognition.',
    'passed': min(minimum) >= .9,
}
(output/'scene-check.json').write_text(json.dumps(verification, indent=2))
print('SCENE CHECK', max_pose_error, 'NUMBER VISIBILITY', minimum, flush=True)
assert verification['passed'], minimum
for frame in (1, 1+s.frame_end//4, 1+s.frame_end//2, 1+3*s.frame_end//4):
    s.frame_set(frame)
    s.render.filepath = str(output/('after.png' if frame == 1 else f'preview-{frame}.png'))
    bpy.ops.render.render(write_still=True)
if '--motion' in args:
    (output/'frames').mkdir(exist_ok=True)
    s.render.filepath = str(output/'frames/####')
    bpy.ops.render.render(animation=True)
