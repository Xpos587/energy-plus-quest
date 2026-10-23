from pathlib import Path
from io import BytesIO
from PIL import Image, ImageChops, ImageFilter, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

P = Path(__file__).resolve().parent
SHADOW = P.parent / 'fleet-grounding-v10-2026-10-07'
OLD = P.parent / 'fleet-style-v08-2026-10-07'
bg = Image.open(P.parent / 'whole-map-v06-2026-10-06/backdrop/city-v06.png').convert('RGBA').resize((1920, 1334), Image.Resampling.LANCZOS)
h, s, v = bg.convert('RGB').convert('HSV').split()
mask = ImageChops.multiply(h.point(lambda x: 255 if 135 <= x <= 159 else 0), s.point(lambda x: 255 if 40 <= x <= 145 else 0))
mask = ImageChops.multiply(mask, v.point(lambda x: 255 if x >= 120 else 0))
mask = mask.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.MinFilter(17))
assert mask.getpixel((600, 700)) == 255
ImageDraw.floodfill(mask, (600, 700), 128, thresh=0)
mask = mask.point(lambda x: 255 if x == 128 else 0).filter(ImageFilter.GaussianBlur(.6))
mask.save(P / 'road-receiver-mask.png')
for frame in (1, 385, 769):
    shade = Image.open(SHADOW / f'shadows-{frame:04d}.png').convert('RGBA')
    shade.putalpha(ImageChops.multiply(shade.getchannel('A'), mask))
    shade.save(P / f'ground-shadows-{frame:04d}.png')
    vehicles = Image.open(P / f'vehicles-{frame:04d}.png').convert('RGBA')
    result = Image.alpha_composite(Image.alpha_composite(bg, shade), vehicles).convert('RGB')
    result.save(P / f'map-v10-{frame:04d}.png')

pdfmetrics.registerFont(TTFont('Review', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
doc = canvas.Canvas(str(P / 'energy-plus-map-v10.pdf'), pagesize=(842, 595))
doc.setTitle('Энергия+ · Карта · v10')
def label(text, x, y, size=12):
    doc.setFont('Review', size); doc.setFillColorRGB(.16,.24,.3); doc.drawString(x,y,text)
def picture(path,x,y,w,h):
    rgba=Image.open(path).convert('RGBA'); im=Image.new('RGBA',rgba.size,(247,250,252,255)); im.alpha_composite(rgba)
    stream=BytesIO(); im.convert('RGB').save(stream,format='JPEG',quality=94); stream.seek(0)
    doc.drawImage(ImageReader(stream),x,y,w,h,preserveAspectRatio=True,anchor='c')
label('Карта · v10 · 1920 × 1334 · статичный кадр',24,569)
picture(P/'map-v10-0001.png',24,38,794,515); doc.showPage()
label('До · v09',24,569); label('После · v10',430,569)
picture(OLD/'map-v09-0001.png',24,295,388,260); picture(P/'map-v10-0001.png',430,295,388,260)
label('v10 · поворот',24,275); label('v10 · другой участок маршрута',430,275)
picture(P/'map-v10-0385.png',24,24,388,240); picture(P/'map-v10-0769.png',430,24,388,240); doc.showPage()
label('Фуры · v10 · детали выбора',24,569)
names=['Красная · старая · 1 водитель','Синяя · современная · 1 водитель','Зелёная · новая · 2 водителя','Жёлтая · старая · 1 водитель']
for i,title in enumerate(names,1):
    x=24+((i-1)%2)*406; y=304 if i<3 else 40
    doc.setFillColorRGB(.97,.98,.99); doc.roundRect(x,y,388,247,8,fill=1,stroke=0)
    source=P/f'front-{i}.png' if i in (1,4) else OLD/'projected/clean'/f'front-{i}.png'
    picture(source,x,y+19,388,228); label(title,x+8,y+6,10)
doc.save()
print(P/'energy-plus-map-v10.pdf')
