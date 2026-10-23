from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).parent
REPO=ROOT.parents[2]
OUT=ROOT/'review'
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/TTF/DejaVuSans.ttf'))
PDF=OUT/'energy-plus-map-turn-v1.pdf'
c=canvas.Canvas(str(PDF),pagesize=(842,595))
c.setTitle('Энергия+ · Карта · Поворот · Проба v1')
def text(x,y,s,size=12):
    c.setFont('DejaVu',size);c.setFillColorRGB(.12,.23,.31);c.drawString(x,y,s)
def image(im,x,y,w,h):
    if isinstance(im,(str,Path)): im=Image.open(im)
    im=im.convert('RGB');iw,ih=im.size
    scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale
    c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,dw,dh)
text(28,559,'Сцена 1 · Карта · Поворот · Проба v1',19)
text(28,536,'6 с · 72 кадра · 12 кадров/с · кадр сравнения 1024 × 512',10)
text(28,503,'Исходная карта',11)
image(REPO/'design/scene-01/four-truck-loop-2026-10-04/v2b-empty-map.png',28,315,250,178)
text(294,503,'Эталон фуры',11)
image(REPO/'public/scene-art/carrier-results-2026-10-02/crew-wide-v6.webp',294,315,518,178)
guide=Image.open(ROOT/'geometry/guideframes/0035.png').convert('RGB')
alpha=Image.open(ROOT/'geometry/alphaframes/0035.png')
box=alpha.getbbox();box=(max(0,box[0]-12),max(0,box[1]-12),min(960,box[2]+12),min(909,box[3]+12))
text(28,293,'До · геометрия',11)
image(guide.crop(box),28,38,375,243)
text(430,293,'После · рисованный ключ',11)
image(Image.open(ROOT/'style/key-0035.png').crop(box),430,38,375,243)
c.showPage()
text(28,559,'Сцена 1 · Поворот на 90° · Проба v1',19)
text(28,536,'Последовательность · 6 с · 12 кадров/с',10)
for j,i in enumerate((0,14,28,42,56,71)):
    frame=Image.open(OUT/'transfer-three'/f'{i:04}.png').crop((512,27,1024,512))
    col=j%3;row=j//3;x=28+col*265;y=288-row*248
    text(x,y+218,f'{i/12:.2f} с',10)
    image(frame,x,y,251,208)
c.save()
print(str(PDF))
