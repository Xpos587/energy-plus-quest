from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
c = canvas.Canvas(str(HERE / 'energy-plus-scene-01-static-v9.pdf'), pagesize=(842, 595))
c.setTitle('Энергия+ · Первая сцена · Статика V9')

def sheet(title, entries):
    c.setFillColorRGB(.12, .22, .29)
    c.setFont('DejaVu', 19)
    c.drawString(28, 559, title)
    c.setFont('DejaVu', 9)
    c.drawRightString(814, 561, '02.10.2026 · V9 · Статичный кадр')
    width = (786 - 18 * (len(entries) - 1)) / len(entries)
    for i, (path, label) in enumerate(entries):
        img = ImageReader(str(path))
        iw, ih = img.getSize()
        scale = min(width / iw, 477 / ih)
        dw, dh = iw * scale, ih * scale
        x = 28 + i * (width + 18)
        c.drawImage(img, x + (width - dw) / 2, 54 + (477 - dh) / 2, dw, dh)
        c.setFont('DejaVu', 9)
        c.drawString(x, 30, label)
        c.drawRightString(x + width, 30, f'{iw} × {ih} px')
    c.showPage()

sheet('Первая сцена · До / после', [(HERE / 'map-v8.png', 'До · V8'), (HERE / 'map-v9.png', 'После · V9')])
sheet('Карта · V9', [(HERE / 'map-v9.png', 'Статичный кадр')])
sheet('Кабины · исходники локальной правки', [(HERE / 'v9-blue-cab-source.png', 'Синяя · один водитель'), (HERE / 'v9-green-cab-source.png', 'Зелёная · два водителя')])
c.save()
