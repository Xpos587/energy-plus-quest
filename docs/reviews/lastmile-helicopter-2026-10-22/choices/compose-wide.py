from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,cv2,json
P=Path(__file__).resolve().parent;D=P.parent
r=json.loads((P/'registration.json').read_text());M=np.array(r['refinedToTarget']['matrix']);ref=np.array(Image.open(D/'choice-wide-refined.png').convert('RGB'));target=Image.open(D/'choice-wide-helicopter-target.png');aligned=cv2.warpAffine(ref,M,target.size,flags=cv2.INTER_LANCZOS4);Image.fromarray(aligned).save(P/'refined-aligned-to-wide-target.png')
mask=Image.open(P/'aircraft-shadow-union-target-mask.png').convert('L')
rows=[]
for name in ['alva','khor','arseniy']:
 src=Path('public/scene-art/lastmile-family-v1/revision-4')/f'choice-wide-{name}.webp';original=Image.open(src).convert('RGB')
 if name=='alva':
  base=Image.open('.tmp-work/flowers-all-2026-10-20/F0114/pass2-master.png').convert('RGB');kind='accepted P2 F0114'
 else:
  base=original.resize((5120,round(original.height*5120/original.width)),Image.Resampling.LANCZOS);kind='ordinary Lanczos interpolation from original; not Flowers'
 w,h=base.size;sx=w/8192;sy=h/3276
 # Authoritative patch lives at masterBox[3511,62,5370,1074].
 box=[round(3511*sx),round(62*sy),round(5370*sx),round(1074*sy)];sz=(box[2]-box[0],box[3]-box[1]);patch=Image.fromarray(aligned).resize(sz,Image.Resampling.LANCZOS);alpha=mask.resize(sz,Image.Resampling.LANCZOS)
 base.paste(patch,tuple(box[:2]),alpha);out=P/f'choice-wide-{name}-helicopter-corrected.png';base.save(out);base.save(out.with_suffix('.webp'),lossless=True,method=4);base.crop((box[0]-20,box[1],box[2]+20,box[3]+20)).save(P/f'choice-wide-{name}-heli-seam-100pct.png');thumb=base.copy();thumb.thumbnail((1983,1000));thumb.save(P/f'choice-wide-{name}-full-review.png');rows.append({'source':str(src),'output':str(out),'dimensions':list(base.size),'basis':kind,'patchBox':box,'preservation':'outside feathered union aircraft+shadow mask retains selected base pixels; original public source untouched'})
(P/'wide-composition-receipt.json').write_text(json.dumps({'backgroundRegistration':r['refinedToTarget'],'mask':'aircraft-shadow-union-target-mask.png','outputs':rows,'limitations':'Three wide only. Tall transfer invalid global similarity; dedicated tall crop edit needed. Interpolation does not recover details.'},indent=2));print(json.dumps(rows,indent=2))
