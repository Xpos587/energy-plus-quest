# /// script
# dependencies = ["pillow"]
# ///
"""Export the reviewed native warehouse results without resampling the artwork.
Run from repository root: uv run scripts/finish-warehouse-results-v4.py
Only the boat/socks plaque lettering is edited; the four native masters are untouched.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops, ImageDraw, ImageFont

SOURCE = Path('design/scene-03/results-v4')
OUT = Path('public/scene-art/warehouse-results-v4')
FONT = Path('public/fonts/normalidad-proxy-bold.woff2')
PLAQUE = (1054, 232, 1115, 262)
LABELS = {'alphabet-boat': 'Л-М', 'alphabet-socks': 'Н-У'}
SIZES = {'alphabet-camera': (1999, 786), 'entrance': (2004, 785),
         'keeper': (1672, 941), 'wms': (1671, 941)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alphabet_variant(base, text):
    x1, y1, x2, y2 = PLAQUE
    w, h = x2-x1, y2-y1
    patch = Image.new('RGB', (w, h))
    # Interpolate the clean plaque surface between rows above/below the old letters.
    for x in range(w):
        top, bottom = base.getpixel((x1+x, y1-1)), base.getpixel((x1+x, y2))
        for y in range(h):
            patch.putpixel((x, y), tuple(round(a+(b-a)*(y+1)/(h+1)) for a, b in zip(top, bottom)))
    # Supersample only the new glyphs, never the underlying illustration.
    glyphs = Image.new('RGBA', (w*4, h*4))
    draw = ImageDraw.Draw(glyphs)
    font = ImageFont.truetype(str(FONT), 30*4)
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw.text(((w*4-r+l)/2-l, (h*4-b+t)/2-t), text, font=font,
              fill='#18417d', stroke_width=2, stroke_fill='#f7f5f3')
    glyphs = glyphs.rotate(2.5, resample=Image.Resampling.BICUBIC).resize((w, h), Image.Resampling.LANCZOS)
    patch.paste(glyphs, (0, 0), glyphs)
    result = base.copy()
    result.paste(patch, (x1, y1))
    delta = ImageChops.difference(base, result).getbbox()
    assert delta and x1 <= delta[0] < delta[2] <= x2 and y1 <= delta[1] < delta[3] <= y2
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    generation = json.loads((SOURCE/'generation.json').read_text())
    masters = {}
    for name, size in SIZES.items():
        path = SOURCE/f'native-{name}.png'
        assert sha(path) == generation['results'][name]['sourceSha256'], f'Unreviewed master: {name}'
        masters[name] = Image.open(path).convert('RGB')
        assert masters[name].size == size, name
    results = []
    for name in ['alphabet-boat', 'alphabet-camera', 'alphabet-socks', 'entrance', 'keeper', 'wms']:
        branch = 'alphabet-camera' if name.startswith('alphabet-') else name
        result = alphabet_variant(masters[branch], LABELS[name]) if name in LABELS else masters[branch]
        target = OUT/f'outcome-{name}.webp'
        result.save(target, lossless=True, method=6)
        decoded = Image.open(target).convert('RGB')
        assert decoded.size == result.size and decoded.tobytes() == result.tobytes(), name
        results.append({'result': name, 'source': str(SOURCE/f'native-{branch}.png'),
                        'sourceSha256': generation['results'][branch]['sourceSha256'],
                        'sha256': sha(target), 'size': list(result.size), 'lossless': True,
                        'decodedMatchesExpectedPixels': True,
                        'edit': {'text': LABELS[name], 'bounds': list(PLAQUE), 'outsideChangedPixels': 0}
                        if name in LABELS else None})
    (SOURCE/'receipt.json').write_text(json.dumps({'pipeline': 'native pixels; no artwork resampling or warping',
        'plaqueFont': str(FONT), 'plaqueFontSha256': sha(FONT), 'results': results}, indent=2, ensure_ascii=False)+'\n')
    print('Six lossless native-size outcomes: exact decoded pixels; boat/socks differ only inside the plaque.')


if __name__ == '__main__':
    main()
