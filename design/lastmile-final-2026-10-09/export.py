from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
r=Path(__file__).parent
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(r/'energy-plus-lastmile-final-v1.pdf'),pagesize=(842,595))
def image(p,x,y,w,h):
 iw,ih=Image.open(p).size;s=min(w/iw,h/ih);c.drawImage(str(p),x+(w-iw*s)/2,y+(h-ih*s)/2,iw*s,ih*s)
def page(t):
 c.setFont('DV',15);c.drawString(24,568,t);c.setFont('DV',9);c.drawRightString(818,568,'V1 · 09.10.2026 · сценарий 08.10')
def pair(t,a,b):
 page(t);c.setFont('DV',10)
 if 'Площадка' in t:
  c.drawString(24,525,'До');image(a,80,282,682,240);c.drawString(24,266,'После');image(b,80,20,682,240)
 else:
  c.drawString(24,535,'До');c.drawString(430,535,'После');image(a,24,25,390,495);image(b,428,25,390,495)
 c.showPage()
p=Path('public/scene-art/lastmile-family-v1')
pair('Площадка · широкий кадр',p/'choice-neutral-wide-v1.webp',p/'choice-final-wide-v4.webp')
page('Площадка · игра · 393 × 852 / 1440 × 900');image(r/'screens/393-main-choice.png',24,25,235,520);image(r/'screens/1440-main-choice.png',282,25,536,520);c.showPage()
pair('Снегоболотоход · результат',p/'rusak-parcel-result-v1.webp',p/'rusak-parcel-final-v4.webp')
pair('Трубовоз · смена транспорта',p/'pipecarrier-drone-result-v1.webp',p/'pipecarrier-rescue-final-v3.webp')
pair('После вертолёта · доставка',p/'helicopter-ground-boat-result-v3.webp',p/'helicopter-ground-boat-final-v4.webp')
page('Финал · переход · 393 × 852');image(r/'screens/393-mission.png',24,25,390,520);image(r/'screens/393-main-certificate.png',428,25,390,520);c.showPage()
c.save()
