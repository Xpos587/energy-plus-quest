from pathlib import Path
import json,os
p=Path(__file__).resolve().parent
out={}
for folder in ['turn-vehicles','turn-shadow']:
 frames={int(f.stem) for f in (p/folder).glob('[0-9][0-9][0-9][0-9].png')};end=0
 while end+1 in frames:end+=1
 out[folder]={'count':len(frames),'contiguous':end}
receipt=p/'full-progress.json'
if receipt.exists():
 row=json.loads(receipt.read_text())['last_batch'];out['last_decoded']={k:row[k] for k in ['script','first','last','seconds','decoded']}
info=json.loads((p/'full-process.json').read_text())
try:os.kill(info['pid'],0);out['launcher_alive']=True
except ProcessLookupError:out['launcher_alive']=False
out['complete']=(p/'full-complete.json').exists()
print(json.dumps(out))
