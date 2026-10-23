from pathlib import Path
import re
import textwrap
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

r = Path(__file__).parent
art = Path('public/scene-art/barge-family-v1')
source = Path('docs/scenario.md').read_text()
pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
c = canvas.Canvas(str(r / 'energy-plus-barge-rush-v6.pdf'), pagesize=(842, 595))

def heading(title):
    c.setFont('DV', 14)
    c.drawString(24, 569, title)
    c.setFont('DV', 9)
    c.drawRightString(818, 569, 'V6 · 10.10.2026')

def picture(path, x, y, w, h):
    iw, ih = Image.open(path).size
    s = min(w / iw, h / ih)
    c.drawImage(str(path), x + (w - iw * s) / 2, y + (h - ih * s) / 2, iw * s, ih * s)

heading('Иван идёт на кран · до / после')
for i, (label, version) in enumerate([('До · V5', 3), ('После · V6', 4)]):
    y = 300 - i * 270
    c.setFont('DV', 11)
    c.drawString(24, y + 235, label)
    picture(art / f'outcome-rush-neutral-v{version}.webp', 24, y, 794, 220)
c.showPage()

path = art / 'outcome-rush-neutral-v4.webp'
iw, ih = Image.open(path).size
heading(f'Иван идёт на кран · {iw} × {ih}')
picture(path, 24, 132, 794, 412)
c.setFont('DV', 10)
y = 110
for id in ['0023E31A', '27629778']:
    body = re.search(r'<!-- scenario-block id="' + id + r'" role="text"[^>]*-->(.*?)<!-- /scenario-block -->', source, re.S).group(1)
    text = '\n'.join(line[2:] for line in body.splitlines() if line.startswith('> '))
    for line in textwrap.wrap(text, width=125):
        c.drawString(24, y, line)
        y -= 14
    y -= 10
c.showPage()
heading('Иван · деталь · до / после')
for i, (label, version) in enumerate([('До · V5', 3), ('После · V6', 4)]):
    x, y, w, h = 24 + i * 404, 40, 390, 470
    c.setFont('DV', 11)
    c.drawString(x, 535, label)
    path = art / f'outcome-rush-neutral-v{version}.webp'
    iw, ih = Image.open(path).size
    rx, ry, rw, rh = 400, 300, 240, 400
    s = min(w / rw, h / rh)
    cx, cy = x + (w - rw * s) / 2, y + (h - rh * s) / 2
    c.saveState()
    clip = c.beginPath()
    clip.rect(cx, cy, rw * s, rh * s)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(str(path), cx - rx * s, cy - (ih - ry - rh) * s, iw * s, ih * s)
    c.restoreState()
c.showPage()
c.save()
