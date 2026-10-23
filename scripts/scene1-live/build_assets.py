"""Local repairs only. Requires Pillow/numpy/OpenCV (existing ComfyUI venv).
Usage: /home/michael/.local/share/comfyui/venv/bin/python scripts/scene1-live/build_assets.py
"""
from pathlib import Path
import hashlib
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'public/review/map-geometry/pass-18'
OUT = ROOT / 'public/scene1-live'
OUT.mkdir(parents=True, exist_ok=True)
source = Image.open(SOURCE / 'map.png').convert('RGB')
# Coordinates in the 1400-wide review, including the old smoke and ground shadows.
polygons = [
    [(220,85),(266,68),(268,34),(423,20),(449,51),(463,90),(364,81),(349,143),(313,146),(306,173),(230,170),(219,133)],
    [(308,424),(486,438),(513,476),(516,541),(381,544),(372,574),(342,574),(300,568),(298,521)],
    [(1064,381),(1081,251),(1153,256),(1166,302),(1150,408),(1135,473),(1118,486),(1069,486),(1058,449)],
    [(584,626),(593,588),(609,568),(754,525),(782,556),(786,598),(772,610),(749,604),(730,624),(681,645),(657,701),(608,709),(580,691)],
]
mask = Image.new('L', source.size)
draw = ImageDraw.Draw(mask)
factor = source.width / 1400
for poly in polygons:
    draw.polygon([(round(x*factor),round(y*factor)) for x,y in poly],fill=255)
# Remove the complete lower truck shadow, including its former crosswalk overlap.
shadow = [(577,625),(583,601),(602,565),(755,520),(796,553),(810,584),
          (801,624),(763,635),(719,653),(684,670),(660,717),(610,720),(580,704)]
draw.polygon([(round(x*factor), round(y*factor)) for x,y in shadow], fill=255)
# The building and visible leaves are protected original pixels, not generated replacements.
draw.polygon([(round(x*factor),round(y*factor)) for x,y in
              [(733,626),(994,647),(990,794),(716,782),(716,704)]], fill=0)
array = np.array(source)
outer_mask = np.array(mask)
leaves = ((array[:,:,0].astype(float) > array[:,:,2]*1.4) &
          (array[:,:,1].astype(float) > array[:,:,2]*1.4) &
          (array[:,:,1] > 55) & (array[:,:,1] > array[:,:,0]*.96)).astype('uint8')
region = np.zeros(mask.size[::-1], np.uint8)
region[round(594*factor):round(636*factor), round(715*factor):round(780*factor)] = 1
leaves = cv2.dilate(leaves*region, np.ones((5,5), np.uint8))
allowed = outer_mask.copy(); allowed[leaves > 0] = 0
mask = Image.fromarray(allowed)
# A painted clean plate restores actual road/crosswalk continuation. Never tile pavement
# across an arbitrary vehicle polygon: that deletes curbs and leaves triangular shadows.
clean_source = Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-20-live/scene1-clean.png')
candidate = np.array(Image.open(clean_source).convert('RGB').resize(source.size, Image.Resampling.LANCZOS))
registration_scale = .4
small = lambda image: cv2.cvtColor(cv2.resize(image, None, fx=registration_scale, fy=registration_scale), cv2.COLOR_RGB2GRAY)
valid = cv2.resize(255-allowed, None, fx=registration_scale, fy=registration_scale, interpolation=cv2.INTER_NEAREST)
correlation, transform = cv2.findTransformECC(small(array), small(candidate), np.eye(2,3,dtype=np.float32),
    cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,150,1e-5), inputMask=valid, gaussFiltSize=5)
