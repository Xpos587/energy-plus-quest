"""Install approved v23 warehouse media locally, preserving existing tracking."""
from pathlib import Path
import json, shutil, os, time, subprocess
P = Path(__file__).resolve().parent
ROOT = P.parents[3]
validation = json.loads((P / 'validation.json').read_text())
assert len(validation) == 4
for row in validation:
    stream = row['probe']['streams'][0]
    assert stream['nb_read_frames'] == '1536' and float(stream['duration']) == 64 and row['decode_exit'] == 0
backup = Path.home() / '.local/state/energy-plus-quest/runtime-integration-v23-2026-10-09' / ('previous-' + str(int(time.time())))
backup.mkdir(parents=True)
D = ROOT / 'public/scene1-live/separated-routes'
names = ['city-motion-desktop.mp4', 'city-motion-tablet.mp4', 'city-motion-mobile.mp4', 'city-poster.webp']
for name in names:
    dst = D / name
    shutil.copy2(dst, backup / name)
    temp = dst.with_name(name + '.v23-stage')
    shutil.copy2(P / name, temp)
    os.replace(temp, dst)
shutil.copy2(D / 'README.md', backup / 'README.md')
(D / 'README.md').write_text('# Scene1 current loop — v23\n\nSource: `design/scene-01/warehouse-v23-geometry-2026-10-09/`. Approved warehouse geometry, locally composited over v22 city. Existing native v22 vehicle/shadow frames and tracking preserved.\n\n64 seconds, 1536 frames, 24 fps. Desktop 3600×2500; tablet 2560×1778; mobile 1920×1334. Full decode verified before installation. Backups outside deploy tree.\n')
component = ROOT / 'src/components/IllustratedCityMap.tsx'
source = component.read_text()
assert '?v=22' in source or '?v=23' in source
shutil.copy2(component, backup / component.name)
component.write_text(source.replace('?v=22', '?v=23'))
with (P / 'build.log').open('w') as log:
    subprocess.run(['bun', 'run', 'build:app'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
(P / 'install-receipt.json').write_text(json.dumps({'installed': names, 'backup': str(backup), 'build_exit': 0, 'remote_deploy': False}, indent=2))
print('LOCAL_GAME_INSTALLED')
