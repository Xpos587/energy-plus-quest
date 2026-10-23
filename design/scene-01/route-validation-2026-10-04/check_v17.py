"""Explicit visible-obstacle check of proposed R80 corridor against V17."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from shapely.geometry import shape,box,mapping
from shapely.ops import unary_union
P=Path(__file__).resolve().parent
src=P.parent/'animation-pilot-2026-10-04/map-v17-road-candidate.png'
g=shape(json.loads((P/'proposed-road.geojson').read_text())['features'][0]['geometry'])
# Conservative rectangles INSIDE unmistakable non-road; deliberately omit ambiguous curved curbs.
obs=[('A: upper block north',830,0,1048,112),('B1: left tower roof',815,157,873,279),('B2: right tower roof',952,157,1032,309),('B3: connector roof',879,175,944,224),('C: upper west sidewalk',792,285,805,457),('D: lower inner corner',805,583,1029,674),('E: narrow passage east curb',783,612,800,656),('F: lower south building',814,778,1013,990)]
img=Image.open(src).convert('RGBA');ov=Image.new('RGBA',img.size);d=ImageDraw.Draw(ov)
for poly in [g]:
 d.polygon(list(poly.exterior.coords),fill=(0,180,80,65))
 for h in poly.interiors:d.polygon(list(h.coords),fill=(0,0,0,0))
results=[]
for name,x0,y0,x1,y1 in obs:
 cut=g.intersection(box(x0,y0,x1,y1)); results.append({'obstacle':name,'recorded_nonroad_box':[x0,y0,x1,y1],'corridor_overlap_bounds':list(cut.bounds) if not cut.is_empty else None,'corridor_overlap_area_px2':round(cut.area,2)})
 if cut.is_empty:continue
 polys=[cut] if cut.geom_type=='Polygon' else cut.geoms
 for q in polys:d.polygon(list(q.exterior.coords),fill=(245,20,30,170))
 d.text((x0+4,y0+10),name,fill=(130,0,0,255))
d.rectangle((10,873,402,974),fill=(255,255,255,240))
for i,t in enumerate(['V17 does not fit the R80 / 180px proposal','Red: corridor overlaps definite non-road','Green: proposed swept road +6px margin','Curved curbs omitted: these are LOWER BOUNDS']):d.text((20,889+22*i),t,fill=(110,0,0,255))
Image.alpha_composite(img,ov).convert('RGB').save(P/'v17-explicit-obstructions.png')
(P/'v17-obstructions.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
