from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,importlib.util
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v16composite',P.parent/'fleet-behavior-v16-2026-10-07/composite_motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
centers=json.loads((P/'motion-crop-centers.json').read_text())
frames=(48,52,56,60,64,68,144,148,152,156,160,164)
sheet=Image.new('RGB',(1440,1040),'#eeeeee');d=ImageDraw.Draw(sheet)
def crop(im,f,i):
 x,y=centers[str(f)][str(i)];return im.crop((int(x)-90,int(y)-130,int(x)+90,int(y)+110))
for c,f in enumerate(frames):
 im=m.compose(f,P/'turn-vehicles'/f'{f:04}.png')
 for row,i in enumerate((1,4)):
  r=c//6*2+row;col=c%6;imcrop=crop(im,f,i);sheet.paste(imcrop,(col*240+30,r*260+20));d.text((col*240+30,r*260+4),f'{f/24:.2f}s truck{i}',fill='black')
sheet.save(P/'motion-evolution-contact-sheet.png')
proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x480','-r','24','-i','-','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'smoke-tracking-crops-8s.mp4')],stdin=subprocess.PIPE)
try:
 for f in range(1,193):
  im=m.compose(f,P/'turn-vehicles'/f'{f:04}.png');canvas=Image.new('RGB',(720,480))
  for k,i in enumerate((1,4)):canvas.paste(crop(im,f,i).resize((360,480)),(360*k,0))
  proc.stdin.write(canvas.tobytes())
finally:proc.stdin.close()
assert proc.wait()==0
