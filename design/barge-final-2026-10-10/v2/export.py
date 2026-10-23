from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

r = Path(__file__).parent
p = Path('public/scene-art/barge-family-v1')
pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
c = canvas.Canvas(str(r / 'energy-plus-barge-v2.pdf'), pagesize=(842, 595))

def title(text):
    c.setFont('DV', 14)
    c.drawString(24, 568, text)
    c.setFont('DV', 9)
    c.drawRightString(818, 568, 'V2 · 10.10.2026')

def picture(path, x, y, w, h):
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    c.drawImage(str(path), x + (w - iw * scale) / 2, y + (h - ih * scale) / 2, iw * scale, ih * scale)

title('Погрузка на баржу · композиция')
c.drawString(24, 534, 'До')
picture(p / 'choice-neutral-wide-v2.webp', 24, 290, 794, 230)
c.drawString(24, 270, 'После · 1983 × 793')
picture(p / 'choice-neutral-wide-v3.webp', 24, 20, 794, 240)
c.showPage()
title('Вертикальный кадр · 948 × 1659')
c.drawString(24, 534, 'До')
c.drawString(428, 534, 'После')
picture(p / 'choice-neutral-tall-v2.webp', 24, 24, 390, 500)
picture(p / 'choice-neutral-tall-v3.webp', 428, 24, 390, 500)
c.showPage()
title('В игре · 393 × 852 / 1440 × 900')
picture(r / 'screens/393-choice.png', 24, 24, 235, 520)
picture(r / 'screens/1440-choice.png', 280, 24, 538, 520)
c.showPage()
c.save()
