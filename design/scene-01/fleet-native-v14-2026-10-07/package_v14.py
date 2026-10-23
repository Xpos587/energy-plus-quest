from pathlib import Path
from PIL import Image,ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(__file__).resolve().parent;OLD=P.parent/'fleet-clean-v13-2026-10-07'
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'));doc=canvas.Canvas(str(P/'energy-plus-fleet-v14.pdf'),pagesize=(842,595));doc.setTitle('Энергия+ · перевозчики v14 · карта и модели')
def text(t,x,y,size=12):doc.setFont('Review',size);doc.setFillColorRGB(.15,.23,.28);doc.drawString(x,y,t)
def pic(path,x,y,w,h):
 im=Image.open(path).convert('RGBA');flat=Image.new('RGBA',im.size,(243,247,246,255));flat.alpha_composite(im);doc.drawImage(ImageReader(flat.convert('RGB')),x,y,w,h,preserveAspectRatio=True,anchor='c')
def title(t,sub=''):
 text(t,24,567,17)
 if sub:text(sub,24,546,10)
def page():doc.showPage()
title('Карта · v14 · пилот', 'Кадр 385 · новая геометрия старых кабин, общий свет и тени');pic(P/'map-v14-0385.png',24,20,794,518);page()
title('До / после · та же карта, тот же кадр 385');text('v13',24,530);text('v14',432,530)
pic(OLD/'map-v13-0385.png',24,243,386,277);pic(P/'map-v14-0385.png',432,243,386,277)
for j,(name,rect) in enumerate((('red',(930,824,1042,1038)),('blue',(580,947,815,1095)),('green',(1150,999,1390,1128)),('yellow',(1510,266,1620,473)))):
 for ver,base in (('v13',OLD),('v14',P)):
  out=P/f'{ver}-map-crop-{name}.png';Image.open(base/f'map-{ver}-0385.png').crop(rect).save(out)
  pic(out,24+j*200,24 if ver=='v14' else 124,185,94)
text('v13',24,224,9);text('v14',24,116,9);page()
title('Карта · v14', 'Кадр 1 · маршруты, масштаб, камера и склад сохранены');pic(P/'map-v14-0001.png',24,20,794,518);page()
for i,label in ((1,'Красный · низкая старая кабина'),(4,'Жёлтый · компактная коробчатая кабина')):
 title(label,'Слева v13 · справа v14');pic(OLD/f'v13-front-{i}.png',24,60,386,454);pic(P/f'v14-front-{i}.png',432,60,386,454);page()
title('Современные машины · разная высота кабин','Слева v13 · справа v14; сверху синий, снизу зелёный')
for i,y in ((2,285),(3,20)):
 pic(OLD/f'v13-front-{i}.png',24,y,386,251);pic(P/f'v14-front-{i}.png',432,y,386,251)
page();title('Четыре кабины · v14','Единая отделка колёс и металла · персонажи сохранены')
for i,(x,y) in enumerate(((24,285),(432,285),(24,20),(432,20)),1):pic(P/f'v14-front-{i}.png',x,y,386,251)
doc.save()
# Structural image evidence, generated from native object pass rather than painted artwork.
Image.open(P/'ids-0385.png').convert('RGB').filter(ImageFilter.FIND_EDGES).save(P/'edges-0385.png')
print(P/'energy-plus-fleet-v14.pdf')
