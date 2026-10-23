from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
p=Path(__file__).parent;r=Path('/home/michael/Github/energy-plus-quest')
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(p/'map-v13-style.pdf'),pagesize=(842,595))
def title(t):c.setFont('D',17);c.drawString(24,567,t)
for name,label in [('map-v12.png','Исходный кадр · V12'),('map-v13.png','Рисованная стилистика · V13')]:
 title(label);c.drawImage(str(p/name),50,30,width=742,height=515,preserveAspectRatio=True);c.showPage()
title('V13 · сравнение с принятыми сценами')
c.drawImage(str(p/'map-v13.png'),24,100,width=420,height=425,preserveAspectRatio=True)
for file,label,y in [('warehouse-neutral-2026-10-03/wms-v2.webp','Склад',306),('barge-family-v1/petr-boat-v12.png','Баржа',60)]:
 c.setFont('D',11);c.drawString(465,y+210,label);c.drawImage(str(r/'public/scene-art'/file),465,y,width=350,height=197,preserveAspectRatio=True)
c.showPage();title('Зелёная фура · схема маршрута')
x,y,w,h=50,35,742,515;c.drawImage(str(p/'map-v13.png'),x,y,width=w,height=h)
def q(a,b):return(x+a/1506*w,y+(1045-b)/1045*h)
z=c.beginPath();z.moveTo(*q(742,390));z.lineTo(*q(742,675));z.curveTo(*q(742,753),*q(788,753),*q(830,753));z.lineTo(*q(1055,753));z.curveTo(*q(1145,753),*q(1145,705),*q(1145,650));z.lineTo(*q(1145,190));z.curveTo(*q(1145,103),*q(1100,103),*q(1040,103));z.lineTo(*q(840,103));z.curveTo(*q(742,103),*q(742,155),*q(742,200));z.lineTo(*q(742,390));c.setStrokeColorRGB(.0,.55,.25);c.setLineWidth(3);c.setDash(6,4);c.drawPath(z)
c.setFont('D',9);c.drawString(24,15,'Направление: вниз → направо → вверх → налево. Габариты на поворотах ещё проверяются.')
c.save()
