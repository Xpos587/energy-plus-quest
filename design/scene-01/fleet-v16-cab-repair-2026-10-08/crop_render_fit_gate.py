from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
for frame,i in ((91,1),(144,1),(11,4),(154,4)):
 with (P/f'fit-diagnostic-{i}-{frame}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'fleet-v16-cab-repair.blend'),'--python',str(P/'diagnostic_camera.py'),'--','fit',str(frame),str(i)],stdout=log,stderr=subprocess.STDOUT)
 print('fit',frame,i,r.returncode,flush=True);assert r.returncode==0
for script,args in (('crop_render_map.py',['144','144']),('crop_render_shadow.py',['144'])):
 with (P/f'fit-map144-{script}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'fleet-v16-cab-repair.blend'),'--python',str(P/script),'--',*args],stdout=log,stderr=subprocess.STDOUT)
 print(script,r.returncode,flush=True);assert r.returncode==0
