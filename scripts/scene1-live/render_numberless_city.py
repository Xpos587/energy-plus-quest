"""Render the approved separated-route city directly without roof numerals.

blender -b SOURCE.blend -t 4 --python render_numberless_city.py -- OUTPUT_DIR
"""

import sys
from pathlib import Path

import bpy


output = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
output.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene

for index in range(1, 5):
    marker = scene.objects[f"vehicle {index} identification"]
    assert marker.type == "FONT" and not marker.children
    marker.hide_render = True

assert scene.frame_end == 1152
assert scene.render.resolution_x == 1008
assert scene.render.resolution_y == 700
assert scene.render.fps == 24

scene.frame_set(1)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(output / "frames" / "####")
(output / "frames").mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(output / "separated-city-without-numbers.blend"))
bpy.ops.render.render(animation=True)
