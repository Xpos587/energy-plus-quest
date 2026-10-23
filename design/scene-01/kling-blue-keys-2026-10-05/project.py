import bpy,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
p=Path(__file__).resolve().parent;s=bpy.context.scene;r={}
for f in (1,385,577,769):
 s.frame_set(f);pts=[]
 for o in s.objects:
  a=o
  while a.parent:a=a.parent
  if a.name not in ('truck-2-tractor','truck-2-trailer') or o.type!='MESH' or o.hide_render:continue
  pts.extend(world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box)
 r[str(f)]={'bbox_4k':[int(min(q.x for q in pts)*3840)-4,int((1-max(q.y for q in pts))*2667)-4,int(max(q.x for q in pts)*3840)+4,int((1-min(q.y for q in pts))*2667)+4],'roots':{n:[list(bpy.data.objects[n].location),list(bpy.data.objects[n].rotation_euler)] for n in ('truck-2-tractor','truck-2-trailer')}}
(p/'source-placement.json').write_text(json.dumps(r,indent=2));print(r)
