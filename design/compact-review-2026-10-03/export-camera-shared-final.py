from pathlib import Path
import json
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
D=Path(__file__).resolve().parent;R=D.parents[1]
copy={x['id']:x['text'] for x in json.loads((R/'src/scenes/sourceCopy.json').read_text())}
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(D/'camera-place3-shared-final.pdf'),pagesize=(842,595))
style=ParagraphStyle('text',fontName='DV',fontSize=12,leading=17,textColor='#183b50')
def para(text,x,y,w):
 p=Paragraph(text,style);_,h=p.wrap(w,500);p.drawOn(c,x,y-h);return y-h
for title,file,pid,note in [('Фотоаппарат · место 3 · вручную','camera-zone3-packed-v40.png','p264','Финал: фотоаппарат закреплён, три коробки возвращены в кузов.'),('Фотоаппарат · место 3 · автоматически','camera-zone3-packed-v40.png','p308','Тот же финальный кадр. Порядок погрузки сценарий не описывает.')]:
 c.setFillColorRGB(.08,.19,.27);c.setFont('DV',17);c.drawString(22,565,title)
 c.setFont('DV',9);c.drawRightString(820,543,'03.10.2026 · Текущая версия')
 im=Image.open(R/'public/compact-art'/file).convert('RGB');w,h=im.size;s=min(480/w,475/h)
 c.drawImage(ImageReader(im),22+(480-w*s)/2,45+(475-h*s)/2,w*s,h*s)
 y=para('Точный текст сценария',523,512,294)-16
 y=para(copy[pid],523,y,294)-25
 y=para(note,523,y,294)
 c.setFont('DV',8);c.drawString(22,22,f'{file} · {w} × {h} px')
 c.drawRightString(820,22,f'Сценарий: правки 17.09 · {pid}')
 c.showPage()
c.save()
