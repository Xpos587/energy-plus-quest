from pathlib import Path
import cv2,numpy as np,json,os
cv2.setNumThreads(1)
r=Path(__file__).resolve().parent;out=r/'candidate-25s';out.mkdir(exist_ok=True);rd=out/'rgba-frames';cd=out/'composite-frames';rd.mkdir(exist_ok=True);cd.mkdir(exist_ok=True)
first=r.parents[1]/'kling-layer-extract-2026-10-05'
segments=[('1',first),('2a',r/'segment-2a-layer'),('2b',r/'segment-2b-layer'),('3',r/'segment-3-layer'),('4-translated',r/'seam-correction')]
base=cv2.imread(str(first/'empty-map-padded.png'));rows=[];layers=[];comps=[];bounds=[]
for seg,d in segments:
 for j,f in enumerate(sorted((d/'rgba-frames').glob('*.png'))[:120]):
  a=cv2.imread(str(f),cv2.IMREAD_UNCHANGED);idx=len(rows);alpha=a[:,:,3:4].astype(np.float32)/255;comp=(a[:,:,:3]*alpha+base*(1-alpha)).round().astype(np.uint8)
  target=rd/f'{idx+1:04}.png'
  if target.exists():target.unlink()
  os.link(f,target);cv2.imwrite(str(cd/f'{idx+1:04}.png'),comp)
  body=a[:,:,3]>127;ys,xs=np.where(body);hsv=cv2.cvtColor(a[:,:,:3],cv2.COLOR_BGR2HSV);white=body&(hsv[:,:,1]<70)&(hsv[:,:,2]>150);wy,wx=np.where(white);green=body&(hsv[:,:,0]>35)&(hsv[:,:,0]<90)&(hsv[:,:,1]>65);gy,gx=np.where(green)
  rows.append({'frame':idx,'time':idx/24,'segment':seg,'centroid_px':[float(xs.mean()),float(ys.mean())],'roof_estimate':[float(wx.mean()/1280),float(wy.mean()/720)],'cab_estimate':[float(gx.mean()/1280),float(gy.mean()/720)]})
  if j in [0,119]:bounds.append((seg,j,a,comp))
seams=[];panels=[]
for k in range(5):
 end=bounds[k*2+1];start=bounds[((k+1)%5)*2];a=end[2][:,:,3]>127;b=start[2][:,:,3]>127;i=k*120+119;n=((k+1)%5)*120;delta=np.array(rows[n]['centroid_px'])-rows[i]['centroid_px']
 seams.append({'from':end[0],'to':start[0],'centroid_step_px':float(np.linalg.norm(delta)),'centroid_vector_px':delta.tolist(),'alpha_iou':float((a&b).sum()/(a|b).sum()),'previous_step_px':float(np.linalg.norm(np.array(rows[i]['centroid_px'])-rows[i-1]['centroid_px'])),'next_step_px':float(np.linalg.norm(np.array(rows[n+1]['centroid_px'])-rows[n]['centroid_px']))})
 ys,xs=np.where(a|b);cx=int(xs.mean());cy=int(ys.mean());x=max(0,min(1280-220,cx-110));y=max(0,min(720-180,cy-90));tile=np.hstack([end[3][y:y+180,x:x+220],start[3][y:y+180,x:x+220]]);cv2.putText(tile,end[0]+' end | '+start[0]+' start',(5,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1);panels.append(tile)
cv2.imwrite(str(out/'seams.png'),np.vstack(panels));(out/'green-tracking.json').write_text(json.dumps({'fps':24,'frames':600,'dimensions':[1280,720],'convention':'x/width,y/height from upper left; roof estimate is observed opaque white trailer pixels centroid, not a native 3D anchor','rows':rows},indent=2));(out/'seam-report.json').write_text(json.dumps({'candidate_duration_seconds':25,'frames':600,'fps':24,'seams':seams,'status':'PENDING actual seam visual review; only green vehicle layer on exact empty static map'},indent=2));print(json.dumps(seams,indent=2))
