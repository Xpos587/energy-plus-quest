from pathlib import Path
import subprocess,json,time
P=Path(__file__).resolve().parent;receipt=[]
for start,end in ((97,144),(145,192)):
 for script,args in [('render_map.py',[str(start),str(end)]),('render_shadow.py',[str(f) for f in range(start,end+1)])]:
  begin=time.monotonic()
  with (P/f'{script}-{start}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'merged.blend'),'--python',str(P/script),'--',*args],stdout=log,stderr=subprocess.STDOUT)
  receipt.append({'script':script,'start':start,'end':end,'exit':r.returncode,'seconds':time.monotonic()-begin});(P/'crop-sequence-render-receipt.json').write_text(json.dumps(receipt,indent=2));print(receipt[-1],flush=True)
  if r.returncode:raise SystemExit(r.returncode)
