from PIL import Image,ImageDraw
from pathlib import Path
P=Path(__file__).resolve().parent
# Native source-pixel crops, enlarged2x for inspection; maps remain full native resolution separately.
boxes={48:((1500,470,1610,640),(920,585,1040,760)),96:((1490,260,1640,450),(920,720,1040,900)),144:((1300,160,1530,310),(910,850,1050,1020))}
sheet=Image.new('RGB',(1020,800),'#eeeeee');d=ImageDraw.Draw(sheet)
for c,(f,(red,yellow)) in enumerate(boxes.items()):
 im=Image.open(P/f'map-{f:04}.png')
 for r,(name,b) in enumerate((('red',red),('yellow',yellow))):
  crop=im.crop(b);crop.thumbnail((320,340));crop=crop.resize((min(320,crop.width*2),min(340,crop.height*2)))
  crop.save(P/f'{name}-crop-{f:04}.png');sheet.paste(crop,(c*340,40+r*390));d.text((c*340+8,10+r*390),f'Frame {f} / {name}',fill='black')
sheet.save(P/'smoke-three-times-review.png')
