from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pathlib import Path
p=Path(__file__).parent
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(p/'map-v10-review.pdf'),pagesize=(842,595))
def text(s,x,y,size=12):
 c.setFont('D',size);c.drawString(x,y,s)
text('Первая сцена · V10 · Статичный кадр',24,568,18)
text('1505 × 1045 px · исходник для проверки композиции',24,547,10)
c.drawImage(str(p/'map-v10.png'),47,32,width=748,height=510,preserveAspectRatio=True,anchor='c')
c.showPage()
text('Кабины · фрагменты той же карты',24,564,18)
for name,label,x in [('blue','Синяя · 1 водитель',28),('green','Зелёная · 2 водителя',440)]:
 text(label,x,523,14);c.drawImage(str(p/(name+'-crop.png')),x,78,width=320,height=420,preserveAspectRatio=True,anchor='c')
text('Увеличенные исходные пиксели; отдельная дорисовка фрагментов не применялась.',24,30,10)
c.showPage()
text('Кабины · фрагменты той же карты',24,564,18)
for name,label,x in [('red','Красная · требуется читаемый водитель',28),('yellow','Жёлтая · требуется читаемый водитель',440)]:
 text(label,x,523,12);c.drawImage(str(p/(name+'-crop.png')),x,78,width=320,height=420,preserveAspectRatio=True,anchor='c')
text('Ракурс и детализация кабин требуют доработки перед анимацией.',24,30,10)
c.save()
