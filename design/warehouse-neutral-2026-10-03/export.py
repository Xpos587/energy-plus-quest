from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
H=Path(__file__).resolve().parent;R=H.parents[1]
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(H/'energy-plus-warehouse-neutral-v1.pdf'),pagesize=(842,595));c.setTitle('Склад · Единые результаты · V1')
rows=[('entrance','У приёмки','Лишний путь: работник опирается на тележку, переводит дух.','panorama'),('keeper','Поиск новой сменой','Сменщики сверяют документы и ищут посылку.','family'),('alphabet','По алфавиту','Груз собран: работник остановился вытереть лоб.','panorama'),('wms','WMS','Спокойная работа: посылка найдена и готова к отгрузке.','family')]
def page(title,entries,note):
 c.setFillColorRGB(.08,.19,.27);c.setFont('DV',18);c.drawString(24,560,title)
 c.setFont('DV',9);c.drawRightString(818,538,'03.10.2026 · V1 · На ревью')
 cw=(794-18*(len(entries)-1))/len(entries)
 for i,(p,label) in enumerate(entries):
  im=Image.open(p).convert('RGB');w,h=im.size;s=min(cw/w,458/h);x=24+i*(cw+18)
  c.drawImage(ImageReader(im),x+(cw-w*s)/2,62+(458-h*s)/2,w*s,h*s)
  c.setFont('DV',8);c.drawString(x,44,f'{label} · {w} × {h} px')
 c.setFont('DV',10);c.drawString(24,24,note);c.showPage()
for key,title,note,fmt in rows:
 old=R/f'public/scene-art/outcomes/inventory-{key}-boat-{fmt}-v1.webp';new=H/f'{key}-v1.png'
 page(title+' · до / после',[(old,'До'),(new,'После')],note)
 page(title,[(new,'Единый кадр для всех подарков')],note)
c.save()
print(H/'energy-plus-warehouse-neutral-v1.pdf')
