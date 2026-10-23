from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

P = Path(__file__).resolve().parent
S = P.parent / 'fleet-v16-worn-motion-2026-10-08'
pdfmetrics.registerFont(TTFont('Review', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
out = P / 'energy-plus-v16-worn-motion.pdf'
c = canvas.Canvas(str(out), pagesize=(842,595))
c.setTitle('Энергия+ · v16 · Тряска старых фур')
def text(t,x,y,size=12):
    c.setFont('Review',size); c.setFillColorRGB(.15,.23,.28); c.drawString(x,y,t)
def pic(p,x,y,w,h):
    c.drawImage(ImageReader(Image.open(p).convert('RGB')),x,y,w,h,preserveAspectRatio=True,anchor='c')
text('v16 · Тряска старых фур',24,567,17)
text('08.10.2026 · Видеопроба 4 с · 24 кадра/с · 960 × 668',24,546,10)
pic(S/'map-proof-0096.png',24,24,794,510);c.showPage()
for i,name in [(1,'Красная фура'),(4,'Жёлтая фура')]:
    text(name,24,567,17)
    text('До',24,535);text('После · Подвеска кабины',432,535)
    pic(S/f'cab-{i}-before-0096.png',24,72,386,440)
    pic(S/f'cab-{i}-after-0096.png',432,72,386,440)
    text('Кадр 96 · Движение — в приложенном видео',24,32,10);c.showPage()
c.save();print(out)
