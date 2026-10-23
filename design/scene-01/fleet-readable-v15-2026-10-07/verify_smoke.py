import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;checks=[]
for frame in (1,239,385,769,1152):
 s.frame_set(frame);bpy.context.view_layer.update()
 for i in (1,4):
  root=bpy.data.objects[f'truck-{i}-tractor'];pipe=bpy.data.objects[f'{i} exhaust stack'];smoke=bpy.data.objects[f'V15 {i} connected exhaust plume'];p=[root.matrix_world.inverted()@pipe.matrix_world@Vector(v)for v in pipe.bound_box];tip=Vector(((min(v.x for v in p)+max(v.x for v in p))/2,(min(v.y for v in p)+max(v.y for v in p))/2,max(v.z for v in p)));pipe_world=root.matrix_world@tip;smoke_world=sum((smoke.matrix_world@v.co for v in list(smoke.data.vertices)[:16]),Vector())/16;gap=(pipe_world-smoke_world).length
  assert gap<.0001,(frame,i,gap);assert not smoke.hide_render
  checks.append({'frame':frame,'truck':i,'pipe_outlet_world':list(pipe_world),'plume_base_world':list(smoke_world),'gap':gap})
(P/'smoke-outlet-validation.json').write_text(json.dumps({'validated':True,'method':'world-space transformed pipe bounding-box cap vs volume first-ring centre; handles matrix_parent_inverse','checks':checks},indent=2));print('SMOKE_OUTLETS_PASS',len(checks))
