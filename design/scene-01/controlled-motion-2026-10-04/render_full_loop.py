"""Render remaining native frames using exactly the verified preview settings."""
import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
s.frame_start=121;s.frame_end=1152;s.render.fps=24
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=8
s.render.resolution_x=720;s.render.resolution_y=500;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
frames=p/'loop-frames';frames.mkdir(exist_ok=True)
for i in range(1,121):
 source=p/'preview-frames'/f'{i:04}.png';assert source.exists()
 target=frames/source.name
 if not target.exists():target.symlink_to(Path('../preview-frames')/source.name)
s.render.filepath=str(frames/'####')
settings={'source':bpy.data.filepath,'engine':s.render.engine,'samples':s.eevee.taa_render_samples,'fps':s.render.fps,'resolution':[720,500],'native_frames':1152,'duration_seconds':48,'reused_preview_frames':[1,120],'rendered_frames':[121,1152],'threads':4,'camera':{'name':s.camera.name,'location':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'ortho_scale':s.camera.data.ortho_scale},'source_scene_modified':False}
(p/'full-render-settings.json').write_text(json.dumps(settings,indent=2))
bpy.ops.render.render(animation=True)
