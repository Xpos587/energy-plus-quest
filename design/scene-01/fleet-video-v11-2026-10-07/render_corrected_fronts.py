import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1);hide={o.name:o.hide_render for o in s.objects};c=s.camera;c.animation_data_clear();c.data.type='ORTHO';c.data.ortho_scale=9;s.render.use_compositing=False;s.render.film_transparent=True;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.color_mode='RGBA'
for i in range(1,5):
 r=bpy.data.objects[f'truck-{i}-tractor'];t=bpy.data.objects[f'truck-{i}-trailer'];keep={r,t,*r.children_recursive,*t.children_recursive}
 for o in s.objects:
  if o.type not in ('CAMERA','LIGHT'):o.hide_render=hide[o.name] or o not in keep
 target=r.matrix_world@Vector((-1.4,0,1.2));c.location=r.matrix_world@Vector((9,-12,7));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/f'front-{i}-corrected.png');bpy.ops.render.render(write_still=True)
