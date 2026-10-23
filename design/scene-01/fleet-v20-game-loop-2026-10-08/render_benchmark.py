import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene
print('SAMPLES',[(k,getattr(s.eevee,k))for k in s.eevee.bl_rna.properties.keys()if 'sample'in k],flush=True)
s.frame_set(60);s.render.resolution_percentage=100;s.eevee.volumetric_samples=32;s.eevee.taa_render_samples=16;s.render.filepath=str(P/'benchmark-16.png');bpy.ops.render.render(write_still=True)
