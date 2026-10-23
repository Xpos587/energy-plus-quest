from pathlib import Path
import subprocess,json,time
P=Path(__file__).resolve().parent
receipts=[]
for start,end in ((1,48),(49,96),(97,144),(145,192)):
 t=time.monotonic();log=P/f'render-chunk-{start:04}.log'
 with log.open('w') as f:
  run=subprocess.run(['/usr/bin/blender','-b',str(P/'fleet-v16-smoke.blend'),'--python',str(P/'render_motion.py'),'--',str(start),str(end)],stdout=f,stderr=subprocess.STDOUT)
 receipt={'start':start,'end':end,'returncode':run.returncode,'seconds':time.monotonic()-t};receipts.append(receipt);(P/'chunk-receipts.json').write_text(json.dumps(receipts,indent=2));print(receipt,flush=True)
 if run.returncode!=0:raise SystemExit(run.returncode)
