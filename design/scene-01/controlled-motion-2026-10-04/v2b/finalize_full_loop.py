"""Encode and verify complete technical loop without changing source artifacts."""
import json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
p=Path(__file__).resolve().parent
frames=sorted((p/'loop-frames').glob('*.png'))
assert [x.name for x in frames]==[f'{i:04}.png' for i in range(1,1153)]
assert all(Image.open(x).size==(720,500) for x in frames)
subprocess.run(['ffmpeg','-y','-framerate','24','-i',str(p/'loop-frames/%04d.png'),'-c:v','libx264','-threads','4','-crf','19','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(p/'source-loop-48s.mp4')],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_frames,nb_read_frames,duration','-of','json',str(p/'source-loop-48s.mp4')]))
v=probe['streams'][0]
assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'],v['nb_read_frames'],v['duration'])==(720,500,'24/1','1152','1152','48.000000')
motion=np.load(p/'motion.npy');track=json.loads((p/'tracking.json').read_text());screen=np.array(track['normalized_screen_origins'])
assert motion.shape==(1153,8,4) and screen.shape==(1153,8,2)
loop_position=float(np.abs(motion[0,:,:3]-motion[-1,:,:3]).max())
loop_angle=float(np.abs(np.angle(np.exp(1j*(motion[0,:,3]-motion[-1,:,3])))).max())
loop_screen=float(np.abs(screen[0]-screen[-1]).max())
assert loop_position==0 and loop_angle<1e-10 and loop_screen<1e-6
check=json.loads((p/'scene-check.json').read_text());assert check['passed'] and check['saved_pose_max_error']<.00002
report={'passed':True,'video':probe,'engine':'BLENDER_EEVEE','samples':8,'preview_frames_reused':120,'new_frames_rendered':1032,'camera_preserved':True,'scene_geometry_preserved':True,'loop_position_error':loop_position,'loop_angle_error_radians':loop_angle,'loop_screen_origin_error':loop_screen,'tracking_frames_including_boundary':len(screen),'saved_native_pose_max_error':check['saved_pose_max_error'],'timing':'Encoded frames1..1152 cover t=0 through47+23/24seconds; native boundary frame1153 at t=48 is exactly same pose as frame1 modulo full turns. Boundary frame not duplicated in video.','limitations':'Technical8-sample V2b reference at85percent native vehicle scale. Whole-rig visibility sampled every0.5seconds; cab visibility every0.25seconds in first5seconds and every1second elsewhere. Blue is not strictly closest to warehouse at every instant. Full conservative swept geometry and projected-clearance checks are supplied separately.'}
(p/'full-loop-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
