"""Independent original-quality full smoke NVIDIA benchmark; explicit frames only."""
import bpy,json,time,sys,gpu
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;cam=s.camera
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:raise RuntimeError('Explicit frame numbers required')
frames=[int(v) for v in args]
if not all(1<=f<=1537 for f in frames):raise ValueError(frames)
gpu.init();info={'vendor':gpu.platform.vendor_get(),'renderer':gpu.platform.renderer_get(),'version':gpu.platform.version_get(),'backend':gpu.platform.backend_type_get()};print('GPU',json.dumps(info),flush=True)
s.render.resolution_x=3840;s.render.resolution_y=2668;s.render.resolution_percentage=100
s.eevee.taa_render_samples=8;s.eevee.volumetric_tile_size='4';s.eevee.volumetric_samples=32;s.eevee.use_volume_custom_range=True
puffs=[o for o in bpy.data.collections['V16 smoke worldspace exhaust puffs'].objects if not o.hide_render]
dest=P/'pilot-nvidia-tile4';dest.mkdir(exist_ok=True);receipt=[]
for f in frames:
 start=time.monotonic();s.frame_set(f);bpy.context.view_layer.update();inv=cam.matrix_world.inverted()
 depths=[-(inv@o.matrix_world@Vector(v)).z for o in puffs for v in o.bound_box]
 s.eevee.volumetric_start=min(depths)-2;s.eevee.volumetric_end=max(depths)+2
 s.render.filepath=str(dest/f'{f:04}.png');bpy.ops.render.render(write_still=True)
 receipt.append({'frame':f,'seconds':time.monotonic()-start});print('NVIDIA_DONE',receipt[-1],flush=True)
 (P/'nvidia-tile4-receipt.json').write_text(json.dumps({'gpu':info,'resolution':[3840,2668],'taa':8,'volume_samples':32,'volume_tile':4,'timings':receipt},indent=2))
