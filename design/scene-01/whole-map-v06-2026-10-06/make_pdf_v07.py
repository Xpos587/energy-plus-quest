from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
P=Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(P/'energy-plus-map-v07.pdf'),pagesize=(842,595))
def title(t):c.setFont('Review',14);c.drawString(24,566,t)
def pic(path,x,y,w,h):
    im=Image.open(path);iw,ih=im.size;s=min(w/iw,h/ih)
    c.drawImage(ImageReader(im),x+(w-iw*s)/2,y+(h-ih*s)/2,iw*s,ih*s)
for label,path in [('До · v05',P.parent/'whole-map-render-2026-10-06/map-0001.png'),('После · v07',P/'map-v07-0001.png')]:
    title('Первая сцена · '+label);pic(path,24,40,794,510)
    c.setFont('Review',9);c.drawString(24,20,'v07 · 1920 × 1334 · 48 с · 24 fps' if 'v07' in label else 'Предыдущая версия');c.showPage()
title('Склад · до / после · эталон')
for label,path,x in [('До',P/'backdrop/warehouse-before.png',24),('После · v07',P/'backdrop/warehouse-after.png',294),('Эталон',P/'backdrop/reference-warehouse.png',564)]:
    c.setFont('Review',11);c.drawString(x,530,label);pic(path,x,130,250,380)
c.showPage();title('Первая сцена · v07 · 16 с / 32 с')
pic(P/'map-v07-0385.png',24,80,386,450);pic(P/'map-v07-0769.png',432,80,386,450)
c.showPage();title('Зелёная фура · два водителя · v07')
pic(P/'fleet/textured-v07-green-desktop-visible.png',24,35,510,510)
pic(P.parents[2]/'public/review/carrier-art-2026-09-27/closer-crew.png',564,170,250,300)
c.setFont('Review',10);c.drawString(564,490,'Референс карточки');c.save();print(P/'energy-plus-map-v07.pdf')
