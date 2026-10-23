from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;video=P/'v20-game-loop-64s.mp4';D=P/'decoded-seam';D.mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf','select=eq(n\\,0)+eq(n\\,1)+eq(n\\,1534)+eq(n\\,1535)','-fps_mode','passthrough',str(D/'%02d.png')],check=True)
sheet=Image.new('RGB',(1280,960),'white')
for k,label in enumerate(('First frame, t=0','Second frame','Penultimate frame','Last frame, t=63.958s')):
 im=Image.open(D/f'{k+1:02d}.png').convert('RGB').resize((640,445),Image.Resampling.LANCZOS);x=k%2*640;y=k//2*480;sheet.paste(im,(x,y+25));ImageDraw.Draw(sheet).text((x+10,y+5),label,fill='black')
sheet.save(P/'decoded-seam-sheet.png')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-filter_complex','[0:v]split=2[a][b];[a]trim=start=63:end=64,setpts=PTS-STARTPTS[tail];[b]trim=start=0:end=1,setpts=PTS-STARTPTS[head];[tail][head]concat=n=2:v=1:a=0,scale=960:667:flags=lanczos,pad=960:668:0:0[v]','-map','[v]','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'seam-inspection-last-second-first-second.mp4')],check=True)
print('ENCODED_SEAM_READY',flush=True)
