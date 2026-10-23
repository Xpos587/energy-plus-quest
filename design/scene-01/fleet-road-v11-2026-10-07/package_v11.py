from pathlib import Path
from io import BytesIO
import json
from PIL import Image, ImageChops, ImageStat
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

P = Path(__file__).resolve().parent
FLEET = P.parent / 'fleet-coupling-v11-2026-10-07'
OLD = P.parent / 'fleet-lookdev-v10-2026-10-07'
old_bg = Image.open(P.parent / 'whole-map-v06-2026-10-06/backdrop/city-v06.png').convert('RGB').resize((1920,1334),Image.Resampling.LANCZOS)
generated = Image.open(P/'backdrop-generated.png').convert('RGB').resize(old_bg.size,Image.Resampling.LANCZOS)
receiver = Image.open(OLD/'road-receiver-mask.png').convert('L')
h,s,v = old_bg.convert('HSV').split()
chroma = s.point(lambda x: max(0,min(255,round((x-20)*255/30))) if x<=145 else 0)
chroma = ImageChops.multiply(chroma,h.point(lambda x: 255 if 135<=x<=159 else 0))
paint_mask = ImageChops.multiply(receiver,chroma)
bg = Image.composite(generated,old_bg,paint_mask).convert('RGBA')
bg.save(P/'backdrop-v11.png')
paint_mask.save(P/'asphalt-edit-mask.png')
protected = paint_mask.point(lambda x: 255 if x==0 else 0)
diff = ImageChops.difference(bg.convert('RGB'),old_bg)
assert all(ImageChops.multiply(c,protected).getbbox() is None for c in diff.split())
core = paint_mask.point(lambda x: 255 if x>=250 else 0)
receipt = {'source':'../whole-map-v06-2026-10-06/backdrop/city-v06.png',
    'generated_source':'backdrop-generated.png', 'method':'Imagegen asphalt edit, composited only through original connected road mask and asphalt chroma; original white road markings retained',
    'resolution':[1920,1334], 'protected_pixel_difference':0,
    'asphalt_mean_rgb_before':ImageStat.Stat(old_bg,core).mean,
    'asphalt_mean_rgb_after':ImageStat.Stat(bg.convert('RGB'),core).mean,
    'asphalt_mean_hsv_before':ImageStat.Stat(old_bg.convert('HSV'),core).mean,
    'asphalt_mean_hsv_after':ImageStat.Stat(bg.convert('RGB').convert('HSV'),core).mean}
(P/'backdrop-receipt.json').write_text(json.dumps(receipt,indent=2))
frames = (1,385,769)
for frame in frames:
    shadefile = FLEET/f'shadows-{frame:04d}.png'
    if not shadefile.exists():
        print('Backdrop ready; waiting for',shadefile.name)
        raise SystemExit(0)
    shade=Image.open(shadefile).convert('RGBA')
    shade.putalpha(ImageChops.multiply(shade.getchannel('A'),receiver))
    vehicles=Image.open(FLEET/f'vehicles-{frame:04d}.png').convert('RGBA')
    Image.alpha_composite(Image.alpha_composite(bg,shade),vehicles).convert('RGB').save(P/f'map-v11-{frame:04d}.png')

pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'))
doc=canvas.Canvas(str(P/'energy-plus-map-v11.pdf'),pagesize=(842,595))
doc.setTitle('Энергия+ · Карта · v11')
def label(text,x,y,size=12):
    doc.setFont('Review',size);doc.setFillColorRGB(.16,.24,.3);doc.drawString(x,y,text)
def picture(path,x,y,w,he):
    rgba=Image.open(path).convert('RGBA'); flat=Image.new('RGBA',rgba.size,(247,250,252,255));flat.alpha_composite(rgba)
    stream=BytesIO();flat.convert('RGB').save(stream,format='JPEG',quality=94);stream.seek(0)
    doc.drawImage(ImageReader(stream),x,y,w,he,preserveAspectRatio=True,anchor='c')
label('Карта · v11 · 1920 × 1334',24,569)
picture(P/'map-v11-0001.png',24,38,794,515);doc.showPage()
label('До · v10',24,569);label('После · v11',430,569)
picture(OLD/'map-v10-0001.png',24,295,388,260);picture(P/'map-v11-0001.png',430,295,388,260)
label('v11 · поворот',24,275);label('v11 · другой участок маршрута',430,275)
picture(P/'map-v11-0385.png',24,24,388,240);picture(P/'map-v11-0769.png',430,24,388,240);doc.showPage()
label('Сцепка · до / после',24,569)
picture(FLEET/'coupling-before-after.png',24,38,794,515);doc.showPage()
label('Фуры · v11',24,569)
for i,title in enumerate(['Красная','Синяя','Зелёная · 2 водителя','Жёлтая'],1):
    x=24+((i-1)%2)*406;y=304 if i<3 else 40
    doc.setFillColorRGB(.97,.98,.99);doc.roundRect(x,y,388,247,8,fill=1,stroke=0)
    picture(FLEET/f'front-{i}.png',x,y+19,388,228);label(title,x+8,y+6,10)
doc.save();print(P/'energy-plus-map-v11.pdf')
