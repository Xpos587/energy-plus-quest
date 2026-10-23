import bpy,json,math
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
p=Path('/home/michael/Github/energy-plus-quest/design/scene-01/route-preflight-2026-10-04')
s=bpy.context.scene
best=(99,0); tracks=[]
for f in range(1,s.frame_end+1):
 s.frame_set(f); row=[]; errors=[]
 for i in range(1,5):
  a=s.objects[f'truck-{i}-tractor'];b=s.objects[f'truck-{i}-trailer']
  yaw=a.rotation_euler.z;delta=math.atan2(math.sin(yaw-b.rotation_euler.z),math.cos(yaw-b.rotation_euler.z))
  errors.append(abs(delta))
  v=world_to_camera_view(s,s.camera,a.matrix_world.translation);row.append([v.x,1-v.y])
 tracks.append(row)
 if max(errors)<best[0]:best=(max(errors),f)
s.frame_set(best[1]);s.render.resolution_x=1440;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.filepath=str(p/'geometry-source.png')
(p/'inspection.json').write_text(json.dumps({'best_frame':best[1],'max_articulation_degrees':math.degrees(best[0]),'frames':len(tracks),'fps':s.render.fps,'tracks':tracks}))
print('BEST',best,flush=True)
bpy.ops.render.render(write_still=True)
