from pathlib import Path
import subprocess,json,time,os
P=Path(__file__).resolve().parent
marker=P.parent/'render/full-complete.json'
while not marker.exists():
 time.sleep(20)
d=json.loads(marker.read_text());assert d['both_passes_decoded']and len(d['frames_checked'])==1537
subprocess.run(['uv','run','--with','pillow','--with','numpy',str(P/'compose.py'),'--full'],check=True)
print('DELIVERY_MEDIA_READY',flush=True)
