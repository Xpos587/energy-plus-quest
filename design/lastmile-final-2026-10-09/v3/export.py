from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
r=Path(__file__).parent;p=Path('public/scene-art/lastmile-family-v1')
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(r/'energy-plus-lastmile-v3.pdf'),pagesize=(842,595))
def image(path,x,y,w,h):
 iw,ih=Image.open(path).size;s=min(w/iw,h/ih);c.drawImage(str(path),x+(w-iw*s)/2,y+(h-ih*s)/2,iw*s,ih*s)
def title(t):
 c.setFont('DV',14);c.drawString(24,568,t);c.setFont('DV',9);c.drawRightString(818,568,'V3 · 09.10.2026')
def comparison(title_text,a,b,label):
 title(title_text);c.drawString(24,527,label);image(p/a,80,284,682,240)
 c.drawString(24,267,'После · V7');image(p/b,80,20,682,240);c.showPage()
comparison('Стиль · 1983 × 793','choice-final-wide-v6.webp','choice-final-wide-v7.webp','До · V6')
comparison('Площадка · перенос на сушу','choice-final-wide-v5.webp','choice-final-wide-v7.webp','До · V5')
title('Игра · 393 × 852 / 1440 × 900')
image(r/'screens/393-choice.png',24,25,235,520);image(r/'screens/1440-choice.png',282,25,536,520);c.showPage();c.save()
