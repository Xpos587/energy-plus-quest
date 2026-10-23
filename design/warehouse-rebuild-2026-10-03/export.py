from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import json
H=Path(__file__).resolve().parent; R=H.parents[1]
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(H/'energy-plus-warehouse-review-v2.pdf'),pagesize=(842,595)); c.setTitle('Склад · Основной кадр и эмоции · 03.10.2026')
def page(title,imgs,note=''):
 c.setFillColorRGB(.08,.19,.27); c.setFont('DV',17);c.drawString(24,565,title)
 c.setFont('DV',9); c.drawRightString(818,544,'03.10.2026 · На ревью')
 cw=(794-18*(len(imgs)-1))/len(imgs)
 for i,(im,label) in enumerate(imgs):
  if isinstance(im,(Path,str)): im=Image.open(im).convert('RGB')
  w,h=im.size;s=min(cw/w,470/h);x=24+i*(cw+18)
  c.drawImage(ImageReader(im),x+(cw-w*s)/2,62+(470-h*s)/2,w*s,h*s)
  c.setFont('DV',8);c.drawString(x,43,label+f' · {w} × {h} px')
 c.setFont('DV',9);c.drawString(24,24,note);c.showPage()
old=Image.open(R/'public/scene-art/inventory-clean-family-v1.webp').convert('RGB')
new=Image.open(H/'warehouse-master-v4.png').convert('RGB')
scale_x=new.width/1672; scale_y=new.height/941
page('Основная сцена · до / после',[(old,'До'),(new,'V4')])
page('Основная сцена · V4',[(new,'Горизонтальный мастер')],'Спокойная рабочая сосредоточенность; исход ещё не определён.')
for p,title in zip(json.loads((H/'patches.json').read_text()),['Кладовщик · руки и форма','Дрон · конструкция','Погрузчик · оператор','Работник в проходе']):
 x,y,w,h=[p[k] for k in ('x','y','w','h')]
 # Old dimensions differ slightly; normalize corresponding field for honest same-area comparison.
 box=(round(x*old.width/1672),round(y*old.height/941),round((x+w)*old.width/1672),round((y+h)*old.height/941))
 page(title,[(old.crop(box),'До'),(new.crop((round(x*scale_x),round(y*scale_y),round((x+w)*scale_x),round((y+h)*scale_y))),'V4 · деталь')])
notes={'entrance':'Трактовка p356: умеренная усталость после лишнего пути, без злости.', 'keeper':'Трактовка p369/p371: уверенный совет; затем поиск и замешательство новой смены.', 'wms':'Трактовка p377: спокойная уверенность, лёгкое удовлетворение.', 'alphabet':'По p363: устали, но справились; облегчение без победного ликования.'}
entries=json.loads((R/'design/warehouse-current-2026-10-03/sources.json').read_text())
for label,rel in entries:
 if '/outcomes/' not in rel:continue
 key=next(k for k in notes if 'inventory-'+k in rel)
 page(label,[(R/'public'/rel,Path(rel).stem)],notes[key])
c.save()
print(H/'energy-plus-warehouse-review-v2.pdf')
