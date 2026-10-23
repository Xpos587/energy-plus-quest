import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.data.objects['V08 4 older rectangular roof hatch'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
