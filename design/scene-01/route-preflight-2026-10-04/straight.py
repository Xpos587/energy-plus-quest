import bpy, math,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
p=Path('/home/michael/Github/energy-plus-quest/design/scene-01/route-preflight-2026-10-04');s=bpy.context.scene
poses={};report=[]
for i in range(1,5):
 a=s.objects[f'truck-{i}-tractor'];b=s.objects[f'truck-{i}-trailer'];best=(999,None)
 for f in range(1,s.frame_end+1):
  s.frame_set(f);y=a.rotation_euler.z
  delta=abs(math.atan2(math.sin(y-b.rotation_euler.z),math.cos(y-b.rotation_euler.z)))
  cardinal=abs(math.sin(2*y))
  q=world_to_camera_view(s,s.camera,a.matrix_world.translation)
  # Prefer visibly front-facing southbound rigs for blue and green.
  cost=delta+cardinal+(0 if i not in (2,3) or math.sin(y)<-.9 else 10)
  if cost<best[0]:best=(cost,(f,a.location.copy(),a.rotation_euler.copy(),b.location.copy(),b.rotation_euler.copy(),delta,[q.x,1-q.y]))
 f,al,ar,bl,br,d,q=best[1];poses[i]=(al,ar,bl,br);report.append({'truck':i,'source_frame':f,'articulation_degrees':math.degrees(d),'screen_cab':q})
s.frame_set(1)
for i,(al,ar,bl,br) in poses.items():
 for part,l,r in [('tractor',al,ar),('trailer',bl,br)]:
  o=s.objects[f'truck-{i}-{part}'];o.animation_data_clear();o.location=l;o.rotation_euler=r
s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(p/'straight-geometry.png');s.render.image_settings.file_format='PNG'
(p/'straight-start.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(p/'straight-candidate.blend'))
bpy.ops.render.render(write_still=True)
