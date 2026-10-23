from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
from pathlib import Path
r=Path(__file__).parent
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(r/'energy-plus-media-crop-v2.pdf'),pagesize=(842,595))
def page(title):
 c.setFont('DV',15);c.drawString(24,568,title)
 c.setFont('DV',9);c.drawRightString(818,568,'V2 · 05.10.2026')
def img(p,x,y,w,h):
 iw,ih=Image.open(p).size;s=min(w/iw,h/ih)
 c.drawImage(str(p),x+(w-iw*s)/2,y+(h-ih*s)/2,width=iw*s,height=ih*s)
def label(t,x):
 c.setFont('DV',11);c.drawString(x,540,t)
for title,before,after in [
 ('Фура · результат · 393 × 852',r/'results/393x852-compact-camera-alva-place-1-page0.png',r/'final-results/results/393x852-compact-camera-alva-place-1-page0.png'),
 ('Склад · выбор · 393 × 852',r/'other-shots/393x852-inventory-boat-alva-choice.png',r/'other-after/393-inventory-choice.png'),
 ('Фура · выбор · 393 × 852',r/'other-shots/393x852-compact-boat-alva-choice.png',r/'other-after/393-compact-choice.png')]:
 page(title);label('До',140);label('После',550);img(before,24,20,390,500);img(after,428,20,390,500);c.showPage()
for title,p in [('Баржа · Пётр · 1440 × 900',r/'final-results/results/1440x900-crane-camera-alva-petr-page0.png'),('Вертолёт · 1440 × 900',r/'final-results/results/1440x900-lastmile-boat-arseniy-helicopter-page0.png')]:
 page(title);img(p,24,20,794,523);c.showPage()
c.save()
