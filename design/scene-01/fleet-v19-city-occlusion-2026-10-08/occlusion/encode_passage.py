from pathlib import Path
from PIL import Image
import subprocess,json,sys
P=Path(__file__).resolve().parent
bgpath=Path(sys.argv[1]) if len(sys.argv)>1 else P.parents[1]/'fleet-road-v11-2026-10-07/backdrop-v11.png'
bg=Image.open(bgpath).convert('RGBA');output=P/'occlusion-passage-2s.mp4'
proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{bg.width}x{bg.height}','-r','24','-i','-','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
for f in range(129,177):
 im=Image.alpha_composite(bg,Image.open(P/'passage'/f'{f:04}.png').convert('RGBA')).convert('RGB');proc.stdin.write(im.tobytes())
proc.stdin.close();assert proc.wait()==0
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames,r_frame_rate,duration','-of','json',str(output)]));v=probe['streams'][0];assert int(v['nb_read_frames'])==48 and v['r_frame_rate']=='24/1'
r=subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-']);assert r.returncode==0
(P/'passage-validation.json').write_text(json.dumps({'probe':probe,'decode_exit':r.returncode,'source_frames':[129,176],'background':str(bgpath),'shadow_note':'This isolated occlusion proof omits separately composited ground shadows; parent final compositor may add existing shadows.'},indent=2))
print(output)
