from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pathlib import Path
p=Path(__file__).parent
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(p/'map-v11-review.pdf'),pagesize=(842,595))
for name,label in [('map-v10.png','Исходный кадр · V10'),('map-v11.png','Новый вариант · V11')]:
 c.setFont('D',18);c.drawString(24,567,label)
 img=ImageReader(str(p/name));w,h=img.getSize()
 c.setFont('D',10);c.drawString(24,548,f'{w} × {h} px · статичная карта')
 c.drawImage(img,47,25,width=748,height=515,preserveAspectRatio=True,anchor='c');c.showPage()
c.save()
