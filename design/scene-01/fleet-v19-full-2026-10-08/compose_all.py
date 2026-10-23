from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,subprocess
P=Path(__file__).resolve().parent
city=P.parent/'fleet-v19-city-occlusion-2026-10-08/city/city-brand-final.png'
bg=Image.open(city).convert('RGBA')
mask=np.asarray(Image.open(P.parent/'fleet-lookdev-v10-2026-10-07/road-receiver-mask.png').convert('L'),dtype=np.float32)/255
assert bg.size==(1920,1334)
def compose(f):
 alpha=Image.open(P/'turn-shadow'/f'{f:04}.png').getchannel('A').filter(ImageFilter.GaussianBlur(1.3)).resize(bg.size,Image.Resampling.LANCZOS)
 alpha=np.rint(np.asarray(alpha,dtype=np.float32)*mask*.48).astype(np.uint8)
 shadow=Image.new('RGBA',bg.size,(83,91,96,0));shadow.putalpha(Image.fromarray(alpha))
 vehicle=Image.open(P/'turn-vehicles'/f'{f:04}.png').convert('RGBA')
 assert vehicle.size==bg.size
 return Image.alpha_composite(Image.alpha_composite(bg,shadow),vehicle).convert('RGB')
output=P/'v19-full-current-8s.mp4'
proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1334','-r','24','-i','-','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
frames=[1,24,48,72,96,120,144,168,192]
sheet=Image.new('RGB',(1440,1065),'white')
for f in range(1,193):
 im=compose(f);proc.stdin.write(im.tobytes())
 if f in frames:
  im.save(P/f'map-{f:04}.png');thumb=im.resize((480,334),Image.Resampling.LANCZOS);i=frames.index(f);x=i%3*480;y=i//3*355;sheet.paste(thumb,(x,y));ImageDraw.Draw(sheet).text((x+8,y+337),f'frame {f} / {(f-1)/24:.3f}s',fill='black')
proc.stdin.close();assert proc.wait()==0
sheet.save(P/'contact-sheet.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames,r_frame_rate,duration','-of','json',str(output)]))
s=probe['streams'][0];assert s['nb_read_frames']=='192' and s['duration']=='8.000000' and s['r_frame_rate']=='24/1'
decode=subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-']).returncode;assert decode==0
(P/'validation.json').write_text(json.dumps({'video':output.name,'probe':probe,'decode_exit':decode,'source_frames':[1,192],'complete_current_source':True,'source':'../fleet-v19-city-occlusion-2026-10-08/occlusion/city-occlusion.blend','city':str(city),'shadow_source':'freshly rendered matching192 current compact-axle frames','scope':'complete8second current source; not previous48second old game clip; not assumed seamless loop; no gameplay mutation'},indent=2))
print(json.dumps(probe),flush=True)
