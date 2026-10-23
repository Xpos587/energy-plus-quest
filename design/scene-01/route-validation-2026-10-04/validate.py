"""Deterministic screen-space swept-envelope diagnostic, not vehicle dynamics certification.
Run: uv run --with pillow --with shapely python design/scene-01/route-validation-2026-10-04/validate.py
"""
import json, math
from pathlib import Path
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'route-preflight-2026-10-04/map-v16.png'
# Manually recorded visible asphalt rectangles. Conservative, axis-aligned inner edges;
# buildings, sidewalks, other vehicles and lane rules are NOT automatically segmented.
BOUNDS=[('central_north',724,0,795,478),('middle_cross',401,483,1506,571),
 ('west_avenue',405,0,492,1045),('bottom_cross',492,697,1506,756),
 ('central_south',741,756,795,1045),('right_avenue',1076,0,1167,1045),
 ('top_cross',0,120,1506,160)]
road=unary_union([box(*b[1:]) for b in BOUNDS])
# Hitch/reference line, 40 px circular transitions at the three requested loop corners.
def line(a,b):
 n=math.ceil(math.dist(a,b)); return [(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n)]
def arc(c,r,a,b):
 n=math.ceil(abs(b-a)*r); return [(c[0]+r*math.cos(a+(b-a)*i/n),c[1]+r*math.sin(a+(b-a)*i/n)) for i in range(n)]
p=line((742,340),(742,713))+arc((782,713),40,math.pi,math.pi/2)+line((782,753),(1105,753))+arc((1105,713),40,math.pi/2,0)+line((1145,713),(1145,143))+arc((1105,143),40,0,-math.pi/2)+line((1105,103),(782,103))+arc((782,143),40,-math.pi/2,-math.pi)+line((742,143),(742,340))
def body(x,y,a,front,back,width):
 u=(math.cos(a),math.sin(a)); v=(-u[1],u[0]); return Polygon([(x+f*u[0]+s*v[0],y+f*u[1]+s*v[1]) for f,s in [(front,width/2),(front,-width/2),(-back,-width/2),(-back,width/2)]])
phi=math.pi/2; states=[]
for i,(x,y) in enumerate(p[:-1]):
 nx,ny=p[i+1]; theta=math.atan2(ny-y,nx-x); ds=math.hypot(nx-x,ny-y)
 phi+=ds*math.sin(theta-phi)/85
 tractor=body(x,y,theta,70,10,43); trailer=body(x,y,phi,0,110,36)
 footprint=unary_union([tractor,trailer]); outside=footprint.difference(road).area
 states.append((x,y,theta,phi,footprint,outside))
img=Image.open(SOURCE).convert('RGBA'); overlay=Image.new('RGBA',img.size); d=ImageDraw.Draw(overlay)
for b in BOUNDS:d.rectangle(b[1:],fill=(35,210,230,28),outline=(0,120,170,170),width=2)
for st in states[::8]:
 for poly in getattr(st[4],'geoms',[st[4]]):d.polygon(list(poly.exterior.coords),fill=(255,0,40,20) if st[5]>1 else (0,200,40,20))
d.line(p,fill=(110,0,190,255),width=4)
for idx in [0,180,440,800,1150,1500]:
 if idx>=len(states):continue
 st=states[idx]
 for poly in getattr(st[4],'geoms',[st[4]]):d.line(list(poly.exterior.coords),fill=(210,0,30,255),width=3)
d.rectangle((515,592,1050,666),fill=(255,245,230,235));d.text((526,610),'BLOCKED: proposed x742 south crosses solid city block',fill=(130,0,0));d.text((526,636),'No turning radius or shorter rig creates this missing road.',fill=(130,0,0))
d.rectangle((15,880,367,962),fill=(255,255,255,235));d.text((25,895),'MAGENTA: proposed hitch path / radius 40px',fill=(70,0,120));d.text((25,920),'RED: envelope outside recorded asphalt',fill=(160,0,0));d.text((25,945),'CYAN: manual conservative road rectangles',fill=(0,80,130))
Image.alpha_composite(img,overlay).convert('RGB').save(ROOT/'swept-path-diagnostic.png')
metrics={'source_dimensions':[img.width,img.height], 'model':{'tractor_length':80,'tractor_width':43,'trailer_length':110,'trailer_width':36,'straight_total_length':180,'hitch_to_trailer_axle':85,'rounding_radius':40},'manual_road_rectangles':[{'name':b[0],'xyxy':b[1:]} for b in BOUNDS],'sample_count':len(states),'outside_samples':sum(s[5]>1 for s in states),'max_outside_area_px2':round(max(s[5] for s in states),2),'max_articulation_degrees':round(max(abs(math.atan2(math.sin(s[2]-s[3]),math.cos(s[2]-s[3]))) for s in states)*180/math.pi,2),'verdict':'FAIL; missing north-south roadway across y571..697 at x742. Raster diagnostic only.'}
(ROOT/'measurements.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics,indent=2))
