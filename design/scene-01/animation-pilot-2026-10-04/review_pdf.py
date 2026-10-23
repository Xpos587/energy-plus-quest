from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
p=Path(__file__).parent
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(p/'animation-pilot-review.pdf'),pagesize=(842,595))
for src,title in [(p.parent/'route-preflight-2026-10-04/map-v16.png','Основа стиля · V16'),(p/'map-v17-road-candidate.png','Сквозной проезд · вариант V17')]:
 c.setFont('D',17);c.drawString(24,566,title);c.drawImage(str(src),50,28,width=742,height=515,preserveAspectRatio=True);c.showPage()
c.setFont('D',17);c.drawString(24,566,'Зелёная фура · проверка движения')
c.setFont('D',11);c.drawString(24,544,'Seedance 1.5 Pro · 4 с · 24 кадра/с · начало и конец заданы')
c.drawImage(str(p/'bounded-contact.png'),24,170,width=794,height=298,preserveAspectRatio=True)
c.setFont('D',10);c.drawString(24,140,'Кадры слева направо: 0 / 0,5 / 1 / 1,5 с; второй ряд: 2 / 2,5 / 3 / 3,5 с.')
c.save()
