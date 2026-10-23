from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
for prefix,frame,i,rest in [('after',31,1,False),('after',144,1,False),('after',11,4,False),('after',154,4,False),('after-rest',91,1,True),('after-rest',91,4,True)]:
 cmd=['/usr/bin/blender','-b',str(P/'fleet-v16-cab-repair.blend'),'--python',str(P/'diagnostic_camera.py'),'--',prefix,str(frame),str(i)]
 if rest:cmd+=['neutral']
 with (P/f'diagnostic-{prefix}-{i}-{frame}.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 print(prefix,frame,i,r.returncode,flush=True);assert r.returncode==0
