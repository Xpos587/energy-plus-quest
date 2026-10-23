import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
for version,source in [('v11',P.parent/'fleet-video-v11-2026-10-07/fleet-v11-video.blend'),('v12',P/'fleet-v12-style.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(330);tr=bpy.data.objects['truck-2-tractor'];tl=bpy.data.objects['truck-2-trailer'];own={tr,tl,*tr.children_recursive,*tl.children_recursive}
 for o in s.objects:
  if o.type not in ('CAMERA','LIGHT') and o not in own:o.hide_render=True
 cam=s.camera;target=tl.matrix_world@Vector((.7,0,2));cam.location=tl.matrix_world@Vector((.7,-10,3.2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=4.4
 s.render.use_compositing=False;s.render.film_transparent=True;s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(P/f'{version}-blue-attachment-turn.png');bpy.ops.render.render(write_still=True)
