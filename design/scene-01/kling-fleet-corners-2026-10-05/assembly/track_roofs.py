from pathlib import Path
import json,cv2,numpy as np
cv2.setNumThreads(1);r=Path(__file__).resolve().parent;o=r/'source-roof-tracking';o.mkdir(exist_ok=True)
configs={'0-1':((690,65,1005,320),(977,210)), '1-mid':((340,45,850,680),(571,126)), 'mid-2':((340,45,850,680),(459,158)), '2-3':((605,220,940,620),(672,320)), '3-0':((760,170,1020,620),(877,575))}
empty=cv2.imread(str(r.parents[1]/'four-truck-loop-2026-10-04/v2b-empty-map.png'));base=np.full((720,1280,3),255,np.uint8);base[:,121:1158]=cv2.resize(empty,(1037,720));summary={}
for color in ['red','yellow']:
 for seg,(roi,init) in configs.items():
  cap=cv2.VideoCapture(str(r.parent/f'{color}-{seg}.mp4'));fps=cap.get(cv2.CAP_PROP_FPS);frames=[]
  while True:
   ok,f=cap.read()
   if not ok:break
   frames.append(f)
  assert fps==24 and len(frames)==121
  x0,y0,x1,y1=roi;local=seg in ['1-mid','mid-2'];q=1045/460 if local else 1;ref=base.copy()
  if local:ref[:]=255;ref[:,311:968]=cv2.resize(empty[100:560,700:1120],(657,720))
  M=np.array([[460/1045,0,121+700*720/1045-311*460/1045],[0,460/1045,100*720/1045]],np.float32) if local else np.array([[1,0,0],[0,1,0]],np.float32)
  bg=np.median(np.stack([f[y0:y1,x0:x1] for f in frames]),axis=0).astype(np.uint8);hbg=cv2.cvtColor(bg,cv2.COLOR_BGR2HSV);hr=cv2.cvtColor(ref[y0:y1,x0:x1],cv2.COLOR_BGR2HSV);road=(hr[:,:,0]>=85)&(hr[:,:,0]<=125)&(hr[:,:,1]>40)
  colored=(((hbg[:,:,0]<12)|(hbg[:,:,0]>170)) if color=='red' else ((hbg[:,:,0]>=15)&(hbg[:,:,0]<=35)))&(hbg[:,:,1]>100);bg[colored&road]=ref[y0:y1,x0:x1][colored&road]
  prev=np.array(init,float)-[x0,y0];vel=np.zeros(2);yy,xx=np.indices(bg.shape[:2]);rows=[];panels=[]
  for i,f in enumerate(frames):
   im=f[y0:y1,x0:x1];h=cv2.cvtColor(im,cv2.COLOR_BGR2HSV);delta=np.max(abs(im.astype(np.int16)-bg.astype(np.int16)),axis=2);cm=(((h[:,:,0]<12)|(h[:,:,0]>170)) if color=='red' else ((h[:,:,0]>=15)&(h[:,:,0]<=35)))&(h[:,:,1]>100)&(h[:,:,2]>35)&(delta>12)&road
   pred=prev+vel*.5;eligible=cm&((xx-pred[0])**2+(yy-pred[1])**2<(25*q)**2);w=np.clip((h[:,:,1].astype(float)-100)/155,0,1)**3*(1+np.clip(delta,0,80))*eligible;assert w.sum()>0,(color,seg,i)
   cutoff=np.quantile(yy[eligible],.40);w*=yy<=cutoff;assert w.sum()>0;center=np.array([(w*xx).sum()/w.sum(),(w*yy).sum()/w.sum()]);v=center-prev;vel=v*min(1,7*q/max(np.linalg.norm(v),1e-6));prev=center;source=center+[x0,y0];mapped=M@np.r_[source,1];rows.append({'frame':i,'time':i/24,'source_cab_px':source.tolist(),'cab_px':mapped.tolist(),'cab_roof_estimate':(mapped/[1280,720]).tolist(),'observed_source_pixels':int(eligible.sum())})
   if i%6==0:
    cx,cy=source.round().astype(int);xx0=int(np.clip(cx-90*q,0,1280-180*q));yy0=int(np.clip(cy-65*q,0,720-130*q));tile=f[yy0:yy0+round(130*q),xx0:xx0+round(180*q)].copy();cv2.circle(tile,(cx-xx0,cy-yy0),round(5*q),(0,0,255) if color=='yellow' else (0,255,0),max(1,round(q)));tile=cv2.resize(tile,(360,260),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{color} {seg} {i/24:.2f}s',(5,20),0,.5,(0,0,0),1);panels.append(tile)
  points=np.array([a['cab_px'] for a in rows]);steps=np.linalg.norm(np.diff(points,axis=0),axis=1);report={'fps':24,'frames':121,'dimensions':[1280,720],'projection':M.tolist(),'hotspot':'Observed upper40percent of local cab-color pixels, saturation-weighted centroid, moving local window; normalized image estimate not3D anchor','max_step_px':float(steps.max()),'rows':rows};(o/f'{color}-{seg}.json').write_text(json.dumps(report,indent=2));cv2.imwrite(str(o/f'{color}-{seg}-quarter-overlay.jpg'),np.vstack([np.hstack(panels[j:j+7]) for j in range(0,21,7)]));summary[color+'-'+seg]={'first_cab':points[0].tolist(),'frame54_cab':points[54].tolist(),'last_kept_cab':points[119].tolist(),'first54_net_px':float(np.linalg.norm(points[54]-points[0])),'first54_path_px':float(steps[:54].sum()),'first54_median_step_px':float(np.median(steps[:54])),'remaining_median_step_px':float(np.median(steps[54:119])),'max_step_px':float(steps.max())};print(color,seg,summary[color+'-'+seg],flush=True)
(o/'timing-receipt.json').write_text(json.dumps(summary,indent=2))
