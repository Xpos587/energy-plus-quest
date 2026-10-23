from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent

def frames(name):
 path=P/name;p=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(path)],text=True))['streams'][0];w,h=p['width'],p['height'];proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(path),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
 for n in range(96):
  data=proc.stdout.read(w*h*3);assert len(data)==w*h*3;yield n,Image.frombytes('RGB',(w,h),data)
 assert proc.stdout.read(1)==b'';proc.stdout.close();assert proc.wait()==0
out=Image.new('RGB',(1920,2016),'white');chosen=[0,5,33,95]
for n,im in frames('wheels-style-fixed-world-closeups-4s.mp4'):
 if n in chosen:out.paste(im,(0,chosen.index(n)*504))
out.save(P/'decoded-fixed-world-motion-sheet.png')
out=Image.new('RGB',(2304,1488),'#eceee9');d=ImageDraw.Draw(out)
windows=[range(5,11),range(33,39),range(90,96)]
for n,im in frames('wheels-style-chassis-follow-subpixel-4s.mp4'):
 for row,window in enumerate(windows):
  if n in window:
   col=n-window.start;crop=im.crop((row*384,0,(row+1)*384,472));out.paste(crop,(col*384,row*496+24));d.text((col*384+10,row*496+6),f'Decoded source frame {97+n}',fill='black')
out.save(P/'decoded-dense-chassis-motion-sheet.png')
print('Decoded fixed-world and dense chassis sheets ready')
