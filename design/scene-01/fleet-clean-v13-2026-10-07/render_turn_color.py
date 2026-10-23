import bpy,time,json
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
for o in s.objects:
 if o.type not in ('CAMERA','LIGHT') and o not in fleet:o.hide_render=True
s.render.use_compositing=False;s.render.film_transparent=True;s.render.resolution_percentage=100;s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.image_settings.file_format='PNG'
s.render.engine='BLENDER_EEVEE'
if hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=16
out=P/'turn-vehicles';out.mkdir(exist_ok=True);ts=[]
for f in range(301,421):
 target=out/f'{f:04}.png'
 if target.exists():continue
 t=time.monotonic();s.frame_set(f);temp=target.with_name(target.stem+'.tmp.png');s.render.filepath=str(temp);bpy.ops.render.render(write_still=True);temp.replace(target);dt=time.monotonic()-t;ts.append(dt);print('PROGRESS_COLOR',f,round(dt,3),flush=True)
 if f%24==0:(P/'turn-color-progress.json').write_text(json.dumps({'last_frame':f,'recent_seconds':ts[-24:]},indent=2))
(P/'turn-color-receipt.json').write_text(json.dumps({'frames':120,'fps':24,'dimensions':[1920,1334],'samples':getattr(s.eevee,'taa_render_samples',None),'source':'fleet-v13-clean.blend','total_render_seconds':sum(ts)},indent=2))
