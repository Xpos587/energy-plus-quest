import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1);r=bpy.data.objects['truck-1-tractor'];t=bpy.data.objects['truck-1-trailer'];keep={r,t,*r.children_recursive,*t.children_recursive}
for o in s.objects:
 if o.type not in ('CAMERA','LIGHT') and o not in keep:o.hide_render=True
s.render.use_compositing=False;s.render.film_transparent=True;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.color_mode='RGBA';c=s.camera;c.animation_data_clear();c.data.type='ORTHO';c.data.ortho_scale=13;target=r.matrix_world@Vector((-3,0,1.2));c.location=r.matrix_world@Vector((-2,-17,3));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/'side-before-1.png');bpy.ops.render.render(write_still=True)
