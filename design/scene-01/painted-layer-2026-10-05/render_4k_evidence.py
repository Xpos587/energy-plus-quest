import bpy,time,json
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2667;s.render.resolution_percentage=100;s.eevee.taa_render_samples=8;s.frame_set(769)
s.render.filepath=str(p/'repaired-stills/4k-0769.png');t=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-t
r={'source':'painted-vehicles-repaired.blend','frame':769,'dimensions':[3840,2667],'samples':8,'threads':4,'measured_render_wall_seconds':round(elapsed,3),'upscaled':False,'source_materials':'archived projected painted textures; native geometry, Cryptomatte against city beauty','full_animation_rendered':False}
(p/'4k-evidence-receipt.json').write_text(json.dumps(r,indent=2));print('4K EVIDENCE COMPLETE',r)
