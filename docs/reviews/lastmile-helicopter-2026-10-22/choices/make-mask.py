from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
P=Path(__file__).resolve().parent
m=Image.new('L',(1859,1012));d=ImageDraw.Draw(m)
# Tight union of old and corrected fuselage, gear, tail, all rotor strokes and cast shadow, in authoritative target pixels.
d.polygon([(475,570),(505,485),(620,410),(690,365),(760,345),(920,370),(990,410),(1000,525),(950,590),(870,630),(790,665),(715,720),(630,725),(540,685),(470,640)],fill=255)
d.polygon([(800,380),(990,285),(1120,245),(1140,130),(1180,85),(1215,100),(1190,270),(1225,310),(1125,340),(970,400)],fill=255)
for a,b,w in [((780,330),(325,461),36),((780,330),(465,245),32),((780,330),(1095,185),34),((780,330),(1215,440),34),((760,320),(340,265),25),((760,320),(710,155),30),((760,320),(1150,245),26),((760,320),(1150,495),27),((760,320),(310,465),28),((1170,180),(1120,150),30),((1170,180),(1255,235),30),((1245,210),(1190,125),28),((1245,210),(1320,125),28),((1245,210),(1320,300),28)]: d.line([a,b],fill=255,width=w)
# Both existing and replacement shadows must be replaced completely.
d.polygon([(505,620),(615,585),(820,495),(1060,350),(1280,360),(1305,425),(1190,470),(1140,550),(1000,595),(870,650),(700,740),(565,710),(490,680)],fill=255)
m=m.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(1));m.save(P/'aircraft-shadow-union-target-mask.png');m.resize((450,245),Image.Resampling.LANCZOS).save(P/'aircraft-shadow-union-sourcewide-mask.png')
# Fill the visible old/new silhouette envelope to avoid cut nose/tail joins; excludes all cones/windsock/pad border.
d=ImageDraw.Draw(m)
d.polygon([(285,470),(300,420),(580,330),(425,255),(440,215),(680,270),(675,125),(735,125),(790,280),(1055,180),(1090,130),(1150,65),(1245,85),(1375,300),(1295,360),(1315,445),(1190,515),(1030,610),(925,655),(730,745),(455,700),(420,625),(430,535)],fill=255)
m=m.filter(ImageFilter.GaussianBlur(1));m.save(P/'aircraft-shadow-union-target-mask.png');m.resize((450,245),Image.Resampling.LANCZOS).save(P/'aircraft-shadow-union-sourcewide-mask.png')