assert correlation > .98, 'Clean plate does not register to the approved original'
transform[:,2] /= registration_scale
candidate = cv2.warpAffine(candidate, transform, source.size, flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
count, labels = cv2.connectedComponents(allowed)
for index in range(1,count):
    region = (labels == index).astype('uint8')
    ring = (cv2.dilate(region,np.ones((33,33),np.uint8))-region).astype(bool)
    correction = np.median(array[ring].astype(float)-candidate[ring].astype(float),axis=0)
    selected = region.astype(bool)
    candidate[selected] = np.clip(candidate[selected].astype(float)+correction,0,255)
weight = np.minimum(1, cv2.distanceTransform(outer_mask,cv2.DIST_L2,5)/12)
weight[allowed == 0] = 0
weight = weight[...,None]
clean_array = np.uint8(np.round(array*(1-weight)+candidate*weight))
assert np.array_equal(clean_array[allowed == 0], array[allowed == 0])
# Authorized warehouse-only palette repair: retain ink, six gates, windows and
# lettering; replace the police-van blue belt with warm limestone and dark type.
palette_mask = Image.new('L', source.size)
palette_draw = ImageDraw.Draw(palette_mask)
facade = [(334,264),(591,283),(590,379),(333,360)]
belt = [(335,288),(591,307),(591,321),(335,303)]
palette_draw.polygon([(round(x*factor),round(y*factor)) for x,y in facade], fill=255)
facade_support = np.array(palette_mask) > 0
pixels = clean_array.astype(float)
neutral = facade_support & (pixels.min(axis=2) > 100) & ((pixels.max(axis=2)-pixels.min(axis=2)) < 42)
pixels[neutral] = np.clip(pixels[neutral] * [1.04,1.025,.96] + [7,4,0], 0,255)
band = Image.new('L',source.size)
ImageDraw.Draw(band).polygon([(round(x*factor),round(y*factor)) for x,y in belt],fill=255)
band_support = np.array(band) > 0
blue = band_support & (pixels[:,:,2] > pixels[:,:,0]*1.25)
light = np.mean(pixels,axis=2)
pixels[blue] = np.stack([177+light[blue]*.35,170+light[blue]*.33,150+light[blue]*.31],axis=1)
letters = band_support & (pixels.min(axis=2) > 170) & ~blue
pixels[letters] = [62,66,62]
clean_array = np.uint8(np.round(pixels))
palette_mask.save(OUT / 'warehouse-palette-mask.png')
mask = Image.fromarray(np.maximum(np.array(mask),np.array(palette_mask)))
clean = Image.fromarray(clean_array)
clean.save(OUT / 'environment.png')
clean.save(OUT / 'environment.webp', lossless=True)
k = source.width / 1400
patch = source.crop(tuple(round(v*k) for v in (1037,552,1076,620)))
patch.resize((80,136),Image.Resampling.LANCZOS).save(OUT / 'road.webp',quality=94)
mask.save(OUT / 'environment-repair-mask.png')
# Raster silhouettes follow the actual inked roof/facade edges, not road-cutting
# runtime polygons. The city courtyard/path is deliberately not in this mask.
architecture = [
    [(356,80),(612,99),(613,133),(630,135),(631,164),(628,263),(620,333),(601,332),(592,380),(335,361),(331,264)],
    [(761,70),(868,76),(869,241),(861,399),(841,404),(740,399),(738,250)],
    [(868,106),(955,113),(951,260),(860,255)],
    [(954,98),(1053,104),(1058,249),(1034,431),(932,422),(932,295)],
    [(743,397),(1028,412),(1030,477),(1021,525),(739,506),(734,463)],
    [(729,624),(995,646),(996,722),(988,790),(971,790),(971,797),(934,794),
     (934,791),(848,785),(848,790),(837,790),(837,781),(722,775),(721,710),(718,710)],
]
foreground_mask = Image.new('L',source.size)
fg = ImageDraw.Draw(foreground_mask)
for polygon in architecture:
    fg.polygon([(round(x*factor),round(y*factor)) for x,y in polygon],fill=255)
foreground = clean.convert('RGBA'); foreground.putalpha(foreground_mask)
foreground.save(OUT / 'foreground.webp',lossless=True)
foreground_mask.save(OUT / 'foreground-mask.png')
# Approved manual outcome identities are reused, not regenerated.
for name in ['old','old4','near','crew']:
    for fmt in ['desktop','mobile']:
        Image.open(SOURCE / f'{name}-{fmt}.png').save(OUT / f'{name}-{fmt}.webp',quality=95)
express = Image.open(SOURCE / 'express-desktop.png').convert('RGB')
mask = Image.new('L',express.size); d = ImageDraw.Draw(mask)
k = express.width/1200
d.polygon([(int(x*k),int(y*k)) for x,y in [(750,210),(925,255),(925,350),(750,325)]],fill=255)
repaired = cv2.inpaint(np.array(express),np.array(mask),12,cv2.INPAINT_NS)
express = Image.composite(Image.fromarray(repaired),express,mask)
express.save(OUT / 'express-desktop.webp',quality=95)
left = (express.width-2057)//2
express.crop((left,0,left+2057,express.height)).save(OUT / 'express-mobile.webp',quality=95)
mask.save(OUT / 'wordmark-removal-mask.png')
(OUT / 'provenance.json').write_text(json.dumps({
    'source': str(SOURCE.relative_to(ROOT)),
    'runtime': '2.5D: preserved illustrated architecture, warehouse-only warm palette, local clean plate, rendered 3D heading atlas',
    'warehousePalette': {'facade': facade, 'belt': belt, 'preserved': 'six gates, seven bay lines, windows, sign lettering and facade geometry'},
    'sourceMapSHA256': hashlib.sha256((SOURCE/'map.png').read_bytes()).hexdigest(),
    'repairs': polygons + [shadow],
    'cleanPlate': str(clean_source),
    'registrationCorrelation': correlation,
    'outsideRepairMaskChangedPixels': 0,
    'preservedReviews': True,
    'wordmark': 'local trailer panel repair only; all cab/crew/background pixels unchanged before WebP encoding',
    'oldOutcome': 'Approved pass18 intentionally uses the same DPS composition for old and old4',
},indent=2)+'\n')
print('Built scene1 clean plate and ten outcome files; prior reviews untouched.')
