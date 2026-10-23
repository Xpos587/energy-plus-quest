from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
P=Path(__file__).resolve().parent
B=P.parent/'four-truck-loop-2026-10-04/v2b-empty-map.png'
bg=Image.open(B).convert('RGBA');patch=Image.open(P/'backdrop/warehouse-after.png').convert('RGBA').resize((305,310),Image.Resampling.LANCZOS)
mask=Image.new('L',bg.size);d=ImageDraw.Draw(mask)
d.polygon([(158,170),(419,178),(421,398),(381,431),(183,423),(150,310)],fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(4));replacement=bg.copy();replacement.paste(patch,(135,145));bg=Image.composite(replacement,bg,mask)
# Local repaired apron only: no whole-map generative re-layout.
apron=Image.open(P/'backdrop/apron-after.png').convert('RGBA').resize((305,480),Image.Resampling.LANCZOS)
road=bg.copy();road.paste(apron,(135,145));apron_mask=Image.new('L',bg.size)
ImageDraw.Draw(apron_mask).rectangle((180,378,370,595),fill=255)
bg=Image.composite(road,bg,apron_mask.filter(ImageFilter.GaussianBlur(4)))
bg.convert('RGB').save(P/'backdrop/city-v06.png')
for f in [1,385,769]:
 fp=P/f'fleet/textured-v06-vehicles-{f:04}.png'
 if not fp.exists():continue
 fg=Image.open(fp).convert('RGBA');canvas=bg.resize(fg.size,Image.Resampling.LANCZOS);canvas.alpha_composite(fg);canvas.convert('RGB').save(P/f'map-{f:04}.png')
print('Whole-map candidate stills written')
