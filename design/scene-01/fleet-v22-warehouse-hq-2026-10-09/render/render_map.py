"""Explicit frames only: blender -b v22-4k-source.blend --python render_map.py -- 1 384 768."""
import bpy,json,time,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;cam=s.camera
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if not args:raise RuntimeError('Explicit frame numbers required; no default full render')
frames=[int(v) for v in args]
if not all(1<=f<=1537 for f in frames):raise ValueError(frames)
s.render.resolution_x=3840;s.render.resolution_y=2668;s.render.resolution_percentage=100
s.eevee.taa_render_samples=8;s.eevee.volumetric_tile_size='4';s.eevee.volumetric_samples=32;s.eevee.use_volume_custom_range=True
puffs=[o for o in bpy.data.collections['V16 smoke worldspace exhaust puffs'].objects if not o.hide_render]
dest=P/'turn-vehicles';dest.mkdir(exist_ok=True);receipt=[]
for f in frames:
 output=dest/f'{f:04}.png'
 if output.exists():continue
 start=time.monotonic();s.frame_set(f);bpy.context.view_layer.update();inv=cam.matrix_world.inverted()
 depths=[-(inv@o.matrix_world@Vector(v)).z for o in puffs for v in o.bound_box]
 s.eevee.volumetric_start=min(depths)-2;s.eevee.volumetric_end=max(depths)+2
 temp=output.with_name(output.stem+'.tmp.png');s.render.filepath=str(temp);bpy.ops.render.render(write_still=True);temp.replace(output)
 receipt.append({'frame':f,'seconds':time.monotonic()-start,'resolution':[3840,2668],'taa':8,'volume_start':s.eevee.volumetric_start,'volume_end':s.eevee.volumetric_end});print('FRAME_DONE',f,receipt[-1],flush=True)
 (P/f'render-receipt-{frames[0]:04}.json').write_text(json.dumps(receipt,indent=2))
