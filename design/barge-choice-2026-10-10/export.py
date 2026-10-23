from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
root=Path(__file__).parent
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(root/'energy-plus-barge-choice-v1.pdf'),pagesize=(842,595))
def heading(title):
 c.setFont('DV',14);c.drawString(24,570,title)
 c.setFont('DV',9);c.drawRightString(818,570,'V1 · 10.10.2026')
def picture(path,x,y,w,h):
 iw,ih=Image.open(path).size;s=min(w/iw,h/ih)
 c.drawImage(str(path),x+(w-iw*s)/2,y+(h-ih*s)/2,iw*s,ih*s)
for width,height in [(1440,900),(393,852),(320,568),(820,1180)]:
 heading(f'Погрузка на баржу · {width} × {height} px')
 if width==1440:
  for i,label in enumerate(['До','После']):
   y=290-i*265;c.setFont('DV',10);c.drawString(24,y+245,label)
   picture(root/'screens'/f'{"before" if i==0 else "after"}-{width}.png',24,y,794,235)
 else:
  for i,label in enumerate(['До','После']):
   c.setFont('DV',10);c.drawString(24+i*404,535,label)
   picture(root/'screens'/f'{"before" if i==0 else "after"}-{width}.png',24+i*404,24,390,495)
 c.showPage()
heading('Перед подтверждением · 393 × 852 px')
for i,(id,label) in enumerate([('rush','1 · Иван'),('wait','2 · По графику'),('petr','3 · Пётр'),('remote','4 · Из офиса')]):
 x=24+i*200;c.setFont('DV',10);c.drawString(x,535,label)
 picture(root/'screens'/f'inspection-{id}-393.png',x,24,190,495)
c.showPage();c.save()
print(root/'energy-plus-barge-choice-v1.pdf')
