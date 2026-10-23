from pathlib import Path
from PIL import Image,ImageDraw
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
P=Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(P/'energy-plus-whole-map.pdf'),pagesize=(842,595));c.setTitle('Энергия+ · Первая сцена · Вся карта')
for frame in [1,385,769]:
 c.setFillColorRGB(.10,.20,.28);c.setFont('Review',19);c.drawString(24,559,'Первая сцена · вся карта')
 c.setFont('Review',10);c.drawRightString(818,561,f'{(frame-1)/24:g} с · 48 с · 24 fps')
 im=Image.open(P/f'map-{frame:04}.png').convert('RGB');w,h=im.size;k=min(794/w,505/h)
 c.drawImage(ImageReader(im),(842-w*k)/2,25,w*k,h*k);c.showPage()
c.save()
sheet=Image.new('RGB',(1800,1250),'white');d=ImageDraw.Draw(sheet)
for j,frame in enumerate([1,97,385,577,769,961]):
 im=Image.open(P/f'map-{frame:04}.png').convert('RGB');im.thumbnail((600,590));x=(j%3)*600;y=(j//3)*625
 sheet.paste(im,(x,y+30));d.text((x+10,y+8),f'frame {frame} / {(frame-1)/24:.2f}s',fill='black')
sheet.save(P/'contact-sheet.png');print('Whole-map PDF and contact sheet written')
