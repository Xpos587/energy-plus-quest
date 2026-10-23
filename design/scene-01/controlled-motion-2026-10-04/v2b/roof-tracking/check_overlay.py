"""Draw exported native roof anchors over three exact encoded-frame source images."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

p = Path(__file__).resolve().parent
tracking = json.loads((p / 'carrier-roof-tracking.json').read_text())
assert tracking['fps'] == 24 and tracking['frames'] == 1152
rows = tracking['projected_roof_centers']
assert len(rows) == 1152 and all(len(row) == 4 and all(len(point) == 2 for point in row) for row in rows)
colors = ['#e44747', '#3275ea', '#209b5c', '#f0b318']
panels = []
for frame in (1, 385, 769):
    image = Image.open(p.parent / 'loop-frames' / f'{frame:04}.png').convert('RGB')
    assert image.size == (720, 500)
    draw = ImageDraw.Draw(image)
    for index, ((x, y), color) in enumerate(zip(rows[frame - 1], colors), 1):
        x, y = x * image.width, y * image.height
        draw.ellipse((x-6,y-6,x+6,y+6), outline='white', width=3)
        draw.ellipse((x-4,y-4,x+4,y+4), fill=color)
        draw.text((x+8,y-10), str(index), fill='white', stroke_width=2, stroke_fill='black')
    draw.rectangle((0,0,170,24), fill='white')
    draw.text((8,7), f'Native frame {frame}: {(frame-1)/24:.0f}s', fill='black')
    image.save(p / f'overlay-{frame:04}.png')
    panels.append(image)
contact = Image.new('RGB', (720 * 3, 500), 'white')
for index, image in enumerate(panels):
    contact.paste(image, (index*720, 0))
contact.save(p / 'overlay-contact.png')
print('PASS: 1152 rows x four normalized [x,y] anchors; overlays at 0s,16s,32s')
