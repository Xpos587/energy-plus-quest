from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

P=Path(__file__).resolve().parent
S=P.parent/'fleet-v16-cab-repair-2026-10-08'
B=P.parent/'fleet-v16-smoke-2026-10-08'
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'))
out=P/'energy-plus-v16-cab-repair.pdf'
c=canvas.Canvas(str(out),pagesize=(842,595))
c.setTitle('Энергия+ · v16 · Кабина и неподвижный крупный план')
def text(t,x,y,size=12):
    c.setFont('Review',size);c.setFillColorRGB(.15,.23,.28);c.drawString(x,y,t)
def pic(im,x,y,w,h):
    c.drawImage(ImageReader(im.convert('RGB')),x,y,w,h,preserveAspectRatio=True,anchor='c')
text('v16 · 08.10.2026',24,567,17)
text('Кадр 144 · 1920 × 1334',24,546,10)
pic(Image.open(S/'final-map-0144.png'),24,24,794,510);c.showPage()
text('Красная фура · Нижняя облицовка',24,567,17)
text('До',24,535);text('После',432,535)
for src,x in [(B/'map-0144.png',24),(S/'final-map-0144.png',432)]:
    pic(Image.open(src).crop((1300,180,1435,305)),x,90,386,420)
text('Кадр 144 · Тряска сохранена · Неподвижный крупный план — в видео',24,32,10)
c.showPage();c.save();print(out)
