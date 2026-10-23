import os,time,json
os.environ['HF_HUB_OFFLINE']='1'
import torch,transformers,numpy as np
from PIL import Image
from transformers import Sam2Model,Sam2Processor
from pathlib import Path
p=Path(__file__).resolve().parent;start=time.monotonic();torch.set_num_threads(4)
cache='/home/michael/.cache/huggingface/hub/models--facebook--sam2.1-hiera-tiny/snapshots/de431c4043854a71d8101e17995dfe596bf101a5'
model=Sam2Model.from_pretrained(cache,local_files_only=True).to('cuda').eval();processor=Sam2Processor.from_pretrained(cache,local_files_only=True);load=time.monotonic()-start
specs=[(0,[776,552,895,595],[[882,575],[821,570],[791,585],[854,585]],[[810,542],[758,593],[901,575]]),(12,[810,551,929,594],[[912,568],[855,567],[829,583],[889,583]],[[850,543],[940,570],[809,600]]),(30,[857,517,958,588],[[944,533],[907,558],[878,578],[924,568]],[[899,505],[970,552],[886,600]]),(60,[925,431,973,536],[[956,443],[948,482],[938,525]],[[983,486],[918,481],[962,549]]),(90,[944,319,981,432],[[966,331],[961,380],[952,424]],[[991,368],[932,385],[957,442]]),(120,[955,200,993,315],[[979,213],[975,257],[966,307]],[[1004,245],[944,260],[973,325]])]
rows=[]
bg=Image.open(p.parent/'four-truck-loop-2026-10-04/v2b-empty-map.png').convert('RGB');bg=bg.resize((1038,720),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(1280,720),'white');canvas.paste(bg,(121,0))
for index,(frame,box,pos,neg) in enumerate(specs,1):
 source=Image.open(p/f'source-{index:02}.png').convert('RGB');x0=max(0,box[0]-45);y0=max(0,box[1]-45);x1=min(1280,box[2]+45);y1=min(720,box[3]+45);crop=source.crop((x0,y0,x1,y1));coords=[[x-x0,y-y0] for x,y in pos+neg];labels=[1]*len(pos)+[0]*len(neg);cb=[box[0]-x0,box[1]-y0,box[2]-x0,box[3]-y0]
 inputs=processor(images=crop,input_points=[[coords]],input_labels=[[labels]],input_boxes=[[cb]],return_tensors='pt').to('cuda');t=time.monotonic()
 with torch.inference_mode(),torch.autocast('cuda',dtype=torch.float16):out=model(**inputs,multimask_output=False)
 masks=processor.post_process_masks(out.pred_masks.cpu(),inputs['original_sizes'].cpu())[0];local=masks[0,0].numpy().astype(np.uint8)*255;mask=Image.new('L',source.size);mask.paste(Image.fromarray(local),(x0,y0));rgba=source.copy();rgba.putalpha(mask);rgba.save(p/f'layer-{frame:03}.png');mask.save(p/f'matte-{frame:03}.png')
 yy,xx=np.indices((720,1280));checker=np.where(((xx//12+yy//12)%2)[...,None],np.array([224,230,233]),np.array([166,177,184])).astype(np.uint8);check=Image.fromarray(checker);check.paste(source,(0,0),mask);check.save(p/f'checker-{frame:03}.png');composite=canvas.copy();composite.paste(source,(0,0),mask);composite.save(p/f'composite-{frame:03}.png')
 # Preserve full native RGB bytes; only alpha differs.
 assert np.array_equal(np.array(rgba)[...,:3],np.array(source))
 row={'frame':frame,'crop':[x0,y0,x1,y1],'box':box,'positive_points':pos,'negative_points':neg,'mask_pixels':int(np.count_nonzero(local)),'inference_seconds':round(time.monotonic()-t,3),'score':float(out.iou_scores[0,0,0]),'rgb_retained_exactly':True};rows.append(row);print(row,flush=True)
receipt={'model':'facebook/sam2.1-hiera-tiny','cached_snapshot':cache,'runtime':{'torch':torch.__version__,'transformers':transformers.__version__,'device':torch.cuda.get_device_name(),'autocast':'float16'},'load_seconds':round(load,3),'elapsed_seconds':round(time.monotonic()-start,3),'frames':rows,'docs':'https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/sam2.md','review_pass_claimed':False};(p/'pilot-receipt.json').write_text(json.dumps(receipt,indent=2))
