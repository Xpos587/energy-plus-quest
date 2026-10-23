import bpy,time,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(60);bpy.context.view_layer.update();s.render.resolution_percentage=100;s.eevee.volumetric_tile_size='2';s.eevee.use_volume_custom_range=True;s.eevee.taa_render_samples=8
inv=s.camera.matrix_world.inverted();puffs=[o for o in bpy.data.collections['V16 smoke worldspace exhaust puffs'].objects if not o.hide_render];depths=[-(inv@o.matrix_world@Vector(v)).z for o in puffs for v in o.bound_box];s.eevee.volumetric_start=min(depths)-2;s.eevee.volumetric_end=max(depths)+2;receipt=[]
for quality in (32,128):
 s.eevee.volumetric_samples=quality;s.render.filepath=str(P/f'quality-{quality}.png');start=time.monotonic();bpy.ops.render.render(write_still=True);receipt.append({'volume_samples':quality,'taa_samples':8,'seconds':time.monotonic()-start})
(P/'quality-benchmark.json').write_text(json.dumps(receipt,indent=2))
