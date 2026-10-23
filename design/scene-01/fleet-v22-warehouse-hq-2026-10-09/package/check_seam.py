from pathlib import Path
from PIL import Image
import numpy as np,json,subprocess
P=Path(__file__).resolve().parent
rows={}
for name in ('turn-vehicles','turn-shadow'):
 a=np.asarray(Image.open(P.parent/'render'/name/'0001.png'),dtype=np.int16);b=np.asarray(Image.open(P.parent/'render'/name/'1537.png'),dtype=np.int16);d=np.abs(a-b)
 rows[name]={'boundary_mae_255':float(d.mean()),'pixels_any_channel_over8':int((d.max(axis=2)>8).sum()),'max_channel_difference':int(d.max())}
 assert rows[name]['boundary_mae_255']<.05,rows[name]
track=json.loads((P/'carrierTracking.json').read_text());r=json.loads((P/'carrierTracking.receipt.json').read_text());assert r['normalized_start_end_error']<1e-5
rows['tracking_boundary_error']=r['normalized_start_end_error']
# Actual encoded last frame is one frame before closure; preserve normal motion, no duplicate hold.
subprocess.run(['ffmpeg','-v','error','-y','-sseof','-0.042','-i',str(P/'city-motion-desktop.mp4'),'-frames:v','1',str(P/'encoded-last.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'city-motion-desktop.mp4'),'-frames:v','1',str(P/'encoded-first.png')],check=True)
(P/'seam-check.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
