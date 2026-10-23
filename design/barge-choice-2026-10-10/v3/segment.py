from pathlib import Path
import sys, json
import numpy as np
import cv2
import torch
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root / '.tmp-work/warehouse-segmentation-model'))
from mobile_sam import sam_model_registry, SamPredictor

out = Path(__file__).parent
(out / 'masks').mkdir(exist_ok=True)
model = sam_model_registry['vit_t'](checkpoint=str(root / '.tmp-work/warehouse-segmentation-model/weights/mobile_sam.pt')).to('cpu').eval()
torch.set_num_threads(4)
predictor = SamPredictor(model)
prompts = {
 'wide': {
  'crane': {'box':[975,35,1420,600], 'points':[[1100,360],[1200,250],[1180,470],[1290,98]]},
  'petr': {'box':[1510,0,1750,365], 'points':[[1600,200],[1640,270],[1700,100]]},
  'remote': {'box':[50,200,385,540], 'points':[[215,350],[230,470],[190,260]]},
 },
 'tall': {
  'crane': {'box':[550,65,965,700], 'points':[[660,470],[775,270],[680,555],[850,115]]},
  'petr': {'box':[930,90,1070,365], 'points':[[975,253],[1000,290],[1020,150]]},
  'remote': {'box':[0,440,435,1140], 'points':[[180,680],[140,870],[270,540]]},
 },
}
result = {}
receipt = {'model':'MobileSAM vit_t', 'checkpoint':'.tmp-work/warehouse-segmentation-model/weights/mobile_sam.pt', 'device':'cpu', 'formats':{}}
for format, regions in prompts.items():
 source = root / f'public/scene-art/barge-family-v1/choice-neutral-{format}-v5.webp'
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
