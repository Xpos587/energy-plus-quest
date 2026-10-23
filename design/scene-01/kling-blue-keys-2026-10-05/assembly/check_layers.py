from pathlib import Path
import cv2,numpy as np,json
cv2.setNumThreads(1);r=Path(__file__).resolve().parent;panels=[];records=[]
for i in range(4):
 d=r/f'segment-{i}-layer';metrics=json.loads((d/'extraction-report.json').read_text())['frames_metrics'];tiles=[]
 for n in [0,12,42,60,84,114]:
  a=cv2.imread(str(d/f'rgba-frames/{n+1:04}.png'),-1);alpha=a[:,:,3:4]/255;im=(a[:,:,:3]*alpha+230*(1-alpha)).astype(np.uint8);ys,xs=np.where(a[:,:,3]>127);x=int(np.clip(xs.mean()-85,0,1110));y=int(np.clip(ys.mean()-85,0,550));tile=im[y:y+170,x:x+170];tile=cv2.resize(tile,(340,340),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{i} / {n/24:g}s',(5,20),0,.6,(0,0,0),1);tiles.append(tile)
 panels.append(np.hstack(tiles));rows=[]
 for n,f in enumerate(sorted((d/'rgba-frames').glob('*.png'))):
  a=cv2.imread(str(f),-1);h=cv2.cvtColor(a[:,:,:3],cv2.COLOR_BGR2HSV);mask=((a[:,:,3]>127)&(h[:,:,0]>=95)&(h[:,:,0]<=125)&(h[:,:,1]>=170)).astype(np.uint8);nc,l,s,c=cv2.connectedComponentsWithStats(mask);j=1+np.argmax(s[1:,4]);rows.append({'frame':n,'cab_px':c[j].tolist(),'cab_roof_estimate':[float(c[j,0]/1280),float(c[j,1]/720)]})
 (d/'cab-tracking.json').write_text(json.dumps({'fps':24,'dimensions':[1280,720],'frames':121,'type':'largest observed opaque blue cab cluster centroid, not 3D anchor','rows':rows},indent=2));records.append({'segment':i,'frames':len(rows),'cab_step_max_px':float(np.linalg.norm(np.diff([a['cab_px'] for a in rows],axis=0),axis=1).max())})
cv2.imwrite(str(r/'all-layer-samples-2x.jpg'),np.vstack(panels));(r/'tracking-validation.json').write_text(json.dumps(records,indent=2));print(records)
