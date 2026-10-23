import bpy,json,time,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;cam=s.camera
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
frames=list(range(int(args[0]),int(args[1])+1)) if args else list(range(1,193))
s.render.resolution_percentage=100;s.eevee.volumetric_tile_size='2';s.eevee.volumetric_samples=128;s.eevee.use_volume_custom_range=True
puffs=list(bpy.data.collections['V17 worldspace exhaust puffs'].objects)
dest=P/'turn-vehicles';dest.mkdir(exist_ok=True);receipt=[]
for f in frames:
 output=dest/f'{f:04}.png'
 if output.exists():continue
 start=time.monotonic();s.frame_set(f);bpy.context.view_layer.update();inv=cam.matrix_world.inverted()
 depths=[-(inv@o.matrix_world@Vector(v)).z for o in puffs for v in o.bound_box]
 s.eevee.volumetric_start=min(depths)-2;s.eevee.volumetric_end=max(depths)+2
 s.render.filepath=str(output);bpy.ops.render.render(write_still=True)
 receipt.append({'frame':f,'seconds':time.monotonic()-start,'volume_start':s.eevee.volumetric_start,'volume_end':s.eevee.volumetric_end});print('FRAME_DONE',f,receipt[-1],flush=True)
 (P/f'render-receipt-{frames[0]:04}.json').write_text(json.dumps(receipt,indent=2))
