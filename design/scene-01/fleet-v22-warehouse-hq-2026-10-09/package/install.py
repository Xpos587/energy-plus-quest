"""Authorized local install after media validation; backups outside public."""
from pathlib import Path
import json,shutil,os,time,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
assert (ROOT/'package.json').exists(),ROOT
validation=json.loads((P/'validation.json').read_text());assert len(validation)==4
for row in validation:
 st=row['probe']['streams'][0];assert st['nb_read_frames']=='1536'and float(st['duration'])==64 and row['decode_exit']==0
tracking=json.loads((P/'carrierTracking.json').read_text());assert len(tracking)==1536
state=Path.home()/'.local/state/energy-plus-quest/runtime-integration-v22-2026-10-09';backup=state/('previous-'+str(int(time.time())));backup.mkdir(parents=True)
D=ROOT/'public/scene1-live/separated-routes'
pairs=[(P/'city-motion-desktop.mp4',D/'city-motion-desktop.mp4'),(P/'city-motion-tablet.mp4',D/'city-motion-tablet.mp4'),(P/'city-motion-mobile.mp4',D/'city-motion-mobile.mp4'),(P/'city-poster.webp',D/'city-poster.webp'),(P/'carrierTracking.json',ROOT/'src/game/carrierTracking.json')]
for src,dst in pairs:
 assert src.exists(),src
 shutil.copy2(dst,backup/dst.name)
 temp=dst.with_name(dst.name+'.v22-stage');shutil.copy2(src,temp);os.replace(temp,dst)
if (D/'README.md').exists():shutil.copy2(D/'README.md',backup/'README.md')
(D/'README.md').write_text('# Scene1 current loop — v22\n\nSource and verification: `design/scene-01/fleet-v22-warehouse-hq-2026-10-09/`.\n\n64seconds,1536frames,24fps. Desktop3600×2500; tablet2560×1778; mobile1920×1334. Native4K Blender vehicle render with v21 compact trailer track/closer coupling. Warehouse architecture restored from08.10scenario digital-warehouse photo; city CGI upscale and local high-detail warehouse reconstruction; exact vector branding.\n\nFrame1→time0. Matching roof tracking exported from v22 source. H264CRF15 master, CRF16 smaller variants. Backups outside deploy tree.\n')
subprocess.run(['bun','run','build:app'],cwd=ROOT,check=True)
r={'installed':[str(dst.relative_to(ROOT))for _,dst in pairs],'backup':str(backup),'build_exit':0,'remote_deploy':False,'source':str(P.parent)}
(P/'install-receipt.json').write_text(json.dumps(r,indent=2));print('LOCAL_GAME_INSTALLED',flush=True)
