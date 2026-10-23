from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
P=Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'))
W,H=landscape(A4)
c=canvas.Canvas(str(P/'v23-scene-review.pdf'),pagesize=(W,H))
for title, file in [('Первая сцена · полный цикл 64 секунды', P/'map-0001.png'), ('Утверждённый склад · v23', P.parent/'warehouse-final.png')]:
    c.setFont('D',18);c.drawString(28,H-35,title)
    im=Image.open(file);w,h=im.size;k=min((W-56)/w,(H-90)/h)
    c.drawImage(str(file),(W-w*k)/2,25,w*k,h*k)
    c.showPage()
c.save()
print('PDF_READY')
