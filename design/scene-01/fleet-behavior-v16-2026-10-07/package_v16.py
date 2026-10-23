from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(__file__).resolve().parent;OLD=P.parent/'fleet-readable-v15-2026-10-07'
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'))
doc=canvas.Canvas(str(P/'energy-plus-fleet-v16-technical-proof.pdf'),pagesize=(842,595));doc.setTitle('Энергия+ · v16 · Проба')
def text(t,x,y,size=12):
 doc.setFont('Review',size);doc.setFillColorRGB(.15,.23,.28);doc.drawString(x,y,t)
def pic(path,x,y,w,h):
 im=Image.open(path).convert('RGBA');flat=Image.new('RGBA',im.size,(243,247,246,255));flat.alpha_composite(im);doc.drawImage(ImageReader(flat.convert('RGB')),x,y,w,h,preserveAspectRatio=True,anchor='c')
def title(t,sub=''):
 text(t,24,567,17)
 if sub:text(sub,24,546,10)
title('v16 · Проба','Кадр 1 · 1920 × 1334');pic(P/'map-v16-0001.png',24,34,794,500);doc.showPage()
title('До / после · Проба','Кадр 385');text('До · v15',24,523);text('После · v16',432,523)
pic(OLD/'map-v15-0385.png',24,70,386,442);pic(P/'map-v16-0385.png',432,70,386,442);doc.showPage()
for i,label in ((1,'Красная машина'),(4,'Жёлтая машина')):
 title(label+' · Проба','До · v15                                      После · v16')
 pic(OLD/f'v15-front-{i}.png',24,48,386,464);pic(P/f'v16-front-{i}.png',432,48,386,464);doc.showPage()
title('Движение · Проба','v16 · 8 секунд · 24 кадра/с · 1920 × 1334')
for f,x in ((1,24),(96,296),(192,568)):
 pic(P/f'video-frame-{f:04}.png',x,140,250,350);text(f'Кадр {f}',x,117,10)
doc.save();print(P/'energy-plus-fleet-v16-technical-proof.pdf')
