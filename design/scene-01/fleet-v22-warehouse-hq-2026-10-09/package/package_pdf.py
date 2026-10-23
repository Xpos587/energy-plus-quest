from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape,A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
pdfmetrics.registerFont(TTFont('D','/usr/share/fonts/TTF/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('DB','/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'))
W,H=landscape(A4);c=canvas.Canvas(str(P/'v22-scene-review.pdf'),pagesize=(W,H))
def text(x,y,t,size=12,bold=False):c.setFont('DB'if bold else'D',size);c.setFillColorRGB(.06,.17,.25);c.drawString(x,y,t)
def fit(file,x,y,w,h):
 im=Image.open(file);a,b=im.size;k=min(w/a,h/b);c.drawImage(str(file),x+(w-a*k)/2,y+(h-b*k)/2,a*k,b*k,mask='auto')
def title(t,sub):text(28,H-35,t,20,True);text(28,H-58,sub,10)
title('Первая сцена · v22','Полный цикл: 64 секунды · 24 кадра/с · 3840 × 2668')
fit(P/'map-0001.png',24,28,W-48,H-107);c.showPage()
title('Цифровой склад','Фотография из сценария от 08.10.2026 и восстановленный облик на игровой карте')
text(28,H-86,'Референс сценария',12,True);text(W/2+16,H-86,'В игре',12,True)
fit(ROOT/'docs/scenario-assets/image8.png',28,125,W/2-54,H-225);fit(P.parent/'city/warehouse-final-crop.png',W/2+16,92,W/2-42,H-194)
text(28,64,'Сохранены: ломаное остекление, ступенчатый корпус, синий навес.',11)
text(28,44,'Три места погрузки и маркировка «Склад» — по требованиям игровой сцены.',11);c.showPage()
title('Качество при приближении','Одинаковый участок карты в одинаковом экранном размере')
old=Image.open(P.parents[1]/'fleet-v20-game-loop-2026-10-08/map-0001.png').crop((170,180,540,570));old.save(P/'before-warehouse.png')
text(28,H-86,'Раньше · исходник видео 1920 px',12,True);text(W/2+16,H-86,'Теперь · исходник видео 3840 px',12,True)
fit(P/'before-warehouse.png',28,93,W/2-54,H-199);fit(P.parent/'city/warehouse-final-crop.png',W/2+16,93,W/2-42,H-199)
text(28,60,'Фуры отрендерены в 4K; фон улучшен отдельно, склад детализирован локально.',10)
text(28,42,'При максимальном 4× зуме масштаб всё ещё может превышать нативное разрешение.',10)
c.save();print('PDF_READY')
