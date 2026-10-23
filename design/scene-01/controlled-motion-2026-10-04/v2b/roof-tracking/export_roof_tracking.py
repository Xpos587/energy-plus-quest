"""Export frozen native roof anchors without modifying or saving the scene.

Run: blender -b controlled-straight-start.blend --python roof-tracking/export_roof_tracking.py
"""
import json
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view

out = Path(__file__).resolve().parent
source = out.parent / 'controlled-straight-start.blend'
assert Path(bpy.data.filepath).resolve() == source.resolve()
scene = bpy.context.scene
anchors = [scene.objects[f'vehicle {i} identification'] for i in range(1, 5)]
rows = []
for frame in range(1, 1153):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    row = []
    for anchor in anchors:
        p = world_to_camera_view(scene, scene.camera, anchor.matrix_world.translation)
        row.append([float(p.x), float(1 - p.y)])
    rows.append(row)
assert len(rows) == 1152 and all(len(row) == 4 for row in rows)
assert all(0 <= coordinate <= 1 for row in rows for point in row for coordinate in point)
payload = {'fps': 24, 'frames': 1152, 'projected_roof_centers': rows}
(out / 'carrier-roof-tracking.json').write_text(json.dumps(payload, separators=(',', ':')))
scene.frame_set(1)
note = {
    'source': str(source.relative_to(out.parents[4])),
    'source_modified': False,
    'order': ['red', 'blue', 'green', 'yellow'],
    'anchors': [{'name': a.name, 'parent': a.parent.name if a.parent else None,
                 'local_location': list(a.location), 'hidden_render': a.hide_render}
                for a in anchors],
    'convention': 'Same hidden vehicle N identification matrix_world.translation as scripts/scene1-live/expand_city_2026_09_28.py; world_to_camera_view normalized [x, 1-y], top-left origin.',
    'camera': {'name': scene.camera.name, 'location': list(scene.camera.location),
               'rotation': list(scene.camera.rotation_euler), 'ortho_scale': scene.camera.data.ortho_scale},
    'timing': 'Row 0 is native frame 1 at t=0; row 1151 is native frame 1152 at t=47+23/24. Boundary frame 1153 omitted to match 1152 video frames.',
    'limitation': 'Roof label anchors retained from the native scene; this does not certify styling or universal roof visibility.'
}
(out / 'anchor-note.json').write_text(json.dumps(note, indent=2))
print('EXPORTED', len(rows), 'rows, four roof anchors, native scene unchanged', flush=True)
