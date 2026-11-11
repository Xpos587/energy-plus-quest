# /// script
# dependencies = ["pillow", "numpy", "opencv-python-headless"]
# ///
"""Prepare registered people-only PPE targets; never modify runtime media."""
import importlib.util
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.tmp-work/r23-warehouse-ppe'
OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('v15',ROOT/'scripts/finish-warehouse-v15.py')
v15=importlib.util.module_from_spec(spec);spec.loader.exec_module(v15)
SCALE=4
CELL=(480,720)
sheet=Image.new('RGB',(CELL[0]*5,CELL[1]*2),(224,227,231))
records=[]
for row,(form,boxes) in enumerate(v15.BOXES.items()):
    suffix='-tall' if form=='tall' else ''
    base=Image.open(ROOT/f'public/scene-art/inventory-master-v15{suffix}.webp').convert('RGB')
    for col,(box,parts) in enumerate(zip(boxes,v15.PARTS[form])):
        crop=base.crop(box)
        mask=Image.fromarray(np.uint8(v15.mask(crop.size,parts[0])*255))
        # The keeper head was changed after the old garment polygons were authored.
        if col==3:
            d=ImageDraw.Draw(mask)
            d.ellipse((46,26,82,66) if form=='wide' else (54,36,85,72),fill=255)
        neutral=Image.new('RGB',crop.size,(224,227,231));neutral.paste(crop,(0,0),mask)
        sheet.paste(neutral.resize(CELL,Image.Resampling.LANCZOS),(col*CELL[0],row*CELL[1]))
        mask.save(OUT/f'{form}-{col}-mask.png')
        records.append({'form':form,'col':col,'row':row,'box':box})
sheet.save(OUT/'people-target.png')
(OUT/'registration.json').write_text(json.dumps({'cell':CELL,'records':records},indent=2))
# Reference is actual runtime result, cropped to the garment and body, not old styling boards.
Image.open(ROOT/'public/scene-art/warehouse-results-v3/outcome-keeper.webp').crop((204,171,704,898)).save(OUT/'result-clothing-reference.png')
assert sheet.size==(2400,1440)
print('Prepared ten people, registration and clothing reference; runtime files unchanged')
