"""Compose the four isolated r30 edit targets and illustrated/photo reference sheets."""
from pathlib import Path
import numpy as np
from PIL import Image

work=Path('.tmp-work/scene5-r31/paint'); work.mkdir(parents=True,exist_ok=True)
family=Path('public/scene-art/lastmile-family-v1')
plate=Image.open(family/'revision-30/choice-wide.webp').convert('RGBA')
masks=np.load('.tmp-work/scene5-r30/paint/wide-masks.npz')

def sheet(images,name,bg='white'):
    out=Image.new('RGB',(1440,960),bg)
    for i,im in enumerate(images):
        im=im.convert('RGBA'); im=im.resize((round(im.width*min(640/im.width,410/im.height)),round(im.height*min(640/im.width,410/im.height))),Image.Resampling.LANCZOS)
        out.paste(im,(i%2*720+(720-im.width)//2,i//2*480+(480-im.height)//2),im)
    out.save(work/name)

items=[]
for k in ('helicopter','rover','pipe_carrier'):
    im=plate.copy(); im.putalpha(Image.fromarray(masks[k]*255));items.append(im.crop(im.getbbox()))
items.append(Image.open('public/scene-art/barge-v6/desk/gift.webp'));sheet(items,'targets.png','#eb62d5')
sheet([Image.open(family/f).crop(box) for f,box in [ ('revision-22/flight-parcel-tall.webp',(200,450,1310,900)),('revision-19/rover-parcel.webp',(270,185,1290,655)),('revision-21/pipe-carrier-tall.webp',(55,790,1040,1410)),('revision-19/robot-parcel.webp',(345,355,835,580))]],'illustrations.jpg')
sheet([Image.open(f'docs/scenario-assets/{f}') for f in ('image13.png','image14.jpg','image16.jpeg','image15.jpeg')],'vehicles.jpg')
