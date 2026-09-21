"""Run with a projection export. CSS-pixel budget, not source-image resolution."""
import json,sys
from pathlib import Path
v=json.loads(Path(sys.argv[1]).read_text())['views']['mobile']
x0,y0,x1,y1=v['bounds']
scale=min((320-24)/(x1-x0),(350-24)/(y1-y0))
sizes=[max(t['bounds'][2]-t['bounds'][0],t['bounds'][3]-t['bounds'][1])*scale for row in v['tracks'] for t in row]
print('320px phone, smallest projected truck long edge:',round(min(sizes),2))
assert min(sizes)>=48,'Truck is still too small in the tightest phone composition'
