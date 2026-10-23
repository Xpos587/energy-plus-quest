from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

P=Path(__file__).resolve().parent
S=P.parent/'fleet-v16-wheels-style-2026-10-08'
B=P.parent/'fleet-v16-cab-repair-2026-10-08'
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'))
out=P/'energy-plus-v16-wheels-style.pdf'
c=canvas.Canvas(str(out),pagesize=(842,595))
c.setTitle('Энергия+ · v16 · Колёса и материалы прицепов')
def text(t,x,y,size=12):
    c.setFont('Review',size);c.setFillColorRGB(.15,.23,.28);c.drawString(x,y,t)
def pic(im,x,y,w,h):
    im=im.convert('RGBA');bg=Image.new('RGBA',im.size,(244,247,246,255));bg.alpha_composite(im)
    c.drawImage(ImageReader(bg.convert('RGB')),x,y,w,h,preserveAspectRatio=True,anchor='c')
text('v16 · Колёса и материалы прицепов',24,567,17)
text('08.10.2026 · 1920 × 1334 · Видеопроба 4 с · 24 кадра/с',24,546,10)
pic(Image.open(S/'map-0130.png'),24,24,794,510);c.showPage()
text('Зелёный прицеп · Материал и стыки',24,567,17)
text('До',24,535);text('После',432,535)
for src,x in [(B/'final-map-0144.png',24),(S/'map-0144.png',432)]:
    pic(Image.open(src).crop((1000,165,1200,330)),x,85,386,430)
text('Кадр 144',24,32,10);c.showPage()
text('Колёса',24,567,17)
text('Передняя ось · Поворот',24,535)
text('Прицеп · Шины и диски',432,535)
im=Image.open(S/'final-truck1-front-f0102.png')
pic(im.crop((0,int(im.height*.50),im.width,im.height)),24,145,386,360)
pic(Image.open(S/'style-trailer3-axle-0130.png'),432,145,386,360)
text('Вращение колёс — в приложенном видео',24,32,10);c.showPage()
c.save();print(out)
