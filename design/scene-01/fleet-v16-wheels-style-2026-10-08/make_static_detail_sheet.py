from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
names=[('Red tractor102','final-truck1-front-f0102.png'),('Red tractor103','final-truck1-front-f0103.png'),('Red tractor104','final-truck1-front-f0104.png'),('Trailer axle130','style-trailer3-axle-0130.png'),('Trailer axle131','style-trailer3-axle-0131.png'),('Green shared paint','style-trailer3-map-0130.png')]
out=Image.new('RGB',(1800,860),'#eceee9');d=ImageDraw.Draw(out)
for j,(label,name) in enumerate(names):
 im=Image.open(P/name).convert('RGBA');im.thumbnail((600,400),Image.Resampling.LANCZOS);x=j%3*600;y=j//3*430;out.paste(im,(x+(600-im.width)//2,y+30),im);d.text((x+12,y+8),label,fill='black')
out.save(P/'static-wheel-paint-detail-sheet.png')
