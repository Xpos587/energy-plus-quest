import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;s=bpy.context.scene;roof={};out={}
for i in (1,4):
 cab=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];local=Matrix.Translation(Vector((.8,0,.9)))@cab.matrix_local;pts=[local@v.co for v in cab.data.vertices];top=max(v.z for v in pts);toppts=[v for v in pts if v.z>top-.03];roof[i]=sum(toppts,Vector())/len(toppts)
for f in range(73,169):
 s.frame_set(f);bpy.context.view_layer.update();out[f]={}
 for i in (1,4):
  root=bpy.data.objects[f'truck-{i}-tractor'];q=world_to_camera_view(s,s.camera,root.matrix_world@roof[i]);out[f][i]=[q.x*960,(1-q.y)*667]
(P/'roof-tracking-centers.json').write_text(json.dumps(out))
