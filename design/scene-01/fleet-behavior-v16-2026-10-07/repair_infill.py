import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
for file in ('fleet-v16.blend','fleet-v16-motion.blend'):
 if not (P/file).exists():continue
 bpy.ops.wm.open_mainfile(filepath=str(P/file))
 for i in (1,4):
  for o in bpy.data.objects:
   if o.name.startswith(f'V09 CLEAN {i}'):o.hide_render=False
 # Reuse the previously verified per-point source fringe repair on restored old cabins.
 code=(P.parent/'fleet-native-v14-2026-10-07/repair_final_seams.py').read_text()
 code=code.replace('((2,(.035,.235,.61,1)),(3,(.18,.50,.075,1)))','((1,(.64,.13,.085,1)),(4,(.87,.58,.075,1)))')
 code=code.split('bpy.ops.wm.save_as_mainfile')[0]
 exec(compile(code,'source_fringe_repair','exec'))
 P=Path(__file__).resolve().parent
 bpy.ops.wm.save_as_mainfile(filepath=str(P/file))
