from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
r=Path(__file__).parent;s=r/'screens'
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(r/'energy-plus-lastmile-markers-v1.pdf'),pagesize=(842,595))
def head(title):
 c.setFont('DV',14);c.drawString(24,570,title);c.setFont('DV',9);c.drawRightString(818,570,'V1 · 10.10.2026')
def pic(path,x,y,w,h):
 iw,ih=Image.open(path).size;k=min(w/iw,h/ih)
 c.drawImage(str(path),x+(w-iw*k)/2,y+(h-ih*k)/2,iw*k,ih*k)
head('Последняя миля · мобильный экран')
for i,(label,path) in enumerate([('До',Path('/home/michael/.cache/tmp/codex-clipboard-iBIKwo.png')),('После · 393 × 852 px',s/'v1-393x852.png')]):
 x=24+i*404;c.setFont('DV',10);c.drawString(x,535,label);pic(path,x,24,390,495)
c.showPage();head('Последняя миля · 1440 × 900 px');pic(s/'v1-1440x900.png',24,24,794,520)
c.showPage();head('Выбранный транспорт · 393 × 852 px')
for i,(label,path) in enumerate([('1 · Вертолёт',s/'v1-selected-helicopter-393x852.png'),('3 · Роботизированная тележка',s/'v1-selected-robot-393x852.png')]):
 x=24+i*404;c.setFont('DV',10);c.drawString(x,535,label);pic(path,x,24,390,495)
c.showPage();c.save();print(r/'energy-plus-lastmile-markers-v1.pdf')
