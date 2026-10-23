from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import json, subprocess

ROOT = Path(__file__).parent
REPO = ROOT.parents[2]
OUT = ROOT / 'review'
OUT.mkdir(exist_ok=True)
receipt = json.loads((ROOT / 'geometry/receipt.json').read_text())
map_image = Image.open(REPO / 'design/scene-01/four-truck-loop-2026-10-04/v2b-empty-map.png').convert('RGB')
x0, y0, x1, y1 = receipt['ROI']
box = (round(x0*map_image.width), round((1-y1)*map_image.height), round(x1*map_image.width), round((1-y0)*map_image.height))
bg = map_image.crop(box).resize((512,485), Image.Resampling.LANCZOS)
bg.save(OUT/'map-crop.png')
font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',18)
for method in ('transfer','transfer-three','transfer-coordinates'):
    source = ROOT / method / 'frames'
    if len(list(source.glob('*.png'))) != 72:
        continue
    dest = OUT / method
    dest.mkdir(exist_ok=True)
    contact = Image.new('RGB',(1536,1024),'white')
    for i in range(72):
        name=f'{i:04}.png'
        rgb=Image.open(source/name).convert('RGB')
        alpha=Image.open(ROOT / method / 'prepared/alpha' / name).convert('L')
        after=bg.copy()
        # Static map preserved. A subtle contact shadow uses the same guide silhouette.
        shadow=Image.new('L',alpha.size)
        shadow.paste(alpha,(2,3))
        shadow=shadow.filter(ImageFilter.GaussianBlur(2)).point(lambda v:round(v*.14))
        after.paste((79,124,151),mask=shadow)
        after.paste(rgb,mask=alpha)
        guide=Image.open(ROOT / 'geometry/vehicleframes' / name).convert('RGBA').resize((512,485),Image.Resampling.LANCZOS)
        before=bg.copy();before.paste(guide,mask=guide.getchannel('A'))
        pair=Image.new('RGB',(1024,512),'white')
        pair.paste(before,(0,27));pair.paste(after,(512,27))
        d=ImageDraw.Draw(pair);d.text((12,4),'Blender',fill='#27475e',font=font);d.text((524,4),'Blender + painted keys + EbSynth',fill='#27475e',font=font)
        pair.save(dest/name)
        if i in (0,14,28,42,56,71):
            j=(0,14,28,42,56,71).index(i)
            contact.paste(pair.resize((768,384)),((j%2)*768,(j//2)*341))
    contact.save(OUT/f'{method}-contact.jpg',quality=94)
    subprocess.run(['ffmpeg','-y','-v','error','-framerate','12','-i',str(dest/'%04d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/f'{method}-turn.mp4')],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(OUT/f'{method}-turn.mp4'),'-vf','crop=512:485:512:27,pad=512:486:0:0:color=white','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/f'{method}-map.mp4')],check=True)
print(json.dumps({'map_roi_pixels':box,'frames':72,'fps':12,'duration_s':6,'map_changed':False,'scope':'single green turn test, not production loop'},indent=2))
