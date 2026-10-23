"""Runnable asset contract: python scripts/scene1-live/test_assets.py."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

root = Path(__file__).resolve().parents[2]
assets = root/'public/scene1-live'
source = root/'public/review/map-geometry/pass-18/map.png'
original = Image.open(source).convert('RGB')
clean = Image.open(assets/'environment.png').convert('RGB')
mask = Image.open(assets/'environment-repair-mask.png').convert('L')
assert clean.size == original.size == mask.size
changed = ImageChops.difference(clean,original)
protected = ImageChops.invert(mask)
assert ImageChops.multiply(changed,Image.merge('RGB',(protected,)*3)).getbbox() is None, 'Non-truck pixels changed outside the repair support'
assert ImageChops.difference(clean,Image.open(assets/'environment.webp').convert('RGB')).getbbox() is None, 'Lossy backdrop changes protected original pixels'
provenance = json.loads((assets/'provenance.json').read_text())
assert provenance['sourceMapSHA256'] == hashlib.sha256(source.read_bytes()).hexdigest()
assert provenance['registrationCorrelation'] > .98
metadata = json.loads((assets/'atlas.json').read_text())
assert metadata['cabOrthoScale'] == 7.5 and metadata['trailerOrthoScale'] == 8.4 and metadata['trailerAnchorHeight'] == 1.7
# These stripe interiors were crossed by the old truck3 roof's unremoved black edge.
for x,y in [(1115,264),(1127,265),(1141,267)]:
    pixel = clean.getpixel((round(x*clean.width/1400),round(y*clean.width/1400)))
    assert min(pixel) > 180, ('Truck3 roof spike remains on crossing',x,y,pixel)
assert metadata['steeringRadians'] == .5
palette = Image.open(assets/'warehouse-palette-mask.png').convert('L')
assert palette.getbbox() is not None
# The former blue belt is warm/light; the sign remains dark, not erased.
k = clean.width/1400
r,g,b = clean.getpixel((round(365*k),round(297*k)))
assert r > b and min(r,g,b) > 150, ('Warehouse still has a dark blue belt',r,g,b)
for family in ['old-cab','near-cab','crew-cab','old-cab-turn','near-cab-turn','crew-cab-turn','old-chassis','near-chassis','crew-chassis','old-trailer','new-trailer']:
    image = Image.open(assets/f'{family}.webp').convert('RGBA')
    assert image.size == (3072,1536)
    hashes = set()
    for heading in range(72):
        x,y = heading%12*256, heading//12*256
        cell = image.crop((x,y,x+256,y+256))
        bounds = cell.getchannel('A').getbbox()
        assert bounds and bounds[0] > 0 and bounds[1] > 0 and bounds[2] < 256 and bounds[3] < 256, (family,heading,'clipped or empty')
        hashes.add(hashlib.sha256(cell.tobytes()).hexdigest())
    assert len(hashes) == 72, f'{family} is not 72 distinct real heading renders'
for family in ['old','near','crew']:
    straight = Image.open(assets/f'{family}-cab.webp').convert('RGBA')
    turning = Image.open(assets/f'{family}-cab-turn.webp').convert('RGBA')
    assert ImageChops.difference(straight,turning).getbbox(), f'{family} front wheels never steer'
print('PASS: protected source pixels, warm warehouse belt, lossless plate, eleven unclipped 72-heading atlases and actual steering variants')
