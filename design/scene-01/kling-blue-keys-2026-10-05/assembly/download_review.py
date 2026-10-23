from pathlib import Path
import json,urllib.request,cv2,numpy as np,sys
cv2.setNumThreads(1);r=Path(__file__).resolve().parent;done=[]
for i in map(int,sys.argv[1:] or range(4)):
 j=r.parent/f'segment-{i}-result.json'
 if not j.read_text().strip():print(i,'pending',flush=True);continue
 data=json.loads(j.read_text());job=data[0] if isinstance(data,list) else data
 if job.get('status')!='completed':print(i,job.get('status'),flush=True);continue
 p=r/f'segment-{i}.mp4'
 if not p.exists():urllib.request.urlretrieve(job['result_url'],p)
 c=cv2.VideoCapture(str(p));fps=c.get(cv2.CAP_PROP_FPS);frames=[]
 while True:
  ok,f=c.read()
  if not ok:break
  frames.append(f)
 tiles=[]
 for n in range(0,len(frames),6):
  tile=cv2.resize(frames[n],(640,360));cv2.putText(tile,f'{n/fps:.2f}s',(8,20),0,.55,(0,0,0),1);tiles.append(tile)
 while len(tiles)%5:tiles.append(np.full_like(tiles[0],255))
 cv2.imwrite(str(r/f'segment-{i}-quarter-contact.jpg'),np.vstack([np.hstack(tiles[n:n+5]) for n in range(0,len(tiles),5)]))
 for n in [0,24,42,60,84,108,len(frames)-1]:cv2.imwrite(str(r/f'segment-{i}-inspect-{n:03}.png'),frames[n])
 metadata={'segment':i,'source':str(p),'fps':fps,'frames':len(frames),'dimensions':[frames[0].shape[1],frames[0].shape[0]],'duration_seconds':len(frames)/fps,'gate':'pending actual quarter-second native review','driver':'uncertified; exactly one person and empty passenger seat require review, not prompt inference'}
 (r/f'segment-{i}-receipt.json').write_text(json.dumps(metadata,indent=2));done.append(metadata);print(i,'downloaded',len(frames),fps,flush=True)
