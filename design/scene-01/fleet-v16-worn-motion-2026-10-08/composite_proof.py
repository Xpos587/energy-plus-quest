from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,subprocess
P=Path(__file__).resolve().parent;src=P.parent/'fleet-v16-smoke-2026-10-08'
bg=Image.open(P.parent/'fleet-road-v11-2026-10-07/backdrop-v11.png').convert('RGBA').resize((960,667),Image.Resampling.LANCZOS)
mask=Image.open(P.parent/'fleet-lookdev-v10-2026-10-07/road-receiver-mask.png').convert('L').resize((960,667),Image.Resampling.LANCZOS);ma=np.array(mask,dtype=np.float32)/255
centers=json.loads((P/'roof-tracking-centers.json').read_text())
def compose(f):
 a=Image.open(P/'turn-shadow'/f'{f:04}.png').getchannel('A').filter(ImageFilter.GaussianBlur(1.3));alpha=np.rint(np.array(a,dtype=np.float32)*ma*.48).astype(np.uint8);sh=Image.new('RGBA',bg.size,(83,91,96,0));sh.putalpha(Image.fromarray(alpha));return Image.alpha_composite(Image.alpha_composite(bg,sh),Image.open(P/'turn-vehicles'/f'{f:04}.png').convert('RGBA')).convert('RGB')
def encode(path,size):return subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s',size,'-r','24','-i','-','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
# Baseline uses approved native rendered map composite, then same960 display size.
import importlib.util
spec=importlib.util.spec_from_file_location('base',P.parent/'fleet-behavior-v16-2026-10-07/composite_motion.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
mapproc=encode(P/'worn-cab-map-proof-4s.mp4','960x668');cropproc=encode(P/'worn-cab-before-after-tracking-4s.mp4','768x960')
frames=(73,76,79,82,85,88,121,124,127,130,133,136);sheet=Image.new('RGB',(1152,960),'#eeeeee');sd=ImageDraw.Draw(sheet)
def crop(im,f,i):
 x,y=centers[str(f)][str(i)];return im.crop((round(x)-48,round(y)-38,round(x)+48,round(y)+74))
try:
 for f in range(73,169):
  im=compose(f);pad=Image.new('RGB',(960,668));pad.paste(im,(0,0));mapproc.stdin.write(pad.tobytes())
  before=base.compose(f,src/'turn-vehicles'/f'{f:04}.png').resize((960,667),Image.Resampling.LANCZOS)
  tracked=Image.new('RGB',(768,960),'#eeeeee');d=ImageDraw.Draw(tracked)
  for row,i in enumerate((1,4)):
   for col,(label,image) in enumerate((('BASELINE',before),('WORN CAB',im))):
    tracked.paste(crop(image,f,i).resize((384,448)),(col*384,row*480+24));d.text((col*384+12,row*480+6),f'{label} truck{i} source frame{f}',fill='black')
  cropproc.stdin.write(tracked.tobytes())
  if f==96:
   before.save(P/'baseline-map-proof-0096.png');tracked.save(P/'cab-before-after-0096.png')
   for i in (1,4):
    crop(before,f,i).resize((384,448)).save(P/f'cab-{i}-before-0096.png');crop(im,f,i).resize((384,448)).save(P/f'cab-{i}-after-0096.png')
  if f in frames:
   c=frames.index(f)%6;block=frames.index(f)//6
   for row,i in enumerate((1,4)):
    r=block*2+row;sheet.paste(crop(im,f,i).resize((192,224)),(c*192,r*240+16));sd.text((c*192+6,r*240+2),f'frame{f} truck{i}',fill='black')
  if f in (73,96,120,144,168):im.save(P/f'map-proof-{f:04}.png')
finally:mapproc.stdin.close();cropproc.stdin.close()
assert mapproc.wait()==0 and cropproc.wait()==0
sheet.save(P/'worn-cab-motion-contact-sheet.png')
receipt={}
for name in ('worn-cab-map-proof-4s.mp4','worn-cab-before-after-tracking-4s.mp4'):
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(P/name)],text=True));st=probe['streams'][0];assert int(st['nb_read_frames'])==96 and float(st['duration'])==4 and st['r_frame_rate']=='24/1';r=subprocess.run(['ffmpeg','-v','error','-i',str(P/name),'-f','null','-']);assert r.returncode==0;receipt[name]={'probe':probe,'full_decode_exit':r.returncode}
(P/'video-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
