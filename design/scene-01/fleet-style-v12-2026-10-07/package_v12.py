from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(__file__).resolve().parent
bg=Image.open(P.parent/'fleet-road-v11-2026-10-07/backdrop-v11.png').convert('RGBA')
receiver=Image.open(P.parent/'fleet-lookdev-v10-2026-10-07/road-receiver-mask.png').convert('L')
for f in (1,385,769):
 shade=Image.open(P.parent/f'fleet-coupling-v11-2026-10-07/shadows-{f:04d}.png').convert('RGBA');shade.putalpha(ImageChops.multiply(shade.getchannel('A'),receiver))
 truck=Image.open(P/f'vehicles-{f:04d}.png').convert('RGBA')
 Image.alpha_composite(Image.alpha_composite(bg,shade),truck).convert('RGB').save(P/f'map-v12-{f:04d}.png')
font='/usr/share/fonts/TTF/DejaVuSans.ttf'
pdfmetrics.registerFont(TTFont('Review',font));doc=canvas.Canvas(str(P/'energy-plus-fleet-v12.pdf'),pagesize=(842,595));doc.setTitle('Энергия+ · Светлая палитра и состояние фур · v12')
def text(t,x,y,z=13):doc.setFont('Review',z);doc.setFillColorRGB(.15,.23,.28);doc.drawString(x,y,t)
def pic(path,x,y,w,h):
 im=Image.open(path).convert('RGBA');out=Image.new('RGBA',im.size,(243,247,249,255));out.alpha_composite(im);doc.drawImage(ImageReader(out.convert('RGB')),x,y,w,h,preserveAspectRatio=True,anchor='c')
text('Карта · v12',24,566);pic(P/'map-v12-0001.png',24,28,794,520);doc.showPage()
text('v11',24,566);text('v12',432,566);pic(P.parent/'fleet-road-v11-2026-10-07/map-v11-0001.png',24,150,386,350);pic(P/'map-v12-0001.png',432,150,386,350);text('Светлая ткань и заметные заплаты у старых; чистые жёсткие кузова у новых.',24,66,11);doc.showPage()
for i,title in enumerate(('Красная · старая','Синяя · современная','Зелёная · новая, два водителя','Жёлтая · старая'),1):
 text(title,24,566);text('v11',24,531,11);text('v12',432,531,11);pic(P/f'v11-front-{i}.png',24,125,386,386);pic(P/f'v12-front-{i}.png',432,125,386,386);doc.showPage()
doc.save()
# Comparison sheet for independent visual review.
canvasimg=Image.new('RGB',(1600,1400),'#f3f7f9');d=ImageDraw.Draw(canvasimg);ff=ImageFont.truetype(font,24)
for i in range(1,5):
 for j,ver in enumerate(('v11','v12')):
  im=Image.open(P/f'{ver}-front-{i}.png').convert('RGBA');im.thumbnail((760,300));x=j*800+20;y=(i-1)*350+35;canvasimg.paste(im,(x,y),im);d.text((x,y-27),f'{i} · {ver}',font=ff,fill='#293e4b')
canvasimg.save(P/'comparison.png')
print(P/'energy-plus-fleet-v12.pdf')
