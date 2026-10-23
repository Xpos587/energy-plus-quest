from pathlib import Path
import cv2,numpy as np,json
cv2.setNumThreads(1);r=Path(__file__).resolve().parent
configs=[((340,220,590,625),(409,350)),((470,180,755,625),(531,567)),((450,40,755,415),(710,285)),((340,40,610,410),(490,120))]
for seg,(roi,init) in enumerate(configs):
 cap=cv2.VideoCapture(str(r/f'segment-{seg}.mp4'));x0,y0,x1,y1=roi;bg=cv2.imread(str(r/f'segment-{seg}-layer/temporal-background-roi.png'));prev=np.array(init,float)-[x0,y0];vel=np.zeros(2);yy,xx=np.indices(bg.shape[:2]);rows=[]
 for n in range(121):
  ok,f=cap.read();assert ok;im=f[y0:y1,x0:x1];h=cv2.cvtColor(im,cv2.COLOR_BGR2HSV);delta=np.max(abs(im.astype(float)-bg.astype(float)),axis=2);pred=prev+vel*.5;distance=(xx-pred[0])**2+(yy-pred[1])**2
  eligible=(h[:,:,0]>=95)&(h[:,:,0]<=125)&(h[:,:,1]>110)&(h[:,:,2]>35)&(delta>12)&(distance<25**2)
  weights=(np.clip((h[:,:,1].astype(float)-110)/145,0,1)**3)*np.clip(delta-12,0,100)*eligible
  assert weights.sum()>0,(seg,n)
  center=np.array([(weights*xx).sum()/weights.sum(),(weights*yy).sum()/weights.sum()]);v=center-prev;norm=np.linalg.norm(v);vel=v*min(1,7/max(norm,1e-6));prev=center;c=center+[x0,y0]
  rows.append({'frame':n,'cab_px':c.tolist(),'cab_roof_estimate':[float(c[0]/1280),float(c[1]/720)],'eligible_source_pixels':int(eligible.sum())})
 steps=np.linalg.norm(np.diff([a['cab_px'] for a in rows],axis=0),axis=1);(r/f'segment-{seg}-layer/cab-tracking.json').write_text(json.dumps({'fps':24,'frames':121,'dimensions':[1280,720],'type':'Observed source moving blue cab pixels, saturation-weighted local centroid within predicted25px window. Avoids rear-wheel/component switches. Image cab roof estimate, not 3D anchor.','max_step_px':float(steps.max()),'rows':rows},indent=2));print(seg,'max',steps.max(),'end',rows[-1]['cab_px'])
