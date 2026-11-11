# /// script
# dependencies = ["pillow", "numpy", "opencv-python-headless"]
# ///
"""Keep the choice scene's red gift/white ribbon in all warehouse results.
Run: uv run scripts/finish-warehouse-gifts.py
Local face recolour preserves the original illustration, cargo and composition.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path('public/scene-art')
OUT=ROOT/'warehouse-results-v3'
REVIEW=Path('.tmp-work/r22-warehouse')
# Each face is ordered TL, TR, BR, BL. Only one hero gift; ordinary cargo stays kraft.
QUADS={
 'entrance': {
  'top':[(836,506),(949,496),(1087,507),(977,517)],
  'front':[(836,506),(977,517),(977,635),(836,626)],
  'side':[(977,517),(1087,507),(1087,621),(977,635)]},
 'alphabet': {
  'top':[(884,515),(1006,499),(1158,509),(1034,523)],
  'front':[(884,515),(1034,523),(1035,629),(884,629)],
  'side':[(1034,523),(1158,509),(1163,615),(1035,629)]},
 'wms': {
  'top':[(679,523),(749,516),(935,518),(878,535)],
  'front':[(679,523),(878,535),(878,733),(679,717)],
  'side':[(878,535),(935,518),(935,725),(878,733)]},
}


def face_mask(size,quads):
 m=Image.new('L',size);d=ImageDraw.Draw(m)
 for q in quads:d.polygon(q,fill=255)
 return m


def warp_patch(canvas, patch, quad):
 src=np.float32([(0,0),(patch.width-1,0),(patch.width-1,patch.height-1),(0,patch.height-1)])
 h=cv2.getPerspectiveTransform(src,np.float32(quad))
 warped=cv2.warpPerspective(np.asarray(patch),h,canvas.size,flags=cv2.INTER_CUBIC)
 canvas.alpha_composite(Image.fromarray(warped))


def ribbon(face):
 p=Image.new('RGBA',(800,800));d=ImageDraw.Draw(p)
 # A broad white ribbon crosses the top, then wraps down both visible faces.
 colour='#f8f6ef' if face=='top' else '#eeeae2' if face=='front' else '#d5d6d7'
 d.rectangle((354,0,451,800),fill=colour)
 d.line((356,0,356,800),fill='#c6c9cb',width=5)
 d.line((447,0,447,800),fill='#ffffff',width=4)
 if face=='top':
  d.rectangle((0,350,800,448),fill=colour)
  d.line((0,445,800,445),fill='#c6c9cb',width=5)
 return p

def bow(quads):
 p=Image.new('RGBA',(240,110));d=ImageDraw.Draw(p)
 for b in [(8,9,119,72),(121,9,232,72)]:
  d.ellipse(b,fill='#faf9f3',outline='#9da7af',width=4)
 d.line([(21,43),(109,59),(126,59),(218,43)],fill='#c7cbcc',width=3)
 d.polygon([(110,50),(64,105),(99,94),(117,106),(139,55)],fill='#eeeae2')
 d.polygon([(128,50),(178,102),(146,91),(129,107),(107,55)],fill='#f9f7f1')
 d.ellipse((101,39,140,76),fill='#efeee6',outline='#9da7af',width=3)
 top=np.asarray(quads['top']);width=round(np.ptp(top[:,0])*.30)
 patch=p.resize((width,round(width*110/240)),Image.Resampling.LANCZOS)
 center=top.mean(axis=0).astype(int)
 return patch,(int(center[0]-patch.width/2),int(center[1]-patch.height*.65))


def gift_mask(size,quads):
 m=face_mask(size,quads.values());patch,pos=bow(quads)
 # Keep the exact silhouette, including the raised bow, when reusing this parcel.
 layer=Image.new('L',size);layer.paste(patch.getchannel('A'),pos)
 return Image.fromarray(np.maximum(np.asarray(m),np.asarray(layer)))


def wrap(image,quads):
 arr=np.asarray(image).copy();hsv=cv2.cvtColor(arr,cv2.COLOR_RGB2HSV)
 m=(np.asarray(face_mask(image.size,quads.values()))>0)&(hsv[:,:,1]>45)&(hsv[:,:,0]<35)
 red=hsv.copy();red[:,:,0]=1;red[:,:,1]=np.maximum(red[:,:,1],195)
 red[:,:,2]=np.clip(red[:,:,2].astype(float)*1.04,0,245).astype('uint8')
 rgb=cv2.cvtColor(red,cv2.COLOR_HSV2RGB);arr[m]=rgb[m]
 out=Image.fromarray(arr).convert('RGBA')
 for name,q in quads.items():warp_patch(out,ribbon(name),q)
 patch,pos=bow(quads);out.alpha_composite(patch,pos)
 return out.convert('RGB')


def main():
 OUT.mkdir(exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
 for path in sorted((ROOT/'warehouse-results-v2').glob('outcome-*.webp')):
  branch=path.stem.removeprefix('outcome-').split('-')[0]
  if branch=='keeper':continue
  image=Image.open(path).convert('RGB');result=wrap(image,QUADS[branch])
  result.save(OUT/path.name,quality=98,method=6)
  result.save(REVIEW/f'{path.stem}-gift.png')
  allowed=np.asarray(gift_mask(image.size,QUADS[branch]).filter(ImageFilter.MaxFilter(5)))>0
  assert np.array_equal(np.asarray(image)[~allowed],np.asarray(result)[~allowed])
 # Keeper's result originally has an empty cart. Add the SAME wrapped parcel, not another design.
 keeper=Image.open(ROOT/'warehouse-results-v2/outcome-keeper.webp').convert('RGBA')
 source=Image.open(REVIEW/'outcome-wms-gift.png').convert('RGBA')
 source.putalpha(gift_mask(source.size,QUADS['wms']))
 gift=source.crop((678,500,937,735)).resize((190,172),Image.Resampling.LANCZOS)
 shadow=Image.new('RGBA',keeper.size);d=ImageDraw.Draw(shadow)
 d.ellipse((1058,728,1261,751),fill=(15,38,64,85));shadow=shadow.filter(ImageFilter.GaussianBlur(5))
 keeper.alpha_composite(shadow);keeper.alpha_composite(gift,(1062,574))
 keeper.convert('RGB').save(OUT/'outcome-keeper.webp',quality=98,method=6)
 keeper.convert('RGB').save(REVIEW/'outcome-keeper-gift.png')
 names=['entrance','alphabet-boat','alphabet-camera','alphabet-socks','wms','keeper']
 sheet=Image.new('RGB',(1800,720),'white')
 for i,name in enumerate(names):
  im=Image.open(OUT/f'outcome-{name}.webp');im.thumbnail((600,360))
  sheet.paste(im,((i%3)*600,(i//3)*360))
 sheet.save(REVIEW/'results-gifts-v3.jpg',quality=95)
 print('Six red-gift outcomes written; outside-face pixel checks passed for the five recolours.')

if __name__=='__main__':main()
