from pathlib import Path
import json, math
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
ROOT=Path('/home/michael/Github/energy-plus-quest')
HERE=Path(__file__).resolve().parent
entries=[('Основная сцена склада','scene-art/inventory-clean-family-v1.webp')]
labels={'entrance':'У приёмки','keeper':'Опытный кладовщик','wms':'Система управления складом','alphabet':'По алфавиту'}
for key,v in [('entrance','v11'),('keeper','v11'),('wms','v10')]:
    entries.append((labels[key],f'scene-art/outcomes/inventory-{key}-{v}.webp'))
for gift,label in [('camera','камера'),('socks','носки')]:
    entries.append((f'По алфавиту · {label}',f'scene-art/outcomes/inventory-alphabet-{gift}-v10.webp'))
for fmt,label in [('panorama','широкий кадр'),('family','обычный кадр')]:
    for key in labels:
        entries.append((f'{labels[key]} · лодка · {label}',f'scene-art/outcomes/inventory-{key}-boat-{fmt}-v1.webp'))
entries.append(('Основная сцена · вертикальный кадр','scene-art/inventory-choice-tall-v1.webp'))
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/TTF/DejaVuSans.ttf'))
out=HERE/'energy-plus-warehouse-current-2026-10-03.pdf'
c=canvas.Canvas(str(out),pagesize=(842,595))
c.setTitle('Энергия+ · Склад · Текущие изображения · 03.10.2026')
for i,(label,rel) in enumerate(entries,1):
    path=ROOT/'public'/rel
    im=Image.open(path).convert('RGB'); w,h=im.size
    c.setFillColorRGB(.08,.19,.27); c.setFont('DV',17); c.drawString(24,562,label)
    c.setFont('DV',9); c.drawRightString(818,540,'Текущая версия в игре · 03.10.2026')
    scale=min(794/w,480/h); dw,dh=w*scale,h*scale
    c.drawImage(ImageReader(im),(842-dw)/2,47+(480-dh)/2,dw,dh)
    g=math.gcd(w,h)
    c.setFont('DV',8); c.drawString(24,25,f'{w} × {h} px · {w//g}:{h//g} · {path.stem}')
    c.drawRightString(818,25,f'{i} / {len(entries)}')
    c.showPage()
c.save()
(HERE/'sources.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
print(out)
print(f'{len(entries)} pages')
