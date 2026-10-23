from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
root=Path(__file__).parent
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(root/'energy-plus-barge-choice-v2.pdf'),pagesize=(842,595))
def head(title):
 c.setFont('DV',14);c.drawString(24,570,title)
 c.setFont('DV',9);c.drawRightString(818,570,'V2 · 10.10.2026')
def pic(p,x,y,w,h):
 iw,ih=Image.open(p).size;s=min(w/iw,h/ih)
 xx=x+(w-iw*s)/2;yy=y+(h-ih*s)/2
 c.drawImage(str(p),xx,yy,iw*s,ih*s)
 return xx,yy,s,ih
head('Погрузка на баржу · предложение композиции')
p=root/'choice-console-preview.png'
if not p.exists():p=root/'choice-spacing-preview.png'
x,y,s,ih=pic(p,24,135,794,398)
for label,px,py in [('1',1135,402),('2',1179,402),('3',1644,256),('4',308,332)]:
 xx=x+px*s;yy=y+(ih-py)*s
 c.setFillColorRGB(0.02,.37,.61);c.setStrokeColorRGB(1,1,1);c.setLineWidth(.7)
 c.roundRect(xx-8,yy-8,16,16,3,fill=1,stroke=1)
 c.setFillColorRGB(1,1,1);c.setFont('DV',10);c.drawCentredString(xx,yy-3,label)
c.setFillColorRGB(0,0,0);c.setFont('DV',10)
for i,text in enumerate(['1 · Отправить Ивана на кран','2 · Дождаться плановой работы крана через 3 часа','3 · Попросить Петра помочь','4 · Иван управляет краном из офиса']):
 c.drawString(24,111-i*20,text)
c.showPage()
head('Основная игра · 393 × 852 px')
for i,(label,p) in enumerate([('Без выбора',root.parent/'screens'/'thin-393.png'),('Выбран вариант 1',root.parent/'screens'/'inspection-rush-393.png')]):
 x=24+i*404;c.setFont('DV',10);c.drawString(x,535,label)
 pic(p,x,24,390,495)
c.showPage();c.save();print(root/'energy-plus-barge-choice-v2.pdf')
