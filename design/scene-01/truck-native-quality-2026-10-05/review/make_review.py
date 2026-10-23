from pathlib import Path
import json
import subprocess
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

P = Path(__file__).resolve().parents[1]
R = Path(__file__).resolve().parent
R.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Review', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
C = canvas.Canvas(str(R / 'energy-plus-map-3d-v01.pdf'), pagesize=(842, 595))
C.setTitle('Энергия+ · Первая сцена · 3D-проба v01')

def title(text, meta='v01'):
    C.setFillColorRGB(.08, .17, .24)
    C.setFont('Review', 19)
    C.drawString(30, 558, text)
    C.setFont('Review', 10)
    C.setFillColorRGB(.36, .45, .50)
    C.drawRightString(810, 559, meta)

def image(path, box, trim=False):
    im = Image.open(path).convert('RGBA')
    if trim:
        im = im.crop(im.getchannel('A').getbbox())
    white = Image.new('RGBA', im.size, 'white')
    white.alpha_composite(im)
    x, y, w, h = box
    scale = min(w / im.width, h / im.height)
    iw, ih = im.width * scale, im.height * scale
    C.drawImage(ImageReader(white.convert('RGB')), x+(w-iw)/2, y+(h-ih)/2, iw, ih)

def label(text, x, y):
    C.setFont('Review', 10)
    C.setFillColorRGB(.24, .35, .43)
    C.drawString(x, y, text)

title('Первая сцена · зелёная фура')
label('Эталон · текущая игра', 30, 520)
image(P.parents[2] / 'public/scene-art/carrier-results-2026-10-02/crew-wide-v6.webp', (30, 300, 390, 200))
label('Референс для 3D', 30, 270)
image(P / 'image-to-3d/green-tractor-reference.png', (30, 38, 390, 220), True)
label('3D-проба · 900 × 900', 445, 520)
image(P / 'image-to-3d/finished-120.png', (445, 58, 365, 442), True)
C.showPage()

title('Ракурсы · одна модель и текстура', 'v01 · 900 × 900')
for path, x, name in [
    ('finished-front.png', 30, 'Спереди'),
    ('finished-120.png', 292, 'Передний ракурс'),
    ('finished-300.png', 554, 'Задний ракурс'),
]:
    label(name, x, 507)
    image(P / 'image-to-3d' / path, (x, 205, 245, 275), True)
front = Image.open(P / 'image-to-3d/finished-front.png').convert('RGBA')
crop = front.crop((285, 565, 625, 675))
white = Image.new('RGBA', crop.size, 'white')
white.alpha_composite(crop)
C.drawImage(ImageReader(white.convert('RGB')), 271, 65, 300, 97)
label('Кабина · фрагмент исходного рендера', 280, 180)
C.showPage()

motion = P / 'image-to-3d/motion'
video = motion / 'green-tractor-turn.mp4'
if video.exists():
    raw = subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
        'stream=width,height,r_frame_rate:format=duration', '-of', 'json', str(video)
    ])
    info = json.loads(raw)
    stream = info['streams'][0]
    a, b = map(int, stream['r_frame_rate'].split('/'))
    duration = float(info['format']['duration'])
    title('Поворот · проба движения', 'v01 · %.1f с · %g fps' % (duration, a/b))
    for name, x, caption in [('entry.png', 30, 'Вход'), ('apex.png', 292, 'Поворот'), ('exit.png', 554, 'Выход')]:
        label(caption, x, 507)
        image(motion / name, (x, 190, 245, 285))
    label('%d × %d · один тягач и полуприцеп' % (stream['width'], stream['height']), 30, 100)
    C.showPage()
C.save()
print('PDF written')
