from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from composite_turn_video import compose
P=Path(__file__).resolve().parent;OLD=P.parent/'fleet-style-v12-2026-10-07'
for f in (1,385,769):compose(f,P/f'vehicles-{f:04d}.png').save(P/f'map-v13-{f:04d}.png')
for ver,base in [('v12',OLD),('v13',P)]:
 im=Image.open(base/f'map-{ver}-0001.png')
 for name,rect in [('red',(1450,620,1640,880)),('yellow',(935,415,1065,680))]:im.crop(rect).save(P/f'{ver}-{name}-roof-map-crop.png')
 im=Image.open(base/f'map-{ver}-0385.png');im.crop((500,900,820,1160)).save(P/f'{ver}-blue-map-crop.png')
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'));doc=canvas.Canvas(str(P/'energy-plus-fleet-v13.pdf'),pagesize=(842,595));doc.setTitle('Энергия+ · v13')
def text(t,x,y,size=12):doc.setFont('Review',size);doc.setFillColorRGB(.15,.23,.28);doc.drawString(x,y,t)
def pic(path,x,y,w,h):
 im=Image.open(path).convert('RGBA');flat=Image.new('RGBA',im.size,(243,247,249,255));flat.alpha_composite(im);doc.drawImage(ImageReader(flat.convert('RGB')),x,y,w,h,preserveAspectRatio=True,anchor='c')
text('Карта · v13 · 1920 × 1334',24,566);pic(P/'map-v13-0001.png',24,24,794,522);doc.showPage()
text('Крыши прицепов',24,566);text('v12',24,534);text('v13',432,534)
for j,name in enumerate(('red','yellow')):
 y=285-j*250
 pic(P/f'v12-{name}-roof-map-crop.png',24,y,386,232);pic(P/f'v13-{name}-roof-map-crop.png',432,y,386,232)
doc.showPage()
text('Холодильный блок',24,566);text('v12',24,534);text('v13',432,534)
pic(OLD/'v12-front-2.png',24,264,386,250);pic(P/'v13-front-2.png',432,264,386,250)
pic(P/'v12-blue-map-crop.png',24,24,386,225);pic(P/'v13-blue-map-crop.png',432,24,386,225);doc.save()
print(P/'energy-plus-fleet-v13.pdf')
