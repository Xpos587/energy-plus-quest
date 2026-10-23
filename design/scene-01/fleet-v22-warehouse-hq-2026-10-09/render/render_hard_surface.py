import bpy,json,time,sys,gpu
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:raise RuntimeError('Explicit frames required')
frames=[int(v) for v in args]
if not all(1<=f<=1537 for f in frames):raise ValueError(frames)
gpu.init()
info={'vendor':gpu.platform.vendor_get(),'renderer':gpu.platform.renderer_get(),'version':gpu.platform.version_get(),'backend':gpu.platform.backend_type_get()}
print('GPU',json.dumps(info),flush=True)
hidden=[]
for o in s.objects:
 if o.name in bpy.data.collections['V16 smoke worldspace exhaust puffs'].objects or o.name in bpy.data.collections['FX - soft exhaust, old trucks only'].objects:
  o.hide_render=True;hidden.append(o.name)
s.render.resolution_x=3840;s.render.resolution_y=2668;s.render.resolution_percentage=100;s.eevee.taa_render_samples=8
p=P/'pilot-hard-surface';p.mkdir(exist_ok=True);timings=[]
for f in frames:
 s.frame_set(f);bpy.context.view_layer.update();start=time.monotonic();s.render.filepath=str(p/f'{f:04}.png');bpy.ops.render.render(write_still=True);timings.append({'frame':f,'seconds':time.monotonic()-start});print('HARD_DONE',timings[-1],flush=True)
 (P/'hard-surface-receipt.json').write_text(json.dumps({'gpu':info,'hidden_volume_objects':hidden,'timings':timings,'dimensions':[3840,2668],'taa':8},indent=2))
