"""Extract the approved trailer's painted panel texture; no generated vehicle text."""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
root = Path(__file__).resolve().parents[2]
out = Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-22-live')
source = np.array(Image.open(root/'public/review/map-geometry/pass-18/truck-4.png').convert('RGB'))
# Interior of the actual painted side panel, excluding the roof's number and all wheels.
points = np.float32([(160,203),(468,111),(470,172),(169,266)])
transform = cv2.getPerspectiveTransform(points,np.float32([(0,0),(1023,0),(1023,511),(0,511)]))
texture = cv2.warpPerspective(source,transform,(1024,512))
for name, bright in [('old',1.12),('new',1.20)]:
    image = Image.fromarray(np.uint8(np.clip(texture.astype(float)*bright,0,255)))
    if name == 'new':
        image = Image.blend(image,Image.new('RGB',image.size,(242,240,228)),.45)
    draw = ImageDraw.Draw(image)
    draw.rectangle((3,3,1020,508),outline=(67,72,70),width=3)
    draw.line((14,12,1010,12),fill=(255,253,243),width=3)
    image.save(out/f'{name}-trailer-paint.png')
# The roof is a different painted plane, not a stretched copy of the curtain side.
points = np.float32([(105,143),(436,30),(468,86),(137,204)])
transform = cv2.getPerspectiveTransform(points,np.float32([(0,0),(1023,0),(1023,255),(0,255)]))
roof = cv2.warpPerspective(source,transform,(1024,256))
mask = np.zeros((256,1024),np.uint8)
mask[:,370:670] = 255
roof = cv2.inpaint(roof,mask,9,cv2.INPAINT_TELEA)
for name in ['old','new']:
    image = Image.fromarray(roof)
    if name == 'new': image = Image.blend(image,Image.new('RGB',image.size,(244,242,231)),.3)
    image.save(out/f'{name}-roof-trailer-paint.png')
