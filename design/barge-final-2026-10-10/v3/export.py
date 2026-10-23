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
cases = [
    ('rush', 'Иван идёт на кран', '0023E31A', ['27629778'], 'rush-camera-v2.png'),
    ('wait', 'Ожидание по графику', '553650B7', ['14753450'], 'wait-camera-v1.png'),
    ('petr', 'Помощь Петра', '0C6EC2FC', ['42344E38', '64BD7433'], 'petr-camera-v8.png'),
    ('remote', 'Управление из ПРУ', '5EDD1701', ['77362BA7', '5A05E1F5', '44E790DE'], 'remote-camera-v3.png'),
]
pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
c = canvas.Canvas(str(r / 'energy-plus-barge-outcomes-v3.pdf'), pagesize=(842, 595))

def block(id):
    body = re.search(r'<!-- scenario-block id="' + id + r'" role="text"[^>]*-->(.*?)<!-- /scenario-block -->', source, re.S).group(1)
    return '\n'.join(line[2:] for line in body.splitlines() if line.startswith('> '))

def heading(title):
    c.setFont('DV', 14)
    c.drawString(24, 569, title)
    c.setFont('DV', 9)
    c.drawRightString(818, 569, 'V3 · 10.10.2026')

def picture(path, x, y, w, h):
    iw, ih = Image.open(path).size
    s = min(w / iw, h / ih)
    c.drawImage(str(path), x + (w - iw * s) / 2, y + (h - ih * s) / 2, iw * s, ih * s)

for after in [False, True]:
    heading('Погрузка на баржу · ' + ('После' if after else 'До'))
    for i, (id, title, label, results, old) in enumerate(cases):
        x = 24 + (i % 2) * 404
        y = 300 - (i // 2) * 270
        c.setFont('DV', 11)
        c.drawString(x, y + 235, title)
        picture(art / (f'outcome-{id}-neutral-v1.webp' if after else old), x, y, 390, 220)
    c.showPage()

for id, title, label, results, old in cases:
    path = art / f'outcome-{id}-neutral-v1.webp'
    iw, ih = Image.open(path).size
    heading(f'{title} · {iw} × {ih}')
    c.setFont('DV', 10)
    for i, line in enumerate(textwrap.wrap(block(label), width=125)):
        c.drawString(24, 542 - i * 14, line)
    picture(path, 24, 169, 794, 345)
    c.setFont('DV', 10)
    y = 146
    for result in results:
        for line in textwrap.wrap(block(result), width=125):
            c.drawString(24, y, line)
            y -= 14
        y -= 6
    c.showPage()
c.save()
