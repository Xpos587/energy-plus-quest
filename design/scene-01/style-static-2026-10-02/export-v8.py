from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
c = canvas.Canvas(str(HERE / 'energy-plus-scene-01-static-v8.pdf'), pagesize=(842, 595))
c.setTitle('Энергия+ · Первая сцена · Статика V8')

def sheet(title, entries):
    c.setFillColorRGB(.12, .22, .29)
    c.setFont('DejaVu', 19)
    c.drawString(28, 559, title)
    c.setFont('DejaVu', 9)
    c.drawRightString(814, 561, '02.10.2026 · V8 · Статичный кадр')
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

before = HERE / 'map-v4.png'
after = HERE / 'map-v8.png'
sheet('Референсы транспорта', [(HERE / 'actual-truck-refs.png', 'Существующие модели фур')])
sheet('Первая сцена · До / после', [(before, 'До'), (after, 'После · V8')])
sheet('Карта · V8', [(after, 'Основной кадр · 1,44:1')])
sheet('Детали · кабины', [(HERE / 'v8-blue-detail.png', 'Синяя · один водитель'), (HERE / 'v8-green-detail.png', 'Зелёная · два водителя')])
sheet('Детали · склад и техника', [(HERE / 'v8-warehouse-detail.png', 'Стеклянный фасад'), (HERE / 'v8-yellow-detail.png', 'Жёлтая · 2 + 3 оси')])
sheet('Стиль проекта', [(ROOT / 'public/scene-art/barge-family-v1/petr-boat-v12.png', 'Порт'), (ROOT / 'public/scene-art/outcomes/inventory-keeper-v11.webp', 'Склад')])
c.save()
print('PDF exported: 6 pages')
