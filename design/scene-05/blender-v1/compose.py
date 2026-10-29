"""Deterministic finishing of the reference-guided Blender illustration."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, cv2
import sys
r=Path(sys.argv[1])
for fmt in ['wide','tall']:
 base=Image.open(r/f'fixed-{fmt}.png').convert('RGBA')
 if fmt=='wide':
  # Remove the generated six-axle mistake before placing the reference-correct truck.
  m=Image.new('L',base.size); d=ImageDraw.Draw(m)
  d.polygon([(621,438),(650,416),(787,447),(810,458),(843,493),(849,527),(813,548),(771,553),(681,526),(635,512),(617,488)],fill=255)
  m=m.filter(ImageFilter.MaxFilter(9))
  clean=cv2.inpaint(np.array(base.convert('RGB')),np.array(m),7,cv2.INPAINT_TELEA)
  base=Image.fromarray(clean).convert('RGBA')
  truck=Image.open(r/'sprite-truck.png').convert('RGBA').resize((224,143),Image.Resampling.LANCZOS)
  shadow=Image.new('RGBA',base.size);ImageDraw.Draw(shadow).ellipse((633,477,850,550),fill=(45,49,44,65));base=Image.alpha_composite(base,shadow.filter(ImageFilter.GaussianBlur(5)))
  base.alpha_composite(truck,(624,408))
 base.convert('RGB').save(r/f'base-{fmt}.png')
 for who in ['alva','khor','arseniy']:
  im=base.copy(); person=Image.open(r/f'sprite-{who}.png').convert('RGBA')
  # Drop disconnected segmentation specks; keep the person's full silhouette.
  alpha=np.array(person.getchannel('A')); n,labels,stats,_=cv2.connectedComponentsWithStats((alpha>127).astype('uint8'))
  keep=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA])); person.putalpha(Image.fromarray(np.where(labels==keep,alpha,0).astype('uint8')))
  person=person.crop(person.getbbox())
  h=92 if fmt=='wide' else 116
  person=person.resize((round(person.width*h/person.height),h),Image.Resampling.LANCZOS)
  # Stand on the destination bank, separate from the tent/building silhouette.
  x,y=({'arseniy':(1348,304),'alva':(1390,510),'khor':(1390,510)} if fmt=='wide' else {'arseniy':(533,675),'alva':(842,818),'khor':(842,818)})[who]
  shadow=Image.new('RGBA',im.size);ImageDraw.Draw(shadow).ellipse((x-person.width*.45,y-5,x+person.width*.45,y+8),fill=(34,38,30,75))
  im=Image.alpha_composite(im,shadow.filter(ImageFilter.GaussianBlur(3)))
  im.alpha_composite(person,(round(x-person.width/2),y-h))
  im.convert('RGB').save(r/f'final-{fmt}-{who}.png')
