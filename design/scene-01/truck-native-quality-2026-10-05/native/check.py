import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/native/scania-native-shape-gate.blend')
for o in bpy.data.objects:
 if 'tire' in o.name or 'chassis' in o.name:
  vs=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[j] for v in vs) for j in range(3)];hi=[max(v[j] for v in vs) for j in range(3)];print(o.name,lo,hi,[(m.name,m.type) for m in o.modifiers])
