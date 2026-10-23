from pathlib import Path
from PIL import Image,ImageDraw
import json,sys
p=Path(__file__).resolve().parent
for name in sys.argv[1:]:
 q=p/name;r=json.loads((q/'receipt.json').read_text());rows=[]
 for f in range(0,121,6):
  im=Image.open(q/'source'/f'{f+1:04}.png').convert('RGB');layer=Image.open(q/'layers'/f'{f:04}.png');a=layer.getchannel('A');b=a.getbbox();b=(max(0,b[0]-8),max(0,b[1]-8),min(1280,b[2]+8),min(720,b[3]+8));w=b[2]-b[0];h=b[3]-b[1];row=Image.new('RGB',(640,h+24),'white');d=ImageDraw.Draw(row)
  check=Image.new('RGB',im.size)
  for y in range(b[1],b[3],12):
   for x in range(b[0],b[2],12):ImageDraw.Draw(check).rectangle((x,y,x+11,y+11),fill=(224,230,233) if ((x-b[0])//12+(y-b[1])//12)%2 else (166,177,184))
  check.paste(im,(0,0),a)
  for c,(kind,image) in enumerate([('source',im),('checker',check)]):row.paste(image.crop(b),(c*320,24));d.text((c*320+3,3),f'{name} {kind} {f/24:.2f}s /f{f}',fill='black')
  rows.append(row)
 for g in range(3):
  subset=rows[g*7:(g+1)*7];sheet=Image.new('RGB',(640,sum(x.height for x in subset)),'white');y=0
  for row in subset:sheet.paste(row,(0,y));y+=row.height
  sheet.save(q/f'compact-contact-{g+1}.png')
