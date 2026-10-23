from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
for frame in (144,145,146):
 with (P/f'wheel-diagnostic-{frame}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'wheels-base.blend'),'--python',str(P/'diagnostic_camera.py'),'--','wheels',str(frame),'1'],stdout=log,stderr=subprocess.STDOUT)
 print(frame,r.returncode,flush=True);assert r.returncode==0
for script,args in [('render_map.py',['144','144']),('render_shadow.py',['144'])]:
 with (P/f'wheel-map144-{script}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'wheels-base.blend'),'--python',str(P/script),'--',*args],stdout=log,stderr=subprocess.STDOUT)
 print(script,r.returncode,flush=True);assert r.returncode==0
