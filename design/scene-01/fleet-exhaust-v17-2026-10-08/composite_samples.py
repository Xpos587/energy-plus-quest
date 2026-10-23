from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v16composite',P.parent/'fleet-behavior-v16-2026-10-07/composite_motion.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for f in (48,96,144):
 im=m.compose(f,P/f'vehicles-{f:04}.png');im.save(P/f'map-{f:04}.png')
 alpha=Image.open(P/f'vehicles-{f:04}.png').getchannel('A')
 # Full scene rendered at native map size; enlargement is supplementary only.
 im.resize((960,667)).save(P/f'map-display-{f:04}.png')
