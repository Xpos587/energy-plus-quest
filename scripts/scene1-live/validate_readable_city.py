"""Compare saved geometry/motion and sample actual numeral occlusion, without hashes."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
source, candidate, output = map(Path, args)

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    s = bpy.context.scene
    s.frame_set(1)
    meshes = {o.name: ([tuple(v.co) for v in o.data.vertices],
                       [tuple(row) for row in o.matrix_world])
              for o in s.objects if o.type == 'MESH'}
    poses = []
    for f in range(1, s.frame_end + 2):
        s.frame_set(f)
        poses.append([[tuple(row) for row in s.objects[f'truck-{i}-{part}'].matrix_world]
                      for i in range(1, 5) for part in ('tractor', 'trailer')])
    return meshes, poses, tuple(s.camera.location), tuple(s.camera.rotation_euler), s.camera.data.ortho_scale

before = snapshot(source)
after = snapshot(candidate)
assert before[1:] == after[1:], 'Camera or a truck pose changed'
assert all(after[0].get(k) == v for k, v in before[0].items()), 'Existing mesh changed'
s = bpy.context.scene
added = set(after[0]) - set(before[0])
assert len(added) == 6 and all(n.startswith('READ ') for n in added), added
for name in added:
    for corner in s.objects[name].bound_box:
        v = s.objects[name].matrix_world @ Vector(corner)
        assert -51.8 <= v.x <= -32.0 and -21.8 <= v.y <= 23.2 and v.z <= .2, (name, tuple(v))

# Import only the existing geometry/ray helpers; its hash-producing run() is not used.
sys.path.insert(0, str(source.parent.parent))
from validate_visibility import templates, build, coverage, semantic_groups
groups = semantic_groups(s)
all_templates = templates(s)
moving = set().union(*(v for k, v in groups.items() if k.startswith('truck')))
static = build(s, [t for t in all_templates if t[0] not in moving])
records = []
for frame in range(1, s.frame_end + 2, 12):
    s.frame_set(frame)
    bpy.context.view_layer.update()
    dynamic = build(s, [t for t in all_templates if t[0] in moving])
    fractions = []
    for i in range(1, 5):
        group = build(s, [t for t in all_templates if t[0] in groups[f'number-{i}']])
        fractions.append(coverage(group, [static, dynamic], s.camera, s, 32)['visible'])
    records.append({'frame': frame, 'visible': fractions})
minimum = [min(r['visible'][i] for r in records) for i in range(4)]
report = {
    'source': str(source), 'candidate': str(candidate),
    'same_camera_and_all_769_poses': True, 'existing_meshes_preserved': len(before[0]),
    'added_flat_yard_markings': sorted(added), 'number_visibility_minimum': minimum,
    'visibility_samples': records,
    'limits': '32x32 projected glyph silhouette ray grid every 0.5 seconds; not OCR or human recognition.',
    'passed': min(minimum) >= .9,
}
output.write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'visibility_samples'}, indent=2))
assert report['passed'], minimum
