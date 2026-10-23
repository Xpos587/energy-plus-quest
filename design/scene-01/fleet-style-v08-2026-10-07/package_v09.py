from pathlib import Path
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'projected' / 'clean'
PREVIOUS = ROOT.parent / 'whole-map-v06-2026-10-06'
BACKGROUND = Image.open(PREVIOUS / 'backdrop/city-v06.png').convert('RGBA').resize((1920, 1334), Image.Resampling.LANCZOS)
for frame in (1, 385, 769):
    overlay = Image.open(SOURCE / f'vehicles-{frame:04d}.png').convert('RGBA')
    assert overlay.size == BACKGROUND.size
    Image.alpha_composite(BACKGROUND, overlay).convert('RGB').save(ROOT / f'map-v09-{frame:04d}.png')

pdfmetrics.registerFont(TTFont('Review', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
W, H = 842, 595
doc = canvas.Canvas(str(ROOT / 'energy-plus-map-v09.pdf'), pagesize=(W, H))
doc.setTitle('Энергия+ · Карта · v09')
def label(text, x, y, size=12):
    doc.setFont('Review', size)
    doc.setFillColorRGB(.16, .24, .3)
    doc.drawString(x, y, text)
def picture(path, x, y, w, h):
    rgba = Image.open(path).convert('RGBA')
    page_image = Image.new('RGBA', rgba.size, (247, 250, 252, 255))
    page_image.alpha_composite(rgba)
    jpeg = BytesIO()
    page_image.convert('RGB').save(jpeg, format='JPEG', quality=94)
    jpeg.seek(0)
    doc.drawImage(ImageReader(jpeg), x, y, w, h, preserveAspectRatio=True, anchor='c')
label('Карта · v09 · 1920 × 1334 · статичный кадр', 24, 569)
picture(ROOT / 'map-v09-0001.png', 24, 38, 794, 515)
doc.showPage()
label('До · v07', 24, 569)
label('После · v09', 430, 569)
picture(PREVIOUS / 'map-v07-0001.png', 24, 295, 388, 260)
picture(ROOT / 'map-v09-0001.png', 430, 295, 388, 260)
label('Эталон', 24, 275)
picture(ROOT.parent.parent / 'style-audit-2026-09-28/reference.png', 24, 24, 388, 240)
label('v09 · другой участок маршрута', 430, 275)
picture(ROOT / 'map-v09-0769.png', 430, 24, 388, 240)
doc.showPage()
label('Фуры · v09 · детали выбора', 24, 569)
names = ['Красная · старая · тент · 1 водитель', 'Синяя · современная · 1 водитель', 'Зелёная · новая · 2 водителя', 'Жёлтая · старая · тент · 1 водитель']
for i, title in enumerate(names):
    x = 24 + (i % 2) * 406
    y = 304 if i < 2 else 40
    doc.setFillColorRGB(.97, .98, .99)
    doc.roundRect(x, y, 388, 247, 8, fill=1, stroke=0)
    picture(SOURCE / f'front-{i+1}.png', x, y+19, 388, 228)
    label(title, x+8, y+6, 10)
doc.save()
print(ROOT / 'energy-plus-map-v09.pdf')
