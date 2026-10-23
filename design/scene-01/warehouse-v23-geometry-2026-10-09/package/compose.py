from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,subprocess,json,sys
P=Path(__file__).resolve().parent;R=P.parent/'render';W,H=3840,2668
bg=Image.open(P.parent/'city/city-final.png').convert('RGBA')
assert bg.size==(W,H)
mask=Image.open(P.parents[1]/'fleet-lookdev-v10-2026-10-07/road-receiver-mask.png').convert('L').resize((W,H),Image.Resampling.LANCZOS)
mask=np.asarray(mask,dtype=np.float32)/255

def compose(f):
 with Image.open(R/'turn-shadow'/f'{f:04}.png') as src:
  alpha=src.getchannel('A').filter(ImageFilter.GaussianBlur(2.6)).resize((W,H),Image.Resampling.LANCZOS)
 alpha=np.rint(np.asarray(alpha,dtype=np.float32)*mask*.48).astype(np.uint8)
 shadow=Image.new('RGBA',(W,H),(83,91,96,0));shadow.putalpha(Image.fromarray(alpha))
 with Image.open(R/'turn-vehicles'/f'{f:04}.png') as src:
  vehicle=src.convert('RGBA');assert vehicle.size==(W,H)
 return Image.alpha_composite(Image.alpha_composite(bg,shadow),vehicle).convert('RGB')

if __name__=='__main__':
 if '--full' not in sys.argv:
  for f in (1,384,768):
   if (R/'turn-shadow'/f'{f:04}.png').exists():compose(f).save(P/f'pilot-{f:04}.png')
  print('PILOT_COMPOSITES_READY');raise SystemExit
 # Gate: complete validated renderer, no half-written frames.
 for folder in ('turn-vehicles','turn-shadow'):
  assert all((R/folder/f'{f:04}.png').exists()for f in range(1,1538)),folder
 out=P/'v23-game-loop-64s-4k.mp4'
 # Every rendition is encoded directly from original composited pixels.
 # Avoid a second lossy encode from the master for the web variants.
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','24','-i','-','-filter_complex_threads','2','-filter_complex','[0:v]split=4[m][d][t][p];[d]scale=3600:2500:flags=lanczos[dout];[t]scale=2560:1778:flags=lanczos[tout];[p]scale=1920:1334:flags=lanczos[pout]']
 for label,file,crf in [('m',out,'15'),('dout',P/'city-motion-desktop.mp4','16'),('tout',P/'city-motion-tablet.mp4','16'),('pout',P/'city-motion-mobile.mp4','16')]:
  cmd+=['-map',f'[{label}]','-an','-c:v','libx264','-preset','medium','-crf',crf,'-threads','2','-rc-lookahead','20','-g','96','-pix_fmt','yuv420p','-movflags','+faststart',str(file)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 samples=[1,192,384,576,768,960,1152,1344,1536]
 for f in range(1,1537):
  im=compose(f);proc.stdin.write(im.tobytes())
  if f in samples:im.save(P/f'map-{f:04}.png')
  if f==1:im.save(P/'city-poster.webp',quality=95,method=6)
  if f%48==0:print('COMPOSITED',f,flush=True)
 proc.stdin.close();assert proc.wait()==0
 compose(1537).save(P/'map-1537.png')
 receipts=[]
 for file in [out,P/'city-motion-desktop.mp4',P/'city-motion-tablet.mp4',P/'city-motion-mobile.mp4']:
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(file)]));stream=probe['streams'][0]
  assert stream['nb_read_frames']=='1536'and stream['r_frame_rate']=='24/1'and float(stream['duration'])==64
  subprocess.run(['ffmpeg','-v','error','-i',str(file),'-f','null','-'],check=True)
  receipts.append({'file':file.name,'probe':probe,'decode_exit':0})
 (P/'validation.json').write_text(json.dumps(receipts,indent=2));print('ENCODE_VALIDATED',flush=True)
