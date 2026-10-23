from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
r=Path(__file__).parent;p=Path('public/scene-art/lastmile-family-v1')
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(r/'energy-plus-lastmile-v5.pdf'),pagesize=(842,595))
def title(t):
 c.setFont('DV',14);c.drawString(24,568,t);c.setFont('DV',9);c.drawRightString(818,568,'V5 · 09.10.2026')
def image(path,x,y,w,h):
 iw,ih=Image.open(path).size;s=min(w/iw,h/ih);c.drawImage(str(path),x+(w-iw*s)/2,y+(h-ih*s)/2,iw*s,ih*s)
title('Вертикальная карта · 948 × 1659');c.drawString(24,532,'До · V8');c.drawString(428,532,'После · V9')
image(p/'choice-final-tall-v8.webp',24,25,390,495);image(p/'choice-final-tall-v9.webp',428,25,390,495);c.showPage()
title('Широкая карта · 1983 × 793');c.drawString(24,527,'До · V8');image(p/'choice-final-wide-v8.webp',80,284,682,240)
c.drawString(24,267,'После · V9');image(p/'choice-final-wide-v9.webp',80,20,682,240);c.showPage()
title('Снегоболотоход · результаты · 1672 × 941')
for label,file,x,y in [('Посылка','rusak-parcel-final-v5.webp',24,290),('Лодка','rusak-boat-final-v5.webp',428,290),('Возврат труб','pipecarrier-return-swim-v5.webp',24,24)]:
 c.drawString(x,y+225,label);image(p/file,x,y,390,220)
c.showPage()
title('После вертолёта · доставка · 1672 × 941');c.drawString(24,532,'Посылка');c.drawString(428,532,'Лодка')
image(p/'helicopter-ground-parcel-final-v5.webp',24,40,390,480);image(p/'helicopter-ground-boat-final-v5.webp',428,40,390,480);c.showPage()
title('Игра · 393 × 852 / 1440 × 900');image(r/'screens/393-choice.png',24,25,235,520);image(r/'screens/1440-choice.png',282,25,536,520);c.showPage();c.save()
