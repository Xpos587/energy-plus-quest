import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
for i in range(1,5):bpy.data.objects[f'{i} rear underrun bar'].hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v11-video.blend'))
(P/'rear-bar-fix.json').write_text(json.dumps({'source':'../fleet-coupling-v11-2026-10-07/fleet-v11-coupling.blend','change':'hide four unsupported floating rear underrun bars in video master; no other edits','objects':[f'{i} rear underrun bar' for i in range(1,5)]},indent=2))
r=bpy.data.objects['truck-1-tractor'];t=bpy.data.objects['truck-1-trailer'];keep={r,t,*r.children_recursive,*t.children_recursive}
for o in s.objects:
 if o.type not in ('CAMERA','LIGHT') and o not in keep:o.hide_render=True
s.render.use_compositing=False;s.render.film_transparent=True;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.color_mode='RGBA';c=s.camera;c.animation_data_clear();c.data.type='ORTHO';c.data.ortho_scale=13;target=r.matrix_world@Vector((-3,0,1.2));c.location=r.matrix_world@Vector((-2,-17,3));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/'side-1-corrected.png');bpy.ops.render.render(write_still=True)
