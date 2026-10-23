"""Proposed green-road reconstruction, derived from full articulated swept envelope."""
import math,json
from pathlib import Path
from PIL import Image,ImageDraw
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent
# Existing validation definitions, without rerunning its output stage.
exec((ROOT/'validate.py').read_text().split('phi=math.pi/2; states=[]')[0])
# Shift the central road 23px east for width. Make top/bottom road centers 140/730.
# 80px radius minimizes the offtracking relative to tight 40px corners.
x0,x1,y0,y1,r=765,1122,140,730,80
p=line((x0,340),(x0,y1-r))+arc((x0+r,y1-r),r,math.pi,math.pi/2)+line((x0+r,y1),(x1-r,y1))+arc((x1-r,y1-r),r,math.pi/2,0)+line((x1,y1-r),(x1,y0+r))+arc((x1-r,y0+r),r,0,-math.pi/2)+line((x1-r,y0),(x0+r,y0))+arc((x0+r,y0+r),r,-math.pi/2,-math.pi)+line((x0,y0+r),(x0,340))
# Run three loops; include all startup and steady-state sweeps. Initial trailer points south.
phi=math.pi/2; states=[]
for lap in range(3):
 for i,(x,y) in enumerate(p):
  nx,ny=p[(i+1)%len(p)]; th=math.atan2(ny-y,nx-x); ds=math.hypot(nx-x,ny-y)
  phi+=ds*math.sin(th-phi)/85
  fp=unary_union([body(x,y,th,70,10,43),body(x,y,phi,0,110,36)])
  states.append((x,y,th,phi,fp))
sweep=unary_union([s[4] for s in states])
# New road surface exactly contains the simulated swept footprint plus 6px clearance.
# Existing rectangles retained; additional road construction supplied as a polygon mask.
required=sweep.buffer(6,quad_segs=8)
newroad=unary_union([road,required]); edit=required.difference(road)
# independent intermediate checks using interpolated full-pose states
violations=0
for a,b in zip(states,states[1:]):
 if math.dist(a[:2],b[:2])>2:continue
 th=a[2]+.5*math.atan2(math.sin(b[2]-a[2]),math.cos(b[2]-a[2])); ph=a[3]+.5*math.atan2(math.sin(b[3]-a[3]),math.cos(b[3]-a[3])); x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
 fp=unary_union([body(x,y,th,70,10,43),body(x,y,ph,0,110,36)])
 violations+=fp.difference(newroad).area>1e-6
img=Image.open(SOURCE).convert('RGBA');overlay=Image.new('RGBA',img.size);d=ImageDraw.Draw(overlay)
def polys(g):return [g] if g.geom_type=='Polygon' else list(g.geoms)
for g in polys(required):
 d.polygon(list(g.exterior.coords),fill=(20,190,90,85))
 for ring in g.interiors:d.polygon(list(ring.coords),fill=(0,0,0,0))
for g in polys(edit):d.polygon(list(g.exterior.coords),fill=(255,125,0,130))
d.line(p+[p[0]],fill=(0,110,40,255),width=3)
for i in [0,330,520,820,1150,1420]:
 for g in polys(states[i][4]):d.line(list(g.exterior.coords),fill=(0,80,30,255),width=2)
d.rectangle((15,865,395,969),fill=(255,255,255,240))
for k,t in enumerate(['PROPOSED ROAD EDIT, not original V16','Green: full swept corridor + 6px margin','Orange: add road beyond conservative mask','180px rig; R80; 3 laps; no static traffic test']):d.text((25,881+22*k),t,fill=(10,60,30))
Image.alpha_composite(img,overlay).convert('RGB').save(ROOT/'proposed-road-edit-guide.png')
# Binary raster mask white = edit required. It inherits manually conservative boundaries.
mask=Image.new('L',img.size);md=ImageDraw.Draw(mask)
for g in polys(edit):
 md.polygon(list(g.exterior.coords),fill=255)
 for ring in g.interiors:md.polygon(list(ring.coords),fill=0)
mask.save(ROOT/'proposed-road-edit-mask.png')
(ROOT/'proposed-road.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'required_road_with_6px_margin','coordinates':'image pixels, y down'},'geometry':mapping(required)},{'type':'Feature','properties':{'name':'additional_road_mask'},'geometry':mapping(edit)}]}))
sections={}
for y in [103,120,140,160,200,575,600,630,650,675,690,710,730,750,770]:
 cut=required.intersection(box(650,y-.1,1200,y+.1));sections[str(y)]=list(cut.bounds) if not cut.is_empty else None
metrics={'model':{'total_length_px':180,'tractor_width_px':43,'trailer_width_px':36,'trailer_axle_px':85},'path':{'left_x':x0,'right_x':x1,'top_y':y0,'bottom_y':y1,'radius':r},'laps':3,'sample_count':len(states),'max_articulation_deg':max(abs(math.atan2(math.sin(s[2]-s[3]),math.cos(s[2]-s[3]))) for s in states)*180/math.pi,'sampled_footprints_outside_proposed_road':sum(s[4].difference(newroad).area>1e-6 for s in states),'independent_halfstep_violations':violations,'required_corridor_bounds':list(required.bounds),'corridor_sections_y':sections,'minimum_nominal_margin_px':6,'verdict':'Pass only for explicitly reconstructed screen-space road, excluding traffic and steering wheelbase limits'}
(ROOT/'proposed-measurements.json').write_text(json.dumps(metrics,indent=2)+'\n'); print(json.dumps(metrics,indent=2))
