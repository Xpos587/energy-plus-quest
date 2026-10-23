import bpy,pathlib,time,json,os
P=pathlib.Path(__file__).resolve().parent;s=bpy.context.scene
s.render.resolution_x=1024;s.render.resolution_y=712;s.render.resolution_percentage=100
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=4
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True
s.render.threads_mode='FIXED';s.render.threads=4
(P/'loop-frames').mkdir(exist_ok=True);start=time.monotonic()
first=int(os.environ.get('FLEET_START','1'));last=int(os.environ.get('FLEET_END','1152'))
for f in range(first,last+1):
 out=P/f'loop-frames/{f:04}.png'
 if out.exists():continue
 s.frame_set(f);s.render.filepath=str(out);bpy.ops.render.render(write_still=True)
 if f%48==0:print('LOOP_PROGRESS',f,'of',1152,'seconds',round(time.monotonic()-start,1),flush=True)
(P/f'loop-render-{first}-{last}.json').write_text(json.dumps({'frame_range':[first,last],'fps':24,'fleet_layer_dimensions':[1024,712],'elapsed_seconds':time.monotonic()-start,'source':'fleet/fleet-textured-v06.blend','root_actions_changed':False,'purpose':'economical full-motion proof with separately retained1920px stills; not final zoom-resolution video'},indent=2))
