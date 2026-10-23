import bpy,sys,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:];f=int(args[0]);i=int(args[1]);s.frame_set(f);bpy.context.view_layer.update()
r=bpy.data.objects[f'truck-{i}-trailer'];keep=set(r.children_recursive)|{r};q=s.camera.matrix_world.to_quaternion()
for o in s.objects:
 if o.type=='MESH' and o not in keep:o.hide_render=True
s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.use_compositing=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
d=bpy.data.cameras.new('Trailer diagnostic');c=bpy.data.objects.new('Trailer diagnostic',d);s.collection.objects.link(c);s.camera=c;d.type='ORTHO';d.clip_start=.05;d.clip_end=100
for name,eye,target,scale in [('side',(-3.05,-14,2.3),(-3.05,0,1.6),10),('rear',(-16,0,2.2),(-6.8,0,1.8),4.8),('top',(-3.05,0,14),(-3.05,0,2.1),10),('map',None,(-3.05,0,2.1),10),('axle',(-4.48,-10,1.2),(-4.48,-.7,.48),2.4)]:
 t=r.matrix_world@Vector(target)
 if eye is None:c.location=t+q@Vector((0,0,20));c.rotation_euler=q.to_euler()
 else:c.location=r.matrix_world@Vector(eye);c.rotation_euler=(t-c.location).to_track_quat('-Z','Y').to_euler()
 d.ortho_scale=scale;s.render.filepath=str(P/f'style-trailer{i}-{name}-{f:04}.png');bpy.ops.render.render(write_still=True)
