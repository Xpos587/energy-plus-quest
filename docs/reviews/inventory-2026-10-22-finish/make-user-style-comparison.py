from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[3]
review = Path(__file__).resolve().parent
font_path = Path('/usr/share/fonts/TTF/DejaVuSans.ttf')
assert font_path.is_file()
font = ImageFont.truetype(str(font_path), 26)
small = ImageFont.truetype(str(font_path), 20)
canvas = Image.new('RGB', (1700, 850), '#f4f7fa')
draw = ImageDraw.Draw(canvas)
draw.text((35, 25), 'Склад: сравнение стиля — промежуточный вариант', font=font, fill='#18364c')
panels = [
    (root / 'public/scene-art/warehouse-revision-4-2026-10-18/overview-r4-v11-local.png', 35, 'Исходная иллюстрация', 'Референс стиля. Её геометрия ранее отклонена.'),
    (review / 'rack-worldplane-v1-full-source.png', 875, 'Единая геометрия, новый кандидат', 'Стиль пока не принят. В игру не перенесён.'),
]
for path, left, title, note in panels:
    draw.text((left, 85), title, font=font, fill='#18364c')
    image = Image.open(path).convert('RGB')
    image.thumbnail((790, 600), Image.Resampling.LANCZOS)
    canvas.paste(image, (left + (790 - image.width) // 2, 135 + (600 - image.height) // 2))
    draw.text((left, 755), note, font=small, fill='#465d6b')
draw.text((35, 805), 'Проверяются стиль и читаемость. Это не подтверждение runtime и не готовая замена.', font=small, fill='#8b4a18')
canvas.save(review / 'warehouse-style-user-comparison-pending.png')
