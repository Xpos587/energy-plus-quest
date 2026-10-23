from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pathlib import Path
root=Path(__file__).parent
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(root/'energy-plus-crop-v1.pdf'),pagesize=(842,595))
def title(t):
 c.setFont('DejaVu',15);c.drawString(24,567,t)
 c.setFont('DejaVu',9);c.drawRightString(818,567,'V1 · 05.10.2026')
for names,heading in [(['inventory-entrance','inventory-keeper','inventory-wms'],'Склад · экран 393 × 852'),(['carrier-crew','lastmile-helicopter','compact-place-3'],'Результаты · экран 393 × 852')]:
 title(heading)
 for i,name in enumerate(names):
  c.drawImage(str(root/f'{name}-393.png'),48+i*263,24,width=235,height=509,preserveAspectRatio=True,anchor='c')
 c.showPage()
title('Лодка · место №3 · экран 1440 × 900')
c.drawImage(str(root/'compact-place-3-1440.png'),24,40,width=794,height=496,preserveAspectRatio=True,anchor='c')
c.showPage();c.save()
