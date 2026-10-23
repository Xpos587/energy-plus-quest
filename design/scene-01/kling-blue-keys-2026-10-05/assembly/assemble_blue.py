from pathlib import Path
import cv2,numpy as np,json,os
cv2.setNumThreads(1);r=Path(__file__).resolve().parent;out=r/'candidate-20s';out.mkdir(exist_ok=True);rd=out/'rgba-frames';cd=out/'composite-frames';rd.mkdir(exist_ok=True);cd.mkdir(exist_ok=True)
base=cv2.imread(str(r/'segment-0-layer/empty-map-padded.png'));rows=[];alllayers=[];allcomps=[]
for seg in range(4):
 d=r/f'segment-{seg}-layer';tracking=json.loads((d/'cab-tracking.json').read_text())['rows']
 for j,f in enumerate(sorted((d/'rgba-frames').glob('*.png'))[:120]):
  a=cv2.imread(str(f),-1);idx=len(rows);alpha=a[:,:,3:4]/255;comp=(a[:,:,:3]*alpha+base*(1-alpha)).round().astype(np.uint8);target=rd/f'{idx+1:04}.png'
  if target.exists():target.unlink()
  os.link(f,target);cv2.imwrite(str(cd/f'{idx+1:04}.png'),comp);row=dict(tracking[j]);row.update(frame=idx,time=idx/24,segment=seg,source_frame=j);rows.append(row);alllayers.append(a);allcomps.append(comp)
seams=[];panels=[];writer=cv2.VideoWriter(str(out/'seams-4x-source.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),24,(880,720))
for k in range(4):
 end=k*120+119;start=((k+1)%4)*120;c0=np.array(rows[end]['cab_px']);c1=np.array(rows[start]['cab_px']);a=alllayers[end][:,:,3]>127;b=alllayers[start][:,:,3]>127;steps=np.linalg.norm(np.diff([x['cab_px'] for x in rows[k*120:(k+1)*120]],axis=0),axis=1)
 seams.append({'from':k,'to':(k+1)%4,'cab_step_px':float(np.linalg.norm(c1-c0)),'cab_vector_px':(c1-c0).tolist(),'previous_step_px':float(steps[-1]),'segment_typical_step_median_px':float(np.median(steps)),'next_step_px':float(np.linalg.norm(np.array(rows[start+1]['cab_px'])-c1)),'alpha_iou':float((a&b).sum()/(a|b).sum())});ys,xs=np.where(a|b);x=int(np.clip(xs.mean()-110,0,1060));y=int(np.clip(ys.mean()-90,0,540));tiles=[]
 for idx,label in [(end,str(k)+' end'),(start,str((k+1)%4)+' start')]:
  tile=allcomps[idx][y:y+180,x:x+220].copy();cv2.putText(tile,label,(5,18),0,.45,(0,0,0),1);tiles.append(tile)
 panels.append(np.hstack(tiles))
 for off in range(-24,24):
  idx=(start+off)%480;tile=cv2.resize(allcomps[idx][y:y+180,x:x+220],(880,720),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{k} to {(k+1)%4} / frame {idx}',(10,30),0,.7,(0,0,0),2);writer.write(tile)
writer.release();cv2.imwrite(str(out/'seams-native.png'),np.vstack(panels));(out/'blue-tracking.json').write_text(json.dumps({'fps':24,'frames':480,'duration_seconds':20,'dimensions':[1280,720],'hotspot':'largest opaque blue cab cluster centroid, normalized upper left; observed image estimate not 3D anchor','rows':rows},indent=2));(out/'seam-report.json').write_text(json.dumps({'fps':24,'frames':480,'duration_seconds':20,'seams':seams,'retiming':False,'translation':False,'crossfade':False,'driver_count':'Exactly one and empty passenger seat remain uncertain at native scale','status':'Pending actual seam and alpha review'},indent=2));print(json.dumps(seams,indent=2))
