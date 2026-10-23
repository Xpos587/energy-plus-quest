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
  'helicopter': {'box':[925,30,1170,190], 'points':[[1042,138],[1073,96],[1040,110],[1110,173],[980,160]], 'labels':[1,1,1,0,0]},
  'pipe-carrier': {'box':[550,425,865,670], 'points':[[635,581],[735,516],[784,600]]},
  'rover': {'box':[850,480,1082,675], 'points':[[925,582],[1015,549],[995,626]]},
  'robot': {'box':[1120,610,1250,718], 'points':[[1185,662],[1150,681],[1220,682]]},
 },
 'tall': {
  'helicopter': {'box':[328,420,510,555], 'points':[[408,515],[450,500],[414,488],[489,543],[338,538]], 'labels':[1,1,1,0,0]},
  'pipe-carrier': {'box':[120,780,320,935], 'points':[[180,876],[253,823],[270,886]]},
  'rover': {'box':[313,795,472,935], 'points':[[354,874],[415,839],[426,880]]},
  'robot': {'box':[490,880,585,962], 'points':[[530,922],[550,922],[518,941]]},
 },
}
result = {}
receipt = {'model':'MobileSAM vit_t', 'checkpoint':'.tmp-work/warehouse-segmentation-model/weights/mobile_sam.pt', 'device':'cpu', 'formats':{}}
for format, regions in prompts.items():
 source = root / f'public/scene-art/lastmile-family-v1/choice-final-{format}-v9.webp'
 rgb = np.array(Image.open(source).convert('RGB'))
 h, w = rgb.shape[:2]
 predictor.set_image(rgb)
 result[format] = {'source':str(source.relative_to(root)), 'width':w, 'height':h, 'regions':{}}
 receipt['formats'][format] = {}
 combined = rgb.copy()
 for key, prompt in regions.items():
  with torch.no_grad():
   masks,scores,_ = predictor.predict(point_coords=np.array(prompt['points']), point_labels=np.array(prompt.get('labels',[1]*len(prompt['points']))), box=np.array(prompt['box']), multimask_output=True)
  if key == 'helicopter':
   for ci, candidate in enumerate(masks):
    debug=rgb.copy();debug[candidate]=(debug[candidate]*.45+np.array([0,170,210])*.55).astype(np.uint8);Image.fromarray(debug).save(out/'masks'/f'{format}-helicopter-candidate-{ci}.png')
   print(format,'helicopter candidates',scores,flush=True)
  index = 0 if key == 'helicopter' else int(np.argmax(scores))
  mask = masks[index].astype(np.uint8) * 255
  if key == 'helicopter':
   count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
   mask = (labels == (1 + int(np.argmax(stats[1:,cv2.CC_STAT_AREA])))).astype(np.uint8)*255
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
(root / 'src/scenes/lastmile/segmentedContours.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
(out / 'segmentation-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
