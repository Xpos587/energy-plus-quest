from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
for part in ['vehicles','shadow']:
 p=P/f'turn-{part}/0144.png'
 if p.exists():p.rename(P/f'wheel-base-{part}-0144.png')
def run(script,args,label):
 with (P/f'{label}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'merged.blend'),'--python',str(P/script),'--',*map(str,args)],stdout=log,stderr=subprocess.STDOUT)
 print(label,r.returncode,flush=True);assert r.returncode==0
for f in [102,103,104]:run('diagnostic_camera.py',['final',f,1],f'final-red-{f}')
for f,i in [(130,3),(192,4)]:run('diagnostic_camera.py',['final',f,i],f'final-cab-{i}-{f}')
for f in [130,131]:run('diagnostic_trailer.py',[f,3],f'final-trailer-{f}')
for f in [102,130,192,144]:run('render_map.py',[f,f],f'final-map-{f}')
run('render_shadow.py',[102,130,192,144],'final-static-shadows')
