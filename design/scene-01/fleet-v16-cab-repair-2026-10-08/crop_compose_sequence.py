from pathlib import Path
import importlib.util,subprocess,json
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v16compose',P.parent/'fleet-behavior-v16-2026-10-07/composite_motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.P=P
output=P/'repaired-map-proof-4s.mp4';proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1334','-r','24','-i','-','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
try:
 for f in range(73,169):
  im=m.compose(f,P/'turn-vehicles'/f'{f:04}.png');proc.stdin.write(im.tobytes())
  if f in (73,96,120,144,168):im.save(P/f'repaired-map-{f:04}.png');im.resize((960,667)).save(P/f'repaired-map-display-{f:04}.png')
finally:proc.stdin.close()
assert proc.wait()==0
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames,r_frame_rate,duration','-of','json',str(output)],text=True));s=probe['streams'][0];assert int(s['nb_read_frames'])==96 and s['r_frame_rate']=='24/1' and float(s['duration'])==4
r=subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-']);assert r.returncode==0
(P/'crop-map-video-validation.json').write_text(json.dumps({'video':output.name,'probe':probe,'full_decode_exit':r.returncode,'frames':[73,168],'camera':'unchanged original scene desktop camera'},indent=2));print(json.dumps(probe))
