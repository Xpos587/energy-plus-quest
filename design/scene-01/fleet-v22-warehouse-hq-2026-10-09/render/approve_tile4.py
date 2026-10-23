import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene
s.eevee.volumetric_tile_size='4';s.eevee.taa_render_samples=8;s.eevee.volumetric_samples=32
s.render.resolution_x=3840;s.render.resolution_y=2668;s.render.resolution_percentage=100
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(P/'v22-4k-source.blend'))
(P/'approved-render-settings.json').write_text(json.dumps({'engine':s.render.engine,'resolution':[3840,2668],'taa':8,'volume_samples':32,'volume_tile':4,'camera':s.camera.name,'frames_deliverable':[1,1536],'boundary_frame':1537,'fps':24,'duration_seconds':64,'gpu_launch':'prime-run','approved_by':'parent after visual tile2/tile4 comparison'},indent=2))
