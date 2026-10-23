from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
H=Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(H/'energy-plus-warehouse-neutral-v2.pdf'),pagesize=(842,595))
c.setTitle('Склад · Текущие кадры · V2')
for key,title in [('entrance','У приёмки'),('keeper','Поиск новой сменой'),('alphabet','По алфавиту'),('wms','WMS')]:
 im=Image.open(H/f'{key}-v2.png').convert('RGB');w,h=im.size
 c.setFillColorRGB(.08,.19,.27);c.setFont('DV',18);c.drawString(24,560,title)
 c.setFont('DV',9);c.drawRightString(818,560,'V2 · 03.10.2026')
 s=min(794/w,478/h)
 c.drawImage(ImageReader(im),24+(794-w*s)/2,54+(478-h*s)/2,w*s,h*s)
 c.setFont('DV',9);c.drawString(24,28,f'{w} × {h} px · Единый кадр для всех подарков')
 c.showPage()
c.save()
