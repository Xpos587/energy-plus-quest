from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
P=Path(__file__).resolve().parent
S=P.parent/'truck-native-quality-2026-10-05/image-to-3d'
pdfmetrics.registerFont(TTFont('Review','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(P/'energy-plus-green-truck-v03.pdf'),pagesize=(842,595))
c.setTitle('Энергия+ · Зелёная фура · v03')
def text(t,x,y,size=11):
 c.setFillColorRGB(.09,.19,.26);c.setFont('Review',size);c.drawString(x,y,t)
def pic(p,x,y,w,h):
 im=Image.open(p).convert('RGBA');box=im.getchannel('A').getbbox()
 if box:im=im.crop(box)
 bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
 k=min(w/im.width,h/im.height);iw,ih=im.width*k,im.height*k
 c.drawImage(ImageReader(bg.convert('RGB')),x+(w-iw)/2,y+(h-ih)/2,iw,ih)
text('Зелёная фура · кабина',30,554,21);text('v02 → v03',685,554)
text('До',30,512);text('После · два водителя внутри кабины',440,512)
pic(S/'detail-three-quarter.png',30,115,370,370)
pic(P/'body.png',440,115,370,370)
text('Эталон',30,85);pic(P.parent/'cab-detail-pilot-2026-10-05/green-detail-reference.png',100,15,180,105)
text('v03 · 1200 × 900',590,55)
c.showPage()
text('Два водителя · крупный план',30,554,21);text('v03 · 1200 × 900',650,554)
pic(P/'three-quarter.png',30,50,780,450)
c.showPage()
text('Зелёная фура · поворот',30,554,21);text('v03 · 6 с · 24 fps',647,554)
for name,x,label in [('entry',30,'Вход'),('apex',293,'Поворот'),('exit',556,'Выход')]:
 text(label,x,510);pic(P/(name+'.png'),x,190,248,290)
text('960 × 800 · тягач и полуприцеп',30,110)
c.showPage();c.save()
print('PDF written')
