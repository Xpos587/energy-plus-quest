import json,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent
frames=sorted((p/'preview-frames').glob('*.png'))
assert [x.name for x in frames]==[f'{i:04}.png' for i in range(1,121)]
subprocess.run(['ffmpeg','-y','-framerate','24','-i',str(p/'preview-frames/%04d.png'),'-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(p/'motion-preview-5s.mp4')],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(p/'motion-preview-5s.mp4')]))
v=probe['streams'][0];assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'],v['duration'])==(720,500,'24/1','120','5.000000')
(p/'preview-check.json').write_text(json.dumps({'native_duration_seconds':48,'preview':probe,'full_cycle_raster_rendered':False,'passed':True},indent=2))
print(json.dumps(probe,indent=2))
