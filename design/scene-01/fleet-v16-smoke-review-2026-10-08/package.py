from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'fleet-behavior-v16-2026-10-07'
NEW = HERE.parent / 'fleet-v16-smoke-2026-10-08'
pdfmetrics.registerFont(TTFont('Review', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
out = HERE / 'energy-plus-v16-smoke.pdf'
doc = canvas.Canvas(str(out), pagesize=(842, 595))
doc.setTitle('Энергия+ · v16 · Дым')

def text(value, x, y, size=12):
    doc.setFont('Review', size)
    doc.setFillColorRGB(.15, .23, .28)
    doc.drawString(x, y, value)

def pic(path, x, y, w, h):
    im = Image.open(path).convert('RGB')
    doc.drawImage(ImageReader(im), x, y, w, h, preserveAspectRatio=True, anchor='c')

text('v16 · Дым · 08.10.2026', 24, 567, 17)
text('Кадр 96 · 1920 × 1334', 24, 546, 10)
pic(NEW / 'map-0096.png', 24, 24, 794, 510)
doc.showPage()
for frame, label in [(48, 'Прямой участок'), (144, 'Поворот')]:
    text(label, 24, 567, 17)
    text('До · v16', 24, 535)
    text('После · v16 / дым', 432, 535)
    pic(OLD / f'video-frame-{frame:04d}.png', 24, 116, 386, 400)
    pic(NEW / f'map-{frame:04d}.png', 432, 116, 386, 400)
    text(f'Кадр {frame} · 1920 × 1334', 24, 36, 10)
    doc.showPage()
text('Дым · Крупный план', 24, 567, 17)
text('До · v16', 24, 535)
text('После · v16 / дым', 432, 535)
for frame, box, y, label in [
    (96, (920, 720, 1040, 900), 288, 'Жёлтая · Кадр 96'),
    (144, (1300, 160, 1530, 310), 46, 'Красная · Кадр 144'),
]:
    for directory, prefix, x in [(OLD, 'video-frame', 24), (NEW, 'map', 432)]:
        crop = Image.open(directory / f'{prefix}-{frame:04d}.png').crop(box)
        doc.drawImage(ImageReader(crop), x, y, 386, 214,
                      preserveAspectRatio=True, anchor='c')
    text(label, 24, y - 16, 10)
doc.showPage()
doc.save()
print(out)
