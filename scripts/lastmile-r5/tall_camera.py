"""Retarget the R5 tall camera tighter (phone legibility): fit quay row + barge + ABK + helipad + chums, drop empty far tundra.
blender -b <final>/scene.blend --python-exit-code 1 -t 12 --python scripts/lastmile-r5/tall_camera.py -- <final> <out>
Writes <out>/scene.blend, <out>/manifest.json (tall camera updated) and <out>/tall.png. Geometry untouched.
"""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]
src, out = Path(args[0]).resolve(), Path(args[1]).resolve(); out.mkdir(parents=True, exist_ok=True)
manifest = json.loads((src / 'manifest.json').read_text())
RES, PAD = (1000, 1250), .06
FIT_GROUPS = ('helicopter', 'heli_pad', 'pipe_carrier', 'rover', 'robot', 'barge', 'gift', 'quay', 'abk', 'helipad', 'chums')
scene = bpy.context.scene; cam = bpy.data.objects['tall']; cd = cam.data
pts = [o.matrix_world @ Vector(c) for o in scene.objects if o.get('group') in FIT_GROUPS for c in o.bound_box]
scene.render.resolution_x, scene.render.resolution_y = RES; cd.shift_x = cd.shift_y = 0; bpy.context.view_layer.update()
co, _ = cam.camera_fit_coords(bpy.context.evaluated_depsgraph_get(), [v for p in pts for v in p])
fwd = cam.rotation_euler.to_matrix() @ Vector((0, 0, -1))
cam.location = co - fwd * (sum(pts, Vector()) / len(pts) - co).length * PAD
scene.camera = cam; bpy.context.view_layer.update()
manifest['cameras']['tall'].update(resolution=list(RES), location=list(cam.location), retarget='tall_camera.py')
(out / 'manifest.json').write_text(json.dumps(manifest, indent=1))
scene.render.filepath = str(out / 'tall.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'scene.blend'))
print('TALL_RETARGET_COMPLETE', list(cam.location), flush=True)
