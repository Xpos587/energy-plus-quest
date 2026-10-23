from pathlib import Path
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
O=Path(__file__).resolve().parent;root=O.parents[2]
bg=Image.open(O.parent/'four-truck-loop-2026-10-04/v2b-empty-map.png').convert('RGBA').resize((3840,2667),Image.Resampling.LANCZOS)
now=bg.copy();now.alpha_composite(Image.open(O/'map-vehicles-final.png').convert('RGBA'));now.convert('RGB').save(O/'map-final.png');now.resize((1505,1045),Image.Resampling.LANCZOS).convert('RGB').save(O/'map-final-review.png')
old=bg.copy();old.alpha_composite(Image.open(O.parent/'painted-layer-2026-10-05/final-4k-frames/0769.png').convert('RGBA'))
box=(1975,958,2088,1114)
old.crop(box).convert('RGB').save(O/'cab-before-native.png');now.crop(box).convert('RGB').save(O/'cab-after-native.png')
comparison=Image.new('RGB',(928,624),'white');comparison.paste(old.crop(box).resize((452,624),Image.Resampling.NEAREST),(0,0));comparison.paste(now.crop(box).resize((452,624),Image.Resampling.NEAREST),(476,0));comparison.save(O/'cab-before-after-final-4x.png')
detail=Image.new('RGBA',(1200,1200),(242,247,249,255));detail.alpha_composite(Image.open(O/'green-detail-final.png').convert('RGBA'));detail.convert('RGB').save(O/'green-detail-review.png')
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(O/'energy-plus-green-uv-v1.pdf'),pagesize=(842,595));c.setTitle('Зелёная фура — UV v1')
def title(text,sub):
    c.setFillColorRGB(.08,.18,.24);c.setFont('D',18);c.drawString(24,563,text);c.setFont('D',9);c.setFillColorRGB(.35,.43,.48);c.drawRightString(818,563,sub)
def image(path,x,y,w,h):
    im=Image.open(path).convert('RGB');iw,ih=im.size;scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale;stream=BytesIO();im.save(stream,format='JPEG',quality=94,subsampling=0);stream.seek(0);c.drawImage(ImageReader(stream),x+(w-dw)/2,y+(h-dh)/2,dw,dh)
def label(text,x,y):c.setFont('D',10);c.setFillColorRGB(.12,.22,.28);c.drawString(x,y,text)
title('Зелёная фура · UV v1','05.10.2026 · статичный кадр')
label('До · 4×',25,529);label('После · 4×',244,529);label('Модель · другой ракурс',463,529)
image(O/'cab-before-native.png',24,214,200,300);image(O/'cab-after-native.png',243,214,200,300);image(O/'green-detail-review.png',462,204,356,320)
label('Эталон фуры',24,190);image(root/'public/scene-art/carrier-results-2026-10-02/crew-wide-v6.webp',24,28,794,152)
c.showPage();title('Первая сцена · пробный кадр','Карта 3840×2667 · текстура 1254×1254')
image(O/'map-final.png',24,24,794,520);c.showPage();c.save()
