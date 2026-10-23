"""Create stable floating-point follow crops and truly fixed-world proof crops."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json,subprocess
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('input_video');ap.add_argument('--prefix',default='repaired');args=ap.parse_args();anchors=json.loads((P/'crop-anchors.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',args.input_video],text=True))['streams'][0];w,h=probe['width'],probe['height'];aw,ah=anchors['source_pixels'];assert w==aw and h in (ah,ah+1),(w,h,aw,ah)
decoder=subprocess.Popen(['ffmpeg','-v','error','-i',args.input_video,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
def encoder(name,size):return subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',size,'-r','24','-i','-','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(P/name)],stdin=subprocess.PIPE)
followname=f'{args.prefix}-chassis-follow-subpixel-4s.mp4';fixedname=f'{args.prefix}-fixed-world-closeups-4s.mp4'
follow=encoder(followname,'768x472');fixed=encoder(fixedname,'1280x504');contact=Image.new('RGB',(1280,2016),'#eeeeee');cd=ImageDraw.Draw(contact)
def affine(im,rect,size):
 x,y,cw,ch=rect;ow,oh=size
 return im.transform(size,Image.Transform.AFFINE,(cw/ow,0,x,0,ch/oh,y),resample=Image.Resampling.BICUBIC)
try:
 for n,f in enumerate(anchors['frames']):
  data=decoder.stdout.read(w*h*3);assert len(data)==w*h*3,(f,len(data));im=Image.frombytes('RGB',(w,h),data)
  fv=Image.new('RGB',(768,472),'#eeeeee');ff=Image.new('RGB',(1280,504),'#eeeeee');fd=ImageDraw.Draw(fv);gd=ImageDraw.Draw(ff)
  for col,i in enumerate((1,4)):
   x,y=anchors['follow_centers'][str(f)][str(i)];scale=aw/960;fc=affine(im,(x-48*scale,y-38*scale,96*scale,112*scale),(384,448));wc=affine(im,anchors['fixed_world_rectangles'][str(i)],(640,480));fv.paste(fc,(col*384,24));ff.paste(wc,(col*640,24));fd.text((col*384+12,6),f'Truck {i} / chassis-follow / no rotation',fill='black');gd.text((col*640+12,6),f'Truck {i} / FIXED WORLD / source frame {f}',fill='black')
   if f in (91,96,144,154):fc.save(P/f'{args.prefix}-subpixel-truck{i}-f{f:04}.png');wc.save(P/f'{args.prefix}-fixed-truck{i}-f{f:04}.png')
  follow.stdin.write(fv.tobytes());fixed.stdin.write(ff.tobytes())
  if f in (73,91,144,154):contact.paste(ff,(0,(73,91,144,154).index(f)*504))
 assert decoder.stdout.read(1)==b''
finally:decoder.stdout.close();follow.stdin.close();fixed.stdin.close()
assert decoder.wait()==0 and follow.wait()==0 and fixed.wait()==0
contact.save(P/f'{args.prefix}-fixed-world-contact-sheet.png')
receipt={}
for name in (followname,fixedname):
 q=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(P/name)],text=True));v=q['streams'][0];assert int(v['nb_read_frames'])==96 and v['r_frame_rate']=='24/1' and float(v['duration'])==4
 r=subprocess.run(['ffmpeg','-v','error','-i',str(P/name),'-f','null','-']);assert r.returncode==0;receipt[name]={'probe':q,'full_decode_exit':r.returncode}
(P/f'{args.prefix}-crop-video-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
