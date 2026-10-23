import bpy,bmesh
from pathlib import Path
P=Path(__file__).resolve().parent
for i in (2,3):
 o=bpy.data.objects[f'V14 {i} continuous side wing -1'];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
