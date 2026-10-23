import json,numpy as np
from pathlib import Path
from shapely.geometry import MultiPoint
from shapely.ops import unary_union
P=Path(__file__).resolve().parent;d=json.loads((P/'clearance-source.json').read_text());local=[]
for h in d['hulls']:
 pts=np.asarray(h['points']);xy=np.asarray(MultiPoint(pts[:,:2]).convex_hull.exterior.coords);local.append(np.column_stack([xy,np.zeros(len(xy)),np.ones(len(xy))]))
rows={f'{i+1}-{j+1}':{'min_distance':1000,'overlap_frames':[],'max_area':0}for i in range(4)for j in range(i+1,4)}
for f,mats in enumerate(d['frames'],1):
 parts=[MultiPoint((v@np.asarray(m).T)[:,:2]).convex_hull for v,m in zip(local,mats)];rigs=[unary_union(parts[i*2:i*2+2])for i in range(4)]
 for i in range(4):
  for j in range(i+1,4):
   r=rows[f'{i+1}-{j+1}'];dist=rigs[i].distance(rigs[j]);r['min_distance']=min(r['min_distance'],dist)
   if dist<1e-6:
    area=rigs[i].intersection(rigs[j]).area;r['max_area']=max(r['max_area'],area)
    if area>.01:r['overlap_frames'].append(f)
(P/'clearance.json').write_text(json.dumps(rows,indent=2));print(json.dumps({k:{'min':v['min_distance'],'overlap_count':len(v['overlap_frames']),'max_area':v['max_area'],'first':v['overlap_frames'][:8]}for k,v in rows.items()},indent=2))
