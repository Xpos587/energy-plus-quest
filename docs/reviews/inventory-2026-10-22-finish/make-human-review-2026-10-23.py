from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

review = Path(__file__).resolve().parent
root = review.parents[2]
font_path = '/usr/share/fonts/TTF/DejaVuSans.ttf'
title = ImageFont.truetype(font_path, 28)
label = ImageFont.truetype(font_path, 23)
small = ImageFont.truetype(font_path, 18)

def fit(canvas, path, box):
    x, y, w, h = box
    im = Image.open(path).convert('RGB')
    im.thumbnail((w, h), Image.Resampling.LANCZOS)
    canvas.paste(im, (x + (w - im.width) // 2, y + (h - im.height) // 2))

def lines(draw, text, xy, width, font=small, color='#496170'):
    x, y = xy
    for paragraph in text.split('\n'):
        line = ''
        for word in paragraph.split():
            trial = (line + ' ' + word).strip()
            if draw.textlength(trial, font=font) > width and line:
                draw.text((x, y), line, font=font, fill=color)
                y += 27
                line = word
            else:
                line = trial
        draw.text((x, y), line, font=font, fill=color)
        y += 27
    return y

canvas = Image.new('RGB', (1800, 720), '#f3f7fa')
d = ImageDraw.Draw(canvas)
d.text((30, 24), 'Склад: исходный стиль / текущая игра / кандидат', font=title, fill='#17384d')
panels = [
    ('Исходный стиль', root / 'public/scene-art/warehouse-revision-4-2026-10-18/overview-r4-v11-local.png', 'Референс стиля. Его геометрия ранее отклонена.'),
    ('Сейчас в игре · 4344', review / 'current-runtime-desktop-2026-10-23.png', 'Свежий кадр 1440×900. Текущий рисунок также ранее отклонён.'),
    ('Новый кандидат · не внедрён', review / 'rack-worldplane-v1-full-source.png', 'Единая геометрия. Рисованные поверхности. Стиль ждёт просмотра.'),
]
for i, (heading, image, note) in enumerate(panels):
    x = 30 + i * 590
    d.text((x, 85), heading, font=label, fill='#17384d')
    fit(canvas, image, (x, 135, 560, 430))
    lines(d, note, (x, 600), 550)
d.text((30, 678), 'Ни публикация текущего рисунка, ни геометрическая проверка кандидата не означают художественную приёмку.', font=small, fill='#8b4b1e')
canvas.save(review / 'warehouse-human-review-desktop-2026-10-23.png')

canvas = Image.new('RGB', (1500, 1080), '#f3f7fa')
d = ImageDraw.Draw(canvas)
d.text((30, 23), 'Мобильный склад: текущая игра и план панорамирования', font=title, fill='#17384d')
for x, heading, image in [
    (30, 'Сейчас: 390×844', 'current-runtime-mobile-2026-10-23.png'),
    (530, 'Кандидат: первый кадр', 'rack-worldplane-v1-full-portrait.png'),
    (1030, 'Тот же рисунок: справа', 'rack-worldplane-v1-full-pan-right.png'),
]:
    d.text((x, 85), heading, font=label, fill='#17384d')
    im = Image.open(review / image).convert('RGB')
    im.thumbnail((390, 844), Image.Resampling.LANCZOS)
    canvas.paste(im, (x + 30, 135))
lines(d, 'Приёмка и стеллаж «Л» видны сразу. Правая часть и выбор «Ф» потребуют сдвига.', (530, 770), 440)
lines(d, 'Кладовщик и WMS открываются при сдвиге вправо. Это часть того же полного рисунка.', (1030, 770), 440)
lines(d, 'Кандидат показан без интерфейса. Это статические кадры: жесты, автоподводка к выбранной зоне и сохранение четырёх кнопок в новой компоновке пока не проверены в игре.', (530, 930), 940, color='#8b4b1e')
canvas.save(review / 'warehouse-human-review-mobile-2026-10-23.png')
