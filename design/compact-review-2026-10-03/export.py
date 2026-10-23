from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
D=Path(__file__).resolve().parent; R=D.parents[1]; A=R/'public/compact-art'
rows=[('Основная сцена · широкий кадр','loading-clean-belts-v26.png'),('Основная сцена · вертикальный кадр','compact-environment-v26-portrait-v2.png'),('Носки · место 1','socks-zone1-unsecured-v45.png'),('Носки · место 2','socks-zone2-v37.png'),('Носки · место 3 / авторазмещение','socks-zone3-secured-v43.png'),('Носки · место 4','socks-zone4-v39.png'),('Фотоаппарат · место 1','camera-zone1-fallen-v44.png'),('Фотоаппарат · место 2','camera-zone2-v36.png'),('Фотоаппарат · место 3','camera-zone3-unload-v41.png'),('Фотоаппарат · место 4','camera-zone4-v38.png'),('Фотоаппарат · авторазмещение','camera-zone3-packed-v40.png'),('Лодка · место 1','boat-zone1-axle-v47.png'),('Лодка · место 2','boat-zone2-dishes-v46.png'),('Лодка · место 4 / авторазмещение','boat-zone4-v29.png'),('Лодка · место 3 · экран игры',str(D/'boat-place3-live.png'))]
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
c=canvas.Canvas(str(D/'energy-plus-compact-current.pdf'),pagesize=(842,595));c.setTitle('Погрузка в фуру · Текущие кадры · 03.10.2026')
for n,(title,file) in enumerate(rows,1):
 p=A/file; im=Image.open(p).convert('RGB');w,h=im.size
 c.setFillColorRGB(.08,.19,.27);c.setFont('DV',17);c.drawString(22,566,title)
 c.setFont('DV',9);c.drawRightString(820,545,f'03.10.2026 · {n}/{len(rows)}')
 s=min(798/w,480/h);c.drawImage(ImageReader(im),22+(798-w*s)/2,48+(480-h*s)/2,w*s,h*s)
 c.setFont('DV',8);c.drawString(22,23,f'{w} × {h} px · {p.name}');c.showPage()
c.save()
