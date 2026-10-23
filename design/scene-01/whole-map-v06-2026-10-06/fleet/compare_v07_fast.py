from PIL import Image
import numpy as np,json
from pathlib import Path
O=Path(__file__).resolve().parent;records=[]
for f in (1,385):
 a=np.array(Image.open(O/f'textured-v07-vehicles-{f:04}.png').convert('RGBA'),dtype=np.float32)/255
 b=np.array(Image.open(O/f'textured-v07-fast-{f:04}.png').convert('RGBA'),dtype=np.float32)/255
 aa=a[:,:,3];ba=b[:,:,3];union=(aa>0)|(ba>0)
 alpha=np.abs(aa-ba);color=np.abs(a[:,:,:3]*aa[:,:,None]-b[:,:,:3]*ba[:,:,None])
 new=(ba>.02)&(aa<.02);lost=(aa>.02)&(ba<.02)
 records.append({'frame':f,'normal_visible_alpha_pixels':int((aa>.02).sum()),'fast_visible_alpha_pixels':int((ba>.02).sum()),'new_visible_pixels_when_city_hidden':int(new.sum()),'lost_visible_pixels_when_city_hidden':int(lost.sum()),'alpha_changed_pixels_gt_2_255':int((alpha>2/255).sum()),'alpha_max_delta_0_to_1':float(alpha.max()),'premultiplied_rgb_mean_abs_delta_on_union_0_to_1':float(color[union].mean()),'premultiplied_rgb_max_delta_0_to_1':float(color.max())})
 if new.any():
  ys,xs=np.where(new);Image.fromarray(np.uint8(b*255)).crop((int(xs.min())-5,int(ys.min())-5,int(xs.max())+6,int(ys.max())+6)).save(O/f'fast-occlusion-difference-{f:04}.png')
(O/'textured-v07-fast-comparison.json').write_text(json.dumps({'records':records,'scope':'Two pilot frames only; no all-timeline occlusion guarantee'},indent=2));print(json.dumps(records))
