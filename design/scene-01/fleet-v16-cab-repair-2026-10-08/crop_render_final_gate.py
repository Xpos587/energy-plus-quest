from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
for script,args in [('diagnostic_camera.py',['final','144','1']),('crop_render_map.py',['144','144']),('crop_render_shadow.py',['144'])]:
 with (P/f'final-map144-{script}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'fleet-v16-cab-repair.blend'),'--python',str(P/script),'--',*args],stdout=log,stderr=subprocess.STDOUT)
 print(script,r.returncode,flush=True);assert r.returncode==0
