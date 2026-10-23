from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

P = Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('Review', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
c = canvas.Canvas(str(P/'energy-plus-map-v06.pdf'), pagesize=(842,595))
def title(text):
    c.setFont('Review',14); c.drawString(24,566,text)
def pic(path,x,y,w,h):
    im=Image.open(path); iw,ih=im.size; scale=min(w/iw,h/ih)
    c.drawImage(ImageReader(im),x+(w-iw*scale)/2,y+(h-ih*scale)/2,iw*scale,ih*scale)
for label,path in [('До · v05',P.parent/'whole-map-render-2026-10-06/map-0001.png'),('После · v06',P/'map-0001.png')]:
    title('Первая сцена · '+label)
    pic(path,24,40,794,510)
    c.setFont('Review',9);c.drawString(24,20,'Карта · 1920 × 1334 · цикл 48 с · 24 fps' if 'v06' in label else 'Предыдущая версия карты')
    c.showPage()
title('Склад · до / после · эталон')
for label,path,x in [('До',P/'backdrop/warehouse-before.png',24),('После · v06',P/'backdrop/warehouse-after.png',294),('Эталон',P.parent.parent/'style-audit-2026-09-28/reference.png',564)]:
    c.setFont('Review',11); c.drawString(x,530,label)
    if label=='Эталон':
        im=Image.open(path).crop((330,120,760,490));tmp=P/'backdrop/reference-warehouse.png';im.save(tmp);path=tmp
    pic(path,x,130,250,380)
c.showPage()
title('Первая сцена · v06 · кадры цикла')
for label,path,x,y in [('0 с',P/'map-0001.png',24,300),('16 с',P/'map-0385.png',432,300),('32 с',P/'map-0769.png',24,45)]:
    c.setFont('Review',9);c.drawString(x,y+235,label);pic(path,x,y,386,225)
c.save()
print(P/'energy-plus-map-v06.pdf')
