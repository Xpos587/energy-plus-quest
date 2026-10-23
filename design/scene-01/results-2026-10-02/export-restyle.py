from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
c = canvas.Canvas(str(HERE / 'energy-plus-carrier-results-v3.pdf'), pagesize=(842, 595))
c.setTitle('Энергия+ · Первая сцена · Все результаты V3')

def sheet(title, entries):
    c.setFillColorRGB(.12, .22, .29)
    c.setFont('DejaVu', 19)
    c.drawString(28, 559, title)
    c.setFont('DejaVu', 9)
    c.drawRightString(814, 561, '02.10.2026 · V3 · Серия')
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

def overview():
    c.setFillColorRGB(.12,.22,.29)
    c.setFont('DejaVu',19)
    c.drawString(28,559,'Первая сцена · Четыре исхода')
    c.setFont('DejaVu',9)
    c.drawRightString(814,561,'02.10.2026 · V3')
    for i,(key,label) in enumerate([('old','Красная · Проверка документов'),('old4','Жёлтая · Проверка документов'),('near','Синяя · Неторопливый водитель'),('crew','Зелёная · Смена водителей')]):
        x=28+(i%2)*402
        y=286 if i<2 else 22
        c.drawImage(str(HERE/f'{key}-v2.png'),x,y,360,240)
        c.setFont('DejaVu',9)
        c.drawString(x,y-13,label)
    c.showPage()
overview()
for key,title in [('old','Красная · Проверка документов'),('old4','Жёлтая · Проверка документов'),('near','Синяя · Неторопливый водитель'),('crew','Зелёная · Смена водителей')]:
    sheet(title+' · До / после',[(HERE/f'{key}-v1.png','До · V1'),(HERE/f'{key}-v2.png','После · V2')])
    sheet(title,[(HERE/f'{key}-v2.png','V2')])
sheet('Эталон стилистики',[(ROOT/'design/style-audit-2026-09-28/reference.png','Эталон')])
c.save()
