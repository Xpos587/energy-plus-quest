from pathlib import Path
import sys, json
import numpy as np
import cv2
import torch
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / '.tmp-work/warehouse-segmentation-model'))
from mobile_sam import sam_model_registry, SamPredictor

out = Path(__file__).parent
(out / 'masks').mkdir(exist_ok=True)
model = sam_model_registry['vit_t'](checkpoint=str(root / '.tmp-work/warehouse-segmentation-model/weights/mobile_sam.pt')).to('cpu').eval()
torch.set_num_threads(4)
predictor = SamPredictor(model)
prompts = {
 'wide': {
  'crane': {'box':[810,75,1190,580], 'points':[[907,353],[1030,230],[969,475],[1092,143]]},
  'petr': {'box':[1230,0,1500,390], 'points':[[1340,185],[1390,285],[1440,80]]},
  'remote': {'box':[225,235,490,550], 'points':[[355,390],[385,285],[269,445]]},
 },
 'tall': {
  'crane': {'box':[335,409,712,991], 'points':[[445,730],[573,560],[519,900],[632,438]]},
  'petr': {'box':[699,241,925,651], 'points':[[775,479],[854,361],[814,582]]},
  'remote': {'box':[8,550,288,873], 'points':[[145,670],[166,778],[77,604]]},
 },
}
result = {}
receipt = {'model':'MobileSAM vit_t', 'checkpoint':'.tmp-work/warehouse-segmentation-model/weights/mobile_sam.pt', 'device':'cpu', 'formats':{}}
for format, regions in prompts.items():
 source = root / f'public/scene-art/barge-family-v1/choice-neutral-{format}-v3.webp'
 rgb = np.array(Image.open(source).convert('RGB'))
 h, w = rgb.shape[:2]
 predictor.set_image(rgb)
 result[format] = {'source':str(source.relative_to(root)), 'width':w, 'height':h, 'regions':{}}
 receipt['formats'][format] = {}
 combined = rgb.copy()
 for key, prompt in regions.items():
  with torch.no_grad():
   masks,scores,_ = predictor.predict(point_coords=np.array(prompt['points']), point_labels=np.ones(len(prompt['points'])), box=np.array(prompt['box']), multimask_output=True)
  index = int(np.argmax(scores))
  mask = masks[index].astype(np.uint8) * 255
  Image.fromarray(mask).save(out / 'masks' / f'{format}-{key}.png')
  cs,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  paths=[]
  for contour in cs:
   if cv2.contourArea(contour) < 80: continue
   poly = cv2.approxPolyDP(contour, 1.25, True).reshape(-1,2)
   paths.append('M' + ' L'.join(f'{x},{y}' for x,y in poly) + ' Z')
  if not paths: raise RuntimeError(f'No usable contours: {format}/{key}')
  result[format]['regions'][key] = {'path':' '.join(paths)}
  combined[mask > 0] = (combined[mask > 0] * .65 + np.array([255,100,0]) * .35).astype(np.uint8)
  overlay = rgb.copy()
  overlay[mask > 0] = (overlay[mask > 0] * .45 + np.array([0,170,210]) * .55).astype(np.uint8)
  Image.fromarray(overlay).save(out / 'masks' / f'{format}-{key}-review.png')
  receipt['formats'][format][key] = {**prompt,'selectedCandidate':index,'predictedIoU':float(scores[index]),'contours':len(paths)}
  print(format,key,float(scores[index]),len(paths),flush=True)
 Image.fromarray(combined).save(out / 'masks' / f'{format}-combined.png')
(root / 'src/scenes/crane/segmentedContours.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
(out / 'segmentation-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
