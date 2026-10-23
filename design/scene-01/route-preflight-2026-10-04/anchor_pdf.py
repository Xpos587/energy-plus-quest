from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
p=Path(__file__).parent;r=Path('/home/michael/Github/energy-plus-quest')
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(p/'map-v16-reference.pdf'),pagesize=(842,595))
for src,title in [(r/'design/style-audit-2026-09-28/reference.png','Эталон стиля · одобрен Федей со слов Михаила'),(r/'public/review/carrier-map-2026-09-28/map-style-v6.png','Предыдущая рисованная карта · дополнительный референс'),(p/'map-v12.png','Исходная композиция · V12'),(p/'map-v16.png','Новый вариант по эталону · V16')]:
 c.setFont('D',15);c.drawString(24,567,title);c.drawImage(str(src),40,25,width=762,height=520,preserveAspectRatio=True,anchor='c');c.showPage()
c.setFont('D',17);c.drawString(24,565,'Эталон и V16 · рядом')
for src,title,x in [(r/'design/style-audit-2026-09-28/reference.png','Эталон',24),(p/'map-v16.png','V16',433)]:
 c.setFont('D',12);c.drawString(x,506,title);c.drawImage(str(src),x,180,width=385,height=305,preserveAspectRatio=True,anchor='c')
c.save()
