from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
r=Path(__file__).parent;s=r.parent/'screens'
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(r/'energy-plus-barge-choice-v4.pdf'),pagesize=(842,595))
def head(title):
 c.setFont('DV',14);c.drawString(24,570,title);c.setFont('DV',9);c.drawRightString(818,570,'V4 · 10.10.2026')
def pic(path,x,y,w,h):
 iw,ih=Image.open(path).size;k=min(w/iw,h/ih)
 c.drawImage(str(path),x+(w-iw*k)/2,y+(h-ih*k)/2,iw*k,ih*k)
head('Погрузка на баржу · 393 × 852 px')
for i,(label,path) in enumerate([('До',s/'v3-393x852.png'),('После',s/'v4-393x852.png')]):
 x=24+i*404;c.setFont('DV',10);c.drawString(x,535,label);pic(path,x,24,390,495)
c.showPage()
head('Погрузка на баржу · 1440 × 900 px')
pic(s/'v4-1440x900.png',24,24,794,520);c.showPage()
head('Погрузка на баржу · короткие экраны')
for i,(label,path) in enumerate([('320 × 568 px · вся страница',s/'v4-full-320x568.png'),('393 × 650 px · вся страница',s/'v4-full-393x650.png')]):
 x=24+i*404;c.setFont('DV',10);c.drawString(x,535,label);pic(path,x,24,390,495)
c.showPage()
head('Выбор объекта · 393 × 852 px')
for i,(label,path) in enumerate([('2 · Иван идёт на кран',s/'v4-selected-rush-393x852.png'),('4 · Пётр',s/'v4-selected-petr-393x852.png')]):
 x=24+i*404;c.setFont('DV',10);c.drawString(x,535,label);pic(path,x,24,390,495)
c.showPage();c.save();print(r/'energy-plus-barge-choice-v4.pdf')
