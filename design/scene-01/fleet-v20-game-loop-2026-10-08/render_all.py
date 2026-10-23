from pathlib import Path
import subprocess,json,time
P=Path(__file__).resolve().parent
source=P/'v20-game-loop.blend'
receipts=[]
for start in range(1,1537,48):
 end=start+47
 for script,args in [('render_map.py',[str(start),str(end)]),('render_shadow.py',[str(f) for f in range(start,end+1)])]:
  begin=time.monotonic()
  with (P/f'{script}-{start:04}.log').open('w') as log:
   r=subprocess.run(['/usr/bin/blender','-b',str(source),'--python',str(P/script),'--',*args],stdout=log,stderr=subprocess.STDOUT)
  receipts.append({'script':script,'first':start,'last':end,'exit':r.returncode,'seconds':time.monotonic()-begin})
  (P/'render-receipts.json').write_text(json.dumps(receipts,indent=2))
  print(receipts[-1],flush=True)
  if r.returncode:raise SystemExit(r.returncode)
