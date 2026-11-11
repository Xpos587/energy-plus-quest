# /// script
# dependencies = ["pillow", "numpy", "opencv-python-headless"]
# ///
"""Finish v14 warehouse PPE using aligned v12 garment pixels and the actual result keeper.
Run from checkout: uv run scripts/finish-warehouse-v15.py
No image API: local, repeatable edits; source plates/results are never overwritten.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path('public/scene-art')
OUT = Path('.tmp-work/r22-warehouse')
OUT.mkdir(parents=True, exist_ok=True)
BOXES = {
 'wide': [(285,365,405,545),(355,440,475,620),(1200,440,1320,620),(1280,550,1400,730),(1350,650,1470,830)],
 'tall': [(230,640,350,820),(280,730,400,910),(810,730,930,910),(860,870,980,1050),(920,1010,1040,1190)],
}
# Local native coordinates: complete person bounds, shoulder/chest panel, upper thighs.
PARTS = {
 'wide': [
  ([(38,31),(62,31),(64,50),(71,53),(79,75),(75,89),(78,122),(65,127),(52,129),(47,113),(44,95),(39,90),(38,65)], [(41,60),(52,52),(62,52),(69,56),(73,66),(66,69),(48,73),(43,70)], [(48,94),(60,97),(72,94),(74,106),(65,110),(61,108),(52,110)]),
  ([(36,30),(64,30),(70,51),(76,66),(82,87),(79,105),(81,128),(71,139),(52,139),(51,125),(55,97),(38,94),(32,85),(30,69),(38,61)], [(50,58),(60,52),(67,54),(71,61),(73,67),(57,76),(51,69)], [(57,93),(77,91),(79,106),(70,109),(62,112),(56,109)]),
  ([(36,32),(75,32),(79,45),(68,56),(76,65),(90,69),(90,81),(70,82),(64,96),(62,120),(64,134),(49,138),(34,131),(35,118),(38,94),(40,72)], [(45,61),(54,55),(63,58),(67,66),(59,78),(44,73)], [(40,98),(60,100),(60,111),(53,115),(39,111)]),
  ([(36,61),(56,50),(77,50),(87,62),(88,85),(80,96),(78,130),(66,133),(58,128),(46,130),(42,121),(47,96),(39,83),(32,76)], [(48,62),(58,55),(64,63),(73,56),(81,62),(82,73),(66,72),(59,73),(48,71)], [(48,99),(76,100),(75,111),(64,114),(60,111),(49,112)]),
  ([(34,35),(79,35),(84,59),(88,70),(88,86),(82,102),(80,127),(75,146),(65,150),(56,145),(47,151),(36,145),(42,131),(46,106),(43,100),(34,100),(31,91),(46,83),(52,77),(35,73),(28,64)], [(54,70),(67,63),(78,65),(83,69),(84,78),(74,84),(57,84)], [(49,108),(77,109),(74,121),(64,125),(54,122),(48,122)]),
 ],
 'tall': [
  ([(34,55),(56,55),(57,72),(65,75),(69,91),(63,99),(65,118),(67,135),(57,139),(50,135),(43,138),(34,132),(34,114),(30,99),(24,93),(25,80)], [(29,81),(40,74),(50,74),(60,78),(63,84),(55,88),(34,91),(28,88)], [(34,100),(59,100),(61,113),(53,116),(47,111),(37,114)]),
  ([(25,35),(47,35),(50,48),(56,53),(60,67),(60,87),(60,99),(65,117),(59,126),(48,125),(45,119),(37,121),(29,119),(32,104),(33,88),(20,86),(18,77),(22,67),(35,59)], [(43,52),(51,54),(56,62),(57,70),(50,76),(43,70),(38,64)], [(36,90),(58,89),(59,102),(53,108),(47,104),(40,106),(35,102)]),
  ([(51,33),(72,33),(75,46),(67,52),(73,58),(76,73),(68,79),(55,80),(52,102),(50,114),(45,116),(44,122),(33,122),(35,105),(38,91),(37,69),(39,55)], [(45,53),(55,46),(60,51),(60,59),(53,70),(43,66)], [(38,84),(52,85),(51,98),(44,102),(38,98)]),
  ([(38,60),(62,56),(78,57),(86,68),(87,86),(81,96),(73,104),(74,127),(69,141),(59,142),(58,131),(45,129),(43,120),(48,98),(38,85),(30,75)], [(48,67),(61,59),(65,67),(75,62),(82,69),(83,79),(69,77),(61,76),(52,73)], [(48,98),(72,99),(73,109),(65,115),(60,111),(50,112)]),
  ([(42,39),(68,39),(71,55),(75,61),(78,70),(75,89),(70,101),(67,130),(64,140),(54,144),(45,140),(38,137),(42,123),(41,104),(39,97),(34,92),(35,86),(43,80),(47,66)], [(50,67),(62,60),(69,62),(74,67),(74,74),(65,81),(50,84),(46,78)], [(42,99),(68,101),(66,115),(57,119),(46,114),(42,112)]),
 ]
}

def mask(size, points):
    m=Image.new('L',(size[0]*4,size[1]*4))
    ImageDraw.Draw(m).polygon([(x*4,y*4) for x,y in points],fill=255)
    return np.asarray(m.resize(size,Image.Resampling.LANCZOS),dtype=float)/255


def repaint(crop, parts, boot_y):
    a=np.asarray(crop).copy(); hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV).astype(float)
    body=mask(crop.size,parts[0]); navy=(hsv[:,:,0]>94)&(hsv[:,:,0]<137)&(hsv[:,:,1]>80)&(hsv[:,:,2]>35)
    navy[boot_y:]=False  # Dark boots are not blue fabric; floor tint is below the saturation cutoff.
    blue=hsv.copy(); blue[:,:,0]=110; blue[:,:,1]=np.maximum(blue[:,:,1],175); blue[:,:,2]=np.clip(blue[:,:,2]*1.12+4,0,205)
    orange=blue.copy();orange[:,:,0]=14;orange[:,:,1]=225;orange[:,:,2]=np.clip(hsv[:,:,2]*1.55+45,90,248)
    panel=np.maximum(mask(crop.size,parts[1]),mask(crop.size,parts[2]))
    b=cv2.cvtColor(blue.astype('uint8'),cv2.COLOR_HSV2RGB).astype(float)
    o=cv2.cvtColor(orange.astype('uint8'),cv2.COLOR_HSV2RGB).astype(float)
    paint=b*(1-panel[:,:,None])+o*panel[:,:,None]
    alpha=(body*navy)[:,:,None]
    return Image.fromarray(np.uint8(a*(1-alpha)+paint*alpha))


def keeper_head(image, form):
    ref=Image.open(ROOT/'warehouse-results-v2/outcome-keeper.webp').convert('RGB')
    bounds=(457,173,573,309)
    points=[(41,0),(64,2),(87,12),(103,29),(114,51),(116,70),(108,90),(98,99),(86,113),(78,132),(55,136),(33,129),(21,116),(13,91),(13,76),(19,59),(27,39),(4,30),(0,20),(9,15),(27,15)]
    head=ref.crop(bounds).convert('RGBA')
    head.putalpha(Image.fromarray(np.uint8(mask(head.size,points)*255)))
    target=(1332,580,1358,611) if form=='wide' else (919,910,941,937)
    # Remove old head only; the surrounding floor and clipboard stay in place.
    arr=np.asarray(image).copy(); hole=np.zeros(arr.shape[:2],np.uint8)
    x0,y0,x1,y1=target;cv2.ellipse(hole,((x0+x1)//2,(y0+y1)//2),((x1-x0)//2,(y1-y0)//2),0,0,360,255,-1)
    arr=cv2.inpaint(arr,hole,3,cv2.INPAINT_TELEA)
    out=Image.fromarray(arr); patch=head.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS);out.paste(patch,(x0,y0),patch)
    return out


def main():
    for form,boxes in BOXES.items():
        suffix='-tall' if form=='tall' else ''
        base=Image.open(ROOT/f'inventory-master-v14{suffix}.webp').convert('RGB')
        original=Image.open(ROOT/f'inventory-master-v12{suffix}.webp').convert('RGB')
        # Restore all overlapping crops BEFORE repainting: a later crop must not erase its neighbour.
        for box in boxes:
            base.paste(original.crop(box),box[:2])
        boots=[118,128,127,126,140] if form=='wide' else [127,117,112,128,134]
        for box,parts,boot_y in zip(boxes,PARTS[form],boots):
            base.paste(repaint(base.crop(box),parts,boot_y),box[:2])
        base=keeper_head(base,form)
        base.save(OUT/f'{form}-v15.png')
        base.save(ROOT/f'inventory-master-v15{suffix}.webp',quality=98,method=6)
        assert base.size == original.size
        # Guard geometry: every pixel outside the explicitly edited rectangles is untouched.
        m=Image.new('1',base.size);d=ImageDraw.Draw(m)
        for b in boxes:d.rectangle(b,fill=1)
        a=np.asarray(base);b=np.asarray(Image.open(ROOT/f'inventory-master-v14{suffix}.webp').convert('RGB'))
        assert np.array_equal(a[~np.asarray(m)],b[~np.asarray(m)])
    sheet=Image.new('RGB',(1800,1080),'white')
    for row,form in enumerate(BOXES):
        im=Image.open(OUT/f'{form}-v15.png')
        for col,box in enumerate(BOXES[form]):sheet.paste(im.crop(box).resize((360,540)),(col*360,row*540))
    sheet.save(OUT/'people-after.png')
    print('v15 plates written; exact outside-rectangle geometry check passed')

if __name__=='__main__':main()
