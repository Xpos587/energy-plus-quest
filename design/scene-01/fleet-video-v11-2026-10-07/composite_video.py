from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,subprocess,json,time
P=Path(__file__).resolve().parent
bg=Image.open(P.parent/'fleet-road-v11-2026-10-07/backdrop-v11.png').convert('RGBA');mask=Image.open(P.parent/'fleet-lookdev-v10-2026-10-07/road-receiver-mask.png').convert('L');ma=np.array(mask,dtype=np.float32)/255

def compose(f,color=None):
 a=Image.open(P/'projected-shadow'/f'{f:04}.png').getchannel('A').filter(ImageFilter.GaussianBlur(1.3)).resize(bg.size,Image.Resampling.LANCZOS)
 alpha=np.rint(np.array(a,dtype=np.float32)*ma*.60).astype(np.uint8);sh=Image.new('RGBA',bg.size,(83,91,96,0));sh.putalpha(Image.fromarray(alpha))
 vehicle=Image.open(color or P/'vehicles'/f'{f:04}.png').convert('RGBA')
 return Image.alpha_composite(Image.alpha_composite(bg,sh),vehicle).convert('RGB')
if __name__=='__main__':
 import sys
 if '--pilot' in sys.argv:
  f=385;im=compose(f,P.parent/'fleet-coupling-v11-2026-10-07'/f'vehicles-{f:04}.png');im.save(P/'pilot-composite-0385.png');print('pilot ready');raise SystemExit
 dest=P/'fleet-v11-48s.mp4';cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1334','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-threads','4',str(dest)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);start=time.monotonic()
 try:
  for f in range(1,1153):
   im=compose(f);proc.stdin.write(im.tobytes())
   if f in [1,230,385,769,1152]:im.save(P/f'video-frame-{f:04}.png')
   if f%24==0:print('ENCODE',f,flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration,codec_name','-of','json',str(dest)],text=True));stream=probe['streams'][0];assert int(stream['nb_read_frames'])==1152;assert stream['r_frame_rate']=='24/1';assert float(stream['duration'])==48;assert stream['width']==1920 and stream['height']==1334
 receipt={'video':dest.name,'probe':probe,'encode_seconds':time.monotonic()-start,'geometry_source':'fleet-v11-video.blend','background':'../fleet-road-v11-2026-10-07/backdrop-v11.png','receiver_mask':'../fleet-lookdev-v10-2026-10-07/road-receiver-mask.png','shadow':'animated actual mesh projection along same SUN direction; half-resolution coverage with1.3px Gaussian penumbra, upscaled LANCZOS; RGB83,91,96 alpha0.60; roadmask excludes painted roofs','frame_generation':'1152 separately evaluated and rendered source animation frames; no repeated still slideshow'};(P/'video-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
