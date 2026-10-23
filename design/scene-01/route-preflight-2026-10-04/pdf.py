from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
p=Path(__file__).parent
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(p/'map-v12-route.pdf'),pagesize=(842,595))
for src,title in [(p.parent/'map-preflight-2026-10-04/map-v11.png','Исходный кадр · V11'),(p/'map-v12.png','Новый стартовый кадр · V12'),(p/'map-v12.png','Зелёная фура · схема замкнутого маршрута')]:
 c.setFont('D',17);c.drawString(24,570,title)
 x,y,w,h=50,35,742,515
 c.drawImage(str(src),x,y,width=w,height=h)
 if 'схема' in title:
  def q(a,b):return (x+a/1506*w,y+(1045-b)/1045*h)
  path=c.beginPath();path.moveTo(*q(742,390));path.lineTo(*q(742,675));path.curveTo(*q(742,753),*q(788,753),*q(830,753));path.lineTo(*q(1055,753));path.curveTo(*q(1145,753),*q(1145,705),*q(1145,650));path.lineTo(*q(1145,190));path.curveTo(*q(1145,103),*q(1100,103),*q(1040,103));path.lineTo(*q(840,103));path.curveTo(*q(742,103),*q(742,155),*q(742,200));path.lineTo(*q(742,390))
  c.setStrokeColorRGB(.04,.5,.23);c.setLineWidth(3);c.setDash(6,4);c.drawPath(path)
  c.setDash();c.setFillColorRGB(.04,.5,.23)
  for a,b,dx,dy in [(742,435,0,1),(940,753,1,0),(1145,400,0,-1),(935,103,-1,0)]:
   xx,yy=q(a,b);v=c.beginPath();v.moveTo(xx+dx*9,yy-dy*9);v.lineTo(xx-dx*6+dy*5,yy+dy*6+dx*5);v.lineTo(xx-dx*6-dy*5,yy+dy*6-dx*5);v.close();c.drawPath(v,fill=1,stroke=0)
  c.setFillColorRGB(0,0,0);c.setFont('D',9);c.drawString(24,15,'Схема направления. Габариты состава на поворотах ещё не подтверждены.')
 c.showPage()
c.save()
