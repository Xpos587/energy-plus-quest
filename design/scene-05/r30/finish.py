"""Finish the two accepted paintings; derive silhouettes from the paint, using Blender ID box prompts."""
import json, sys
from pathlib import Path
import cv2, numpy as np, torch
from PIL import Image
from spandrel import ModelLoader
from transformers import SamModel, SamProcessor

work=Path(sys.argv[1]); plates=work/'paint'; render=work/'locked'
keys=('helicopter','rover','pipe_carrier','robot','barge'); views=('tall','wide')
palette=json.loads((render/'palette.json').read_text())
model=Path.home()/'.local/share/comfyui/ComfyUI/models/upscale_models/RealESRGAN_x4plus_anime_6B.pth'

@torch.inference_mode()
def upscale():
    net=ModelLoader().load_from_file(str(model)).model.cuda().eval().half()
    for view in views:
        im=Image.open(plates/f'{view}-1.png').convert('RGB'); target=Image.open(render/f'{view}-id.png').size
        a=np.asarray(im); height,width=a.shape[:2]; big=Image.new('RGB',(4*width,4*height))
        for y in range(0,height,240):
            for x in range(0,width,240):
                l,t=max(0,x-16),max(0,y-16); r,b=min(width,x+256),min(height,y+256)
                ten=torch.from_numpy(a[t:b,l:r].copy()).permute(2,0,1)[None].cuda().half()/255
                out=(net(ten)[0].clamp(0,1)*255).round().byte().permute(1,2,0).cpu().numpy()
                part=Image.fromarray(out).crop(((x-l)*4,(y-t)*4,(min(x+240,width)-l)*4,(min(y+240,height)-t)*4));big.paste(part,(x*4,y*4))
        big.resize(target,Image.Resampling.LANCZOS).save(plates/f'{view}-master.png');print('master',view,flush=True)

@torch.inference_mode()
def segment():
    processor=SamProcessor.from_pretrained('facebook/sam-vit-huge',local_files_only=True)
    sam=SamModel.from_pretrained('facebook/sam-vit-huge',local_files_only=True,dtype=torch.float16).to('cuda').eval()
    for view in views:
        im=Image.open(plates/f'{view}-master.png').convert('RGB'); ids=np.array(Image.open(render/f'{view}-id.png')); W,H=im.size; masks={}
        for key in keys:
            guide=np.all(ids==palette[key],axis=2).astype('uint8'); x,y,w,h=cv2.boundingRect(guide)
            pad=65; l,t=max(0,x-pad),max(0,y-pad); r,b=min(W,x+w+pad),min(H,y+h+pad)
            box=[x-l-8,y-t-7,x+w-l+(28 if key in ('helicopter','rover','pipe_carrier') else 8),y+h-t+12]
            inp=processor(im.crop((l,t,r,b)),input_boxes=[[box]],return_tensors='pt').to('cuda');inp['pixel_values']=inp['pixel_values'].half()
            out=sam(**inp,multimask_output=True); candidates=processor.image_processor.post_process_masks(out.pred_masks.float().cpu(),inp['original_sizes'].cpu(),inp['reshaped_input_sizes'].cpu())[0][0].numpy()
            ref=guide[t:b,l:r]; scores=[(m & ref).sum()/(m | ref).sum() for m in candidates]; mask=candidates[int(np.argmax(scores))].astype('uint8'); _,lab,st,_=cv2.connectedComponentsWithStats(mask); mask=(lab==1+np.argmax(st[1:,4])).astype('uint8'); full=np.zeros((H,W),'uint8'); full[t:b,l:r]=mask;masks[key]=full
            print(view,key,'IoU against 3D',round(max(scores),3),'paint box',cv2.boundingRect(full),flush=True)
        np.savez_compressed(plates/f'{view}-masks.npz',**masks)

if sys.argv[-1]!='segment': upscale(); torch.cuda.empty_cache()
segment()
