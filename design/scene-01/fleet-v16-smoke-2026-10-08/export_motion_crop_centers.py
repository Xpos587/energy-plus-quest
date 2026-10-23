import bpy,json
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene;out={}
for f in range(1,193):
 s.frame_set(f);bpy.context.view_layer.update();out[f]={}
 for i in (1,4):
  pipe=bpy.data.objects[f'{i} exhaust stack'];v=[pipe.matrix_world@Vector(c) for c in pipe.bound_box];target=Vector((sum(c.x for c in v)/8,sum(c.y for c in v)/8,max(c.z for c in v)))
  q=world_to_camera_view(s,s.camera,target);out[f][i]=[q.x*1920,(1-q.y)*1334]
(P/'motion-crop-centers.json').write_text(json.dumps(out))
