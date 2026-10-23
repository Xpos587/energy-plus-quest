from pathlib import Path
import subprocess,json,time
P=Path(__file__).resolve().parent;receipt=[]
for start,end in ((73,120),(121,168)):
 for script,arguments in (('render_motion.py',[str(start),str(end)]),('render_motion_shadow.py',[str(f) for f in range(start,end+1)])):
  begin=time.monotonic()
  with (P/f'{script}-{start}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'fleet-v16-worn-motion.blend'),'--python',str(P/script),'--',*arguments],stdout=log,stderr=subprocess.STDOUT)
  receipt.append({'script':script,'start':start,'end':end,'exit':r.returncode,'seconds':time.monotonic()-begin});(P/'proof-render-receipt.json').write_text(json.dumps(receipt,indent=2));print(receipt[-1],flush=True)
  if r.returncode:raise SystemExit(r.returncode)
