import bpy, pathlib, time, json, os
P=pathlib.Path(__file__).resolve().parent
s=bpy.context.scene
s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=8
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True
s.render.threads_mode='FIXED';s.render.threads=4
outdir=P/'loop-v07-frames';outdir.mkdir(exist_ok=True)
start=time.monotonic();first=int(os.environ.get('FLEET_START','1'));last=int(os.environ.get('FLEET_END','1152'))
for f in range(first,last+1):
    out=outdir/f'{f:04}.png'
    if out.exists():continue
    s.frame_set(f);s.render.filepath=str(out);bpy.ops.render.render(write_still=True)
    if f%96==0:print('PROGRESS',f,'elapsed',round(time.monotonic()-start,1),flush=True)
(P/f'loop-v07-{first}-{last}.json').write_text(json.dumps({'frame_range':[first,last],'fps':24,'dimensions':[1920,1334],'elapsed_seconds':time.monotonic()-start,'source':'fleet/fleet-textured-v07-fast.blend','root_actions_changed':False},indent=2))
