from pathlib import Path
import importlib.util,subprocess,json,time
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v16composite',P.parent/'fleet-behavior-v16-2026-10-07/composite_motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
dest=P/'fleet-v16-smoke-proof-8s.mp4';cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1334','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-threads','4',str(dest)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.monotonic()
try:
 for f in range(1,193):
  im=m.compose(f,P/'turn-vehicles'/f'{f:04}.png');proc.stdin.write(im.tobytes())
  if f in (1,48,96,144,192):im.save(P/f'video-frame-{f:04}.png')
finally:proc.stdin.close()
assert proc.wait()==0
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration,codec_name','-of','json',str(dest)],text=True));st=probe['streams'][0]
assert int(st['nb_read_frames'])==192 and st['r_frame_rate']=='24/1' and float(st['duration'])==8 and st['width']==1920 and st['height']==1334
(P/'video-validation.json').write_text(json.dumps({'video':dest.name,'probe':probe,'source':'fleet-v16-smoke.blend','frames':'192 separately evaluated Blender frames','shadow':'read-only v16 actual geometry shadow PNGs, appropriate because cabs and routes unchanged','composite':'read-only v16 compositor/backdrop/road receiver mask','encode_seconds':time.monotonic()-start},indent=2));print(json.dumps(probe))
