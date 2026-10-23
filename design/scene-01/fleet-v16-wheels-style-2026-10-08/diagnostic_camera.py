import bpy,json,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
prefix=args[0] if args else 'before';frame=int(args[1]) if len(args)>1 else 91;i=int(args[2]) if len(args)>2 else 1
s.frame_set(frame);bpy.context.view_layer.update();root=bpy.data.objects[f'truck-{i}-tractor'];fleet=set(root.children_recursive)|{root}
if len(args)>3 and args[3]=='neutral':
 group=bpy.data.objects[f'WORN {i} isolated cab suspension'];group.location=(.8,0,.9);group.rotation_euler=(0,0,0);bpy.context.view_layer.update()
for o in s.objects:
 if o.type=='MESH' and o not in fleet:o.hide_render=True
s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.use_compositing=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
camdata=bpy.data.cameras.new('DIAGNOSTIC camera');cam=bpy.data.objects.new('DIAGNOSTIC camera',camdata);s.collection.objects.link(cam);s.camera=cam;camdata.type='ORTHO';camdata.clip_start=.05;camdata.clip_end=100
receipt=[]
for name,eye,target,scale in [('side',(-.3,-10,1.5),(-.3,0,1.5),6.3),('front',(10,0,1.45),(.8,0,1.45),4.4),('threequarter',(8,-10,5),(.4,0,1.35),5.8)]:
 cam.location=root.matrix_world@Vector(eye);t=root.matrix_world@Vector(target);cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale
 s.render.filepath=str(P/f'{prefix}-truck{i}-{name}-f{frame:04}.png');bpy.ops.render.render(write_still=True);receipt.append({'view':name,'frame':frame,'truck':i,'camera_world':list(cam.location),'target_world':list(t),'ortho_scale':scale})
(P/f'{prefix}-truck{i}-diagnostic-camera.json').write_text(json.dumps(receipt,indent=2))
