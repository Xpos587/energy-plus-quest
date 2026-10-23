import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
names=[f'truck-{i}-{p}' for i in range(1,5) for p in ('tractor','trailer')]
def sample(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;rows=[]
 for f in range(1,1153):
  s.frame_set(f);rows.append([tuple(v for row in bpy.data.objects[n].matrix_world for v in row) for n in names])
 return rows
old=sample(P.parent/'fleet-video-v11-2026-10-07/fleet-v11-video.blend');new=sample(P/'fleet-v12-style.blend');assert old==new
s=bpy.context.scene;s.frame_set(1)
layer=s.view_layers[0];layer.use_pass_normal=True;layer.use_pass_z=True;layer.use_pass_cryptomatte_object=True
s.render.image_settings.media_type='MULTI_LAYER_IMAGE';s.render.image_settings.file_format='OPEN_EXR';s.render.filepath=str(P/'structure-0001.exr');bpy.ops.render.render(write_still=True)
(P/'verification.json').write_text(json.dumps({'all_1152_frames_root_matrices_equal':True,'roots_checked':names,'camera':'desktop','seed':'EEVEE deterministic sampling','dimensions':[1920,1334],'structural_passes':['Normal','Depth','CryptoObject'],'full_video_rendered':False},indent=2))
