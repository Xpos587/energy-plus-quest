from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
font = '/usr/share/fonts/TTF/DejaVuSans.ttf'
pages = []
for frame, title in [(1, 'Начало цикла'), (576, 'Проезд по карте'), (1536, 'Перед повтором')]:
    page = Image.new('RGB', (1600, 1250), '#f6f5f0')
    draw = ImageDraw.Draw(page)
    draw.text((50, 25), f'Карта v20 · {title}', font=ImageFont.truetype(font, 32), fill='#193446')
    draw.text((50, 75), f'Кадр {frame} из 1536 · 64 секунды · 24 кадра/с · 1920 × 1334', font=ImageFont.truetype(font, 21), fill='#536472')
    im = Image.open(P / f'map-{frame:04}.png').convert('RGB')
    im.thumbnail((1500, 1050))
    page.paste(im, ((1600-im.width)//2, 130))
    draw.text((50, 1200), 'Полный игровой цикл. Движение, колёса и дым замыкаются на начало.', font=ImageFont.truetype(font, 20), fill='#536472')
    pages.append(page)
pages[0].save(P/'v20-game-loop-review.pdf', save_all=True, append_images=pages[1:], resolution=144)
print(P/'v20-game-loop-review.pdf')
