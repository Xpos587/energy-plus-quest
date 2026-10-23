from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
r=Path(__file__).parent
p=Path('public/scene-art/lastmile-family-v1')
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(r/'energy-plus-lastmile-v2.pdf'),pagesize=(842,595))
def image(path,x,y,w,h):
 iw,ih=Image.open(path).size;s=min(w/iw,h/ih)
 c.drawImage(str(path),x+(w-iw*s)/2,y+(h-ih*s)/2,iw*s,ih*s)
def title(t):
 c.setFont('DV',14);c.drawString(24,568,t)
 c.setFont('DV',9);c.drawRightString(818,568,'V2 · 09.10.2026')
title('Последний этап · 1983 × 793')
c.drawString(24,527,'До');image(p/'choice-final-wide-v4.webp',80,284,682,240)
c.drawString(24,267,'После');image(p/'choice-final-wide-v6.webp',80,20,682,240);c.showPage()
title('Трубовоз · результат · 1672 × 941')
c.drawString(24,532,'До');c.drawString(430,532,'После')
image(p/'pipecarrier-rescue-final-v3.webp',24,40,390,480)
image(p/'pipecarrier-return-swim-v4.webp',428,40,390,480);c.showPage()
title('Игра · выбор / результат · 393 × 852')
image(r/'screens/393-choice.png',24,25,390,520)
image(r/'screens/393-boat-pipe.png',428,25,390,520);c.showPage()
title('Игра · результат · 1440 × 900')
image(r/'screens/1440-boat-pipe.png',24,24,794,520);c.showPage()
c.save()
