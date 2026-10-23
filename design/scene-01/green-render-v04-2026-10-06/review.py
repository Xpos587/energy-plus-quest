from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
P=Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(P/'energy-plus-green-v04.pdf'),pagesize=(842,595))
c.setTitle('Энергия+ · Зелёная фура · v04')
def label(t,x,y,size=11):
 c.setFillColorRGB(.10,.21,.29);c.setFont('Review',size);c.drawString(x,y,t)
def pic(path,x,y,w,h,crop=None):
 im=Image.open(path).convert('RGBA')
 if crop:im=im.crop(crop)
 bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);k=min(w/im.width,h/im.height)
 iw,ih=im.width*k,im.height*k;c.drawImage(ImageReader(bg.convert('RGB')),x+(w-iw)/2,y+(h-ih)/2,iw,ih)
im=Image.open(P/'green-v04.png');W,H=im.size
label('Зелёная фура · статичный рендер',30,553,20);label(f'v04 · {W} × {H}',650,553)
pic(P/'green-v04.png',30,180,782,350)
label('Эталон · текущая игра',30,150)
pic(P.parents[2]/'public/scene-art/carrier-results-2026-10-02/crew-wide-v6.webp',30,25,390,115)
c.showPage()
label('Кабина · до / после',30,553,20);label('v03 → v04',693,553)
label('До · v03',30,511);label('После · v04',440,511)
pic(P.parent/'truck-style-v03-2026-10-06/three-quarter.png',30,70,370,410)
pic(P/'green-v04.png',440,70,370,410,crop=(int(W*.228),int(H*.20),int(W*.45),int(H*.49)))
c.showPage();c.save();print(f'PDF written; image dimensions {W} x {H}')
