from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,cv2,json
P=Path(__file__).resolve().parent;D=P.parent
# All hand annotations are in the 450x245 crop coordinate plane.
def polygon_mask(size,polygons,lines=(),ellipses=()):
 m=Image.new('L',(450,245));d=ImageDraw.Draw(m)
 for p in polygons:d.polygon(p,fill=255)
 for a,b,w in lines:d.line([a,b],fill=255,width=w)
 for e in ellipses:d.ellipse(e,fill=255)
 return m.resize(size,Image.Resampling.LANCZOS)
newpolys=[[(107,148),(110,137),(116,129),(124,121),(136,115),(143,108),(145,100),(153,95),(168,91),(178,86),(180,79),(190,77),(198,84),(214,88),(230,98),(231,112),(224,129),(213,139),(192,147),(160,153),(144,156),(126,157),(113,154)],[(211,87),(239,80),(266,74),(292,62),(301,49),(306,51),(301,66),(295,75),(268,86),(226,101)]]
newlines=[((185,78),(84,63),3),((185,78),(173,39),5),((185,78),(281,61),4),((185,78),(278,120),4),((185,78),(76,111),4),((308,50),(286,32),4),((308,50),(321,32),4),((308,50),(321,72),4),((214,136),(211,145),3),((142,151),(142,160),3)]
ref=Image.open(D/'choice-wide-refined.png').convert('RGB');a=polygon_mask(ref.size,newpolys,newlines,[(206,138,219,152),(136,153,147,165)])
# The mask has no pad/background; preserve anti-aliased subject edge only.
a.save(P/'common-wide-aircraft-alpha-native.png');rgba=ref.copy();rgba.putalpha(a);rgba.save(P/'common-wide-aircraft-native.png')
r=json.loads((D/'choices/registration.json').read_text());M=np.array(r['refinedToTarget']['matrix'],dtype=float)
# authoritative target1859x1012 maps to source crop450x245.
S=np.array([[450/1859,0,0],[0,245/1012,0],[0,0,1.]])@np.vstack([M,[0,0,1]])
rgb=cv2.warpAffine(np.array(ref),S[:2],(450,245),flags=cv2.INTER_LANCZOS4);alpha=cv2.warpAffine(np.array(a),S[:2],(450,245),flags=cv2.INTER_LINEAR)
Image.fromarray(rgb).save(P/'common-wide-aircraft-aligned-rgb.png');Image.fromarray(alpha).save(P/'common-wide-aircraft-aligned-alpha.png')
oldpolys=[[(131,151),(134,130),(144,112),(157,101),(172,94),(181,84),(197,81),(210,84),(231,81),(242,88),(240,109),(234,128),(240,132),(237,141),(230,140),(227,136),(185,158),(181,169),(172,171),(168,165),(168,160),(149,159)],[(225,81),(270,62),(283,40),(286,29),(294,26),(290,58),(304,55),(305,62),(285,64),(238,96)]]
oldlines=[((80,110),(269,40),10),((110,57),(294,103),10),((274,33),(307,55),9),((291,25),(282,60),8)]
remove=polygon_mask((450,245),oldpolys,oldlines)
# Include the original shadow only; existing visible pad/H is untouched outside this local mask.
d=ImageDraw.Draw(remove);d.polygon([(134,153),(171,142),(211,132),(257,114),(295,113),(300,122),(273,141),(244,152),(212,164),(177,176),(143,168)],fill=255)
remove=remove.filter(ImageFilter.MaxFilter(3));remove.save(P/'common-wide-old-aircraft-removal-mask.png')
orig=Image.open(P/'F0093-original.png').convert('RGB');crop=orig.crop((850,15,1300,260));clean=cv2.inpaint(np.array(crop),np.array(remove),6,cv2.INPAINT_TELEA)
# Restore concealed H continuation only within the removed old-subject area.
h=polygon_mask((450,245),[[(161,75),(179,81),(129,136),(111,130)],[(265,106),(283,112),(232,169),(214,163)],[(140,102),(158,108),(254,139),(236,145)]])
sel=(np.array(h)>127)&(np.array(remove)>0);clean[sel]=[235,239,245]
Image.fromarray(clean).save(P/'common-wide-cleanplate.png')
result=Image.composite(Image.fromarray(rgb),Image.fromarray(clean),Image.fromarray(alpha));out=orig.copy();out.paste(result,(850,15));out.save(P/'F0093-helicopter-corrected-v2.png');result.save(P/'detail-review-v2-100pct.png');result.resize((900,490),Image.Resampling.NEAREST).save(P/'detail-review-v2-2x.png')
(P/'common-wide-transform.json').write_text(json.dumps({'refinedToSourceCrop':S[:2].tolist(),'sourceBox':[850,15,1300,260],'method':'aircraft-only alpha; old-aircraft-only inpaint; hidden H continuation, visible original pad untouched'},indent=2))
