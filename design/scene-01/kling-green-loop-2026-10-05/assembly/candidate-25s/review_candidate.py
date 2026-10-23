from pathlib import Path
import cv2,json,numpy as np
cv2.setNumThreads(1);r=Path(__file__).resolve().parent
cap=cv2.VideoCapture(str(r/'composite.mp4'));frames=[]
while True:
 ok,f=cap.read()
 if not ok:break
 frames.append(f)
assert len(frames)==600 and frames[0].shape==(720,1280,3)
report=json.loads((r/'seam-report.json').read_text());panels=[];seamvideo=cv2.VideoWriter(str(r/'seams-review.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),24,(660,360))
for boundary in [120,240,360,480,600]:
 index=boundary%600;pair=[frames[(index-1)%600],frames[index]]
 row=[]
 tracking=json.loads((r/'green-tracking.json').read_text())['rows'];center=np.mean([tracking[(index-1)%600]['centroid_px'],tracking[index]['centroid_px']],axis=0).astype(int);x=int(np.clip(center[0]-165,0,950));y=int(np.clip(center[1]-150,0,420))
 for offset in range(-24,24):
  i=(index+offset)%600;tile=frames[i][y:y+300,x:x+330].copy();cv2.putText(tile,f'seam {boundary/24:g}s / frame {i}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,0,0),1);seamvideo.write(cv2.resize(tile,(660,360)))
 for i,frame in enumerate(pair):
  tile=frame[y:y+300,x:x+330].copy();cv2.putText(tile,('end' if i==0 else 'start')+f' seam {boundary/24:g}s',(5,20),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1);row.append(tile)
 panels.append(np.hstack(row))
seamvideo.release();cv2.imwrite(str(r/'decoded-video-seams.jpg'),np.vstack(panels))
report.update({'decoded_video_frames':600,'decoded_video_dimensions':[1280,720],'decoded_duration_seconds':25,'status':'REVIEW CANDIDATE, NOT CLEAN FINAL: correct complete road route sampled at quarter seconds; 2a first frame retains a tiny cream sidewalk/pot fragment above trailer; seam 2a→2b and 2b→3 have visible 5px position changes; velocity and drawing style change at some clip boundaries. No duplication or wrong road observed in accepted motion samples.','roof_tracking':'green-tracking.json: observed opaque white trailer centroid estimate; not native 3D roof anchor','retiming':'Not applied: retaining original 5s per half prevents hiding existing speed variation before review.'});(r/'seam-report.json').write_text(json.dumps(report,indent=2));print('600 decoded frames, 1280x720, 25s; five seam crops generated')
