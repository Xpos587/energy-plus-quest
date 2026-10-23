from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',P.parent/'fleet-behavior-v16-2026-10-07/composite_motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.P=P
out=Image.new('RGB',(1920,1390),'#f1f1ed');d=ImageDraw.Draw(out)
for j,f in enumerate([102,130,192,144]):
 im=m.compose(f);im.save(P/f'map-{f:04}.png');small=im.resize((960,667),Image.Resampling.LANCZOS);small.save(P/f'map-display-{f:04}.png');x=(j%2)*960;y=(j//2)*695;out.paste(small,(x,y+28));d.text((x+12,y+7),f'Source frame {f}',fill='black')
out.save(P/'static-map-contact-sheet.png')
