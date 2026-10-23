from pathlib import Path
import subprocess
P=Path(__file__).resolve().parent
archive=P/'pre-wheel-correction';archive.mkdir(exist_ok=True)
for pattern in ['final-truck*.png','style-trailer*.png','map-*.png','static-map-contact-sheet.png']:
 for p in P.glob(pattern):p.rename(archive/p.name)
for part in ['vehicles','shadow']:
 folder=archive/f'turn-{part}';folder.mkdir(exist_ok=True)
 for p in (P/f'turn-{part}').glob('*.png'):p.rename(folder/p.name)
def run(script,args,label):
 with (P/f'{label}.log').open('w') as log:r=subprocess.run(['/usr/bin/blender','-b',str(P/'merged.blend'),'--python',str(P/script),'--',*map(str,args)],stdout=log,stderr=subprocess.STDOUT)
 print(label,r.returncode,flush=True);assert r.returncode==0
for f in [102,103,104]:run('diagnostic_camera.py',['final',f,1],f'corrected-red-{f}')
for f,i in [(130,3),(192,4)]:run('diagnostic_camera.py',['final',f,i],f'corrected-cab-{i}-{f}')
for f in [130,131]:run('diagnostic_trailer.py',[f,3],f'corrected-trailer-{f}')
for f in [102,130,192,144]:run('render_map.py',[f,f],f'corrected-map-{f}')
run('render_shadow.py',[102,130,192,144],'corrected-static-shadows')
