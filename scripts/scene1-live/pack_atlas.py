"""Pack true 3D heading renders without recolouring the approved painted textures."""
from pathlib import Path
import json
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-22-live/atlas')
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'public/scene1-live'
OUT.mkdir(parents=True,exist_ok=True)
for family in ['old-cab','near-cab','crew-cab','old-cab-turn','near-cab-turn','crew-cab-turn','old-chassis','near-chassis','crew-chassis','old-trailer','new-trailer']:
    sheet = Image.new('RGBA',(256*12,256*6))
    for heading in range(72):
        image = Image.open(SOURCE / f'{family}-{heading:02}.png').convert('RGBA')
        assert image.size == (512,512)
        image = image.resize((256,256),Image.Resampling.LANCZOS)
        alpha = image.getchannel('A')
        assert alpha.getbbox(), f'Empty {family} heading {heading}'
        assert not any(alpha.getpixel(point) for point in [(0,128),(255,128),(128,0),(128,255)]), f'Clipped {family} heading {heading}'
        sheet.paste(image,((heading%12)*256,(heading//12)*256))
    sheet.save(OUT / f'{family}.webp',lossless=True)
(OUT/'atlas.json').write_text(json.dumps({
    'headings':72,'cell':256,'columns':12,'cabOrthoScale':7.5,'trailerOrthoScale':8.4,'trailerAnchorHeight':1.7,
    'camera':[8,-100,120],
    'source':'pass-22-live: authored cab/glass/crew/wheel geometry, cel-painted materials and physical fittings; approved18 trailer panel texture; no reconstructed camera-projected cab mesh',
    'articulation':'separate cab, chassis and trailer headings; physical front wheel steering through 0.5 radians; chassis always beneath cargo; continuous premultiplied heading/steering sampling',
    'steeringRadians':.5,
    'crew':'Two seated modeled humans inside an actual windshield cavity behind transparent front glazing',
    'oldFamily':'Maintained slate blue-gray low cab with glass reflections, panel ink and circular headlights; cream worn trailer',
    'nearFamily':'Lower blue modern cab beside warehouse; same coherent modern vehicle paint family',
},indent=2)+'\n')
print('Packed eleven coherent-geometry 72-heading atlases, including front-wheel steering.')
