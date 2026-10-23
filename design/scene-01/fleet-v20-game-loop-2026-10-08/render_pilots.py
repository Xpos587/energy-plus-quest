from pathlib import Path
import subprocess,json
P=Path(__file__).resolve().parent;source=P/'v20-game-loop.blend';frames=[1,385,769,1153,1536,1537]
for f in frames:
 for script,args in [('render_map.py',[str(f),str(f)]),('render_shadow.py',[str(f)])]:
  with (P/f'pilot-{f}-{script}.log').open('w')as log:r=subprocess.run(['/usr/bin/blender','-b',str(source),'--python',str(P/script),'--',*args],stdout=log,stderr=subprocess.STDOUT)
  assert r.returncode==0,(f,script,r.returncode)
  print('PILOT',f,script,flush=True)
