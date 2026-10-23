from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
r=Path(__file__).parent;p=Path('public/scene-art/lastmile-family-v1')
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(r/'energy-plus-chums-v4.pdf'),pagesize=(842,595))
def title(t):
 c.setFont('DV',14);c.drawString(24,568,t);c.setFont('DV',9);c.drawRightString(818,568,'V4 · 09.10.2026')
def image(path,x,y,w,h):
 iw,ih=Image.open(path).size;s=min(w/iw,h/ih);c.drawImage(str(path),x+(w-iw*s)/2,y+(h-ih*s)/2,iw*s,ih*s)
def detail(path,x,y):
 iw,ih=Image.open(path).size;s=390/403
 c.saveState();clip=c.beginPath();clip.rect(x,y,390,320*s);c.clipPath(clip,stroke=0)
 c.drawImage(str(path),x-1580*s,y-(ih-320)*s,iw*s,ih*s);c.restoreState()
title('Чумы · деталь · V7 → V8');c.drawString(24,520,'До');c.drawString(428,520,'После')
detail(p/'choice-final-wide-v7.webp',24,125);detail(p/'choice-final-wide-v8.webp',428,125);c.showPage()
title('Игра · 393 × 852 / 1440 × 900')
image(r/'screens/393-choice.png',24,25,235,520);image(r/'screens/1440-choice.png',282,25,536,520);c.showPage();c.save()
