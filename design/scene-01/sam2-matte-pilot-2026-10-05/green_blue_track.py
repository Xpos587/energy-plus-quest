import os,time,json,subprocess,gc
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_PROGRESS_BARS']='1'
import torch,numpy as np,transformers
from PIL import Image,ImageDraw
from transformers import Sam2VideoModel,Sam2VideoProcessor
from pathlib import Path
p=Path(__file__).resolve().parent;src=p.parent/'kling-fleet-corners-2026-10-05';torch.set_num_threads(4);start=time.monotonic();cache='/home/michael/.cache/huggingface/hub/models--facebook--sam2.1-hiera-tiny/snapshots/de431c4043854a71d8101e17995dfe596bf101a5';model=Sam2VideoModel.from_pretrained(cache,local_files_only=True).to('cuda').eval();processor=Sam2VideoProcessor.from_pretrained(cache,local_files_only=True)
# Coordinates verified on actual provider first frames. Crops cover the full route segment, not merely initial rig.
specs={'green-1': {'crop': [625, 30, 1045, 350], 'box': [955, 196, 993, 311], 'pos': [[978, 208], [975, 255], [968, 303]], 'neg': [[1006, 245], [947, 255], [978, 322]]}, 'green-2a': {'crop': [375, 35, 815, 270], 'box': [539, 89, 780, 174], 'pos': [[567, 121], [650, 125], [563, 157], [735, 161]], 'neg': [[655, 76], [635, 184], [524, 132]]}, 'green-2b': {'crop': [360, 30, 725, 680], 'box': [409, 60, 687, 220], 'pos': [[454, 164], [570, 127], [460, 208], [640, 149]], 'neg': [[575, 52], [697, 121], [499, 239]]}, 'green-3': {'crop': [610, 205, 930, 635], 'box': [650, 242, 694, 348], 'pos': [[670, 321], [674, 280], [665, 340]], 'neg': [[637, 280], [700, 315], [677, 360]]}, 'green-4': {'crop': [730, 155, 1045, 640], 'box': [775, 550, 894, 597], 'pos': [[878, 575], [820, 569], [792, 585], [850, 585]], 'neg': [[814, 542], [902, 576], [798, 607]]}, 'blue-0': {'crop': [375, 220, 640, 625], 'box': [395, 253, 433, 370], 'pos': [[410, 345], [415, 300], [404, 362]], 'neg': [[390, 320], [445, 335], [413, 380]]}, 'blue-1': {'crop': [410, 235, 755, 625], 'box': [433, 515, 556, 593], 'pos': [[536, 570], [482, 544], [455, 552], [515, 580]], 'neg': [[472, 505], [565, 559], [519, 603]]}, 'blue-2': {'crop': [430, 55, 760, 415], 'box': [691, 274, 719, 383], 'pos': [[706, 289], [702, 338], [696, 374]], 'neg': [[729, 350], [681, 315], [700, 394]]}, 'blue-3': {'crop': [370, 50, 630, 405], 'box': [478, 87, 594, 135], 'pos': [[493, 110], [550, 107], [571, 122]], 'neg': [[553, 79], [606, 113], [474, 143]]}}
empty=Image.open(p.parent/'four-truck-loop-2026-10-04/v2b-empty-map.png').convert('RGB')
yy,xx=np.indices((720,1280));checker=Image.fromarray(np.where(((xx//12+yy//12)%2)[...,None],np.array([224,230,233]),np.array([166,177,184])).astype(np.uint8));all_receipts=[]
paths=json.loads((p/'green-blue-sources.json').read_text())
for name in specs:
 if (p/'STOP_GREEN_BLUE').exists():break
 for _ in range(1):
  seg=name;q=p/name;(q/'source').mkdir(exist_ok=True);(q/'layers').mkdir(exist_ok=True);t=time.monotonic();spec=specs[seg];crop=spec['crop'];print('START',name,flush=True)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',paths[name],str(q/'source'/'%04d.png')],check=True)
  files=sorted((q/'source').glob('*.png'));sources=[Image.open(f).convert('RGB') for f in files];frames=[x.crop(crop) for x in sources];session=processor.init_video_session(video=frames,inference_device='cuda',inference_state_device='cpu',processing_device='cpu',video_storage_device='cpu',max_vision_features_cache_size=1,dtype=torch.float16)
  pts=[[x-crop[0],y-crop[1]] for x,y in spec['pos']+spec['neg']];labels=[1]*len(spec['pos'])+[0]*len(spec['neg']);b=spec['box'];box=[b[0]-crop[0],b[1]-crop[1],b[2]-crop[0],b[3]-crop[1]];processor.add_inputs_to_inference_session(session,frame_idx=0,obj_ids=1,input_points=[[pts]],input_labels=[[labels]],input_boxes=[[box]])
  bg=Image.new('RGB',(1280,720),'white')
  if name in ['green-2a','green-2b']:bg.paste(empty.crop((700,100,1120,560)).resize((658,720),Image.Resampling.LANCZOS),(311,0))
  else:bg.paste(empty.resize((1038,720),Image.Resampling.LANCZOS),(121,0))
  panels=[];areas={};bboxes={}
  with torch.inference_mode(),torch.autocast('cuda',dtype=torch.float16):
   model(inference_session=session,frame_idx=0)
   for out in model.propagate_in_video_iterator(session,start_frame_idx=0,max_frame_num_to_track=len(files),show_progress_bar=False):
    f=out.frame_idx;m=processor.post_process_masks([out.pred_masks.cpu()],original_sizes=[[crop[3]-crop[1],crop[2]-crop[0]]])[0][0,0].numpy().astype(np.uint8)*255;mask=Image.new('L',(1280,720));mask.paste(Image.fromarray(m),(crop[0],crop[1]));layer=sources[f].copy();layer.putalpha(mask);layer.save(q/'layers'/f'{f:04}.png');assert np.array_equal(np.array(layer)[...,:3],np.array(sources[f]));areas[str(f)]=int(np.count_nonzero(m));bbox=mask.getbbox();bboxes[str(f)]=bbox
    if f%6==0:
     if bbox is None:bbox=spec['box']
     b0=max(0,bbox[0]-12);b1=max(0,bbox[1]-12);b2=min(1280,bbox[2]+12);b3=min(720,bbox[3]+12);bb=(b0,b1,b2,b3)
     check=checker.copy();check.paste(sources[f],(0,0),mask);composite=bg.copy();composite.paste(sources[f],(0,0),mask)
     row=Image.new('RGB',(960,310),'white');d=ImageDraw.Draw(row)
     for c,(kind,image) in enumerate([('source',sources[f]),('checker',check),('composite',composite)]):row.paste(image.crop(bb),(c*320,25));d.text((c*320+4,5),f'{name} {kind} frame {f} / {f/24:.2f}s',fill='black')
     panels.append(row)
  for group in range(3):
   sheet=Image.new('RGB',(960,7*310),'white')
   for j,row in enumerate(panels[group*7:(group+1)*7]):sheet.paste(row,(0,j*310))
   sheet.save(q/f'native-quarter-contact-{group+1}.png')
  r={'name':name,'source':paths[name],'frames':len(areas),'required_frames':121,'rgba':'layers/%04d.png','indexing':'zero-based','dimensions':[1280,720],'fps':24,'source_rgb_exactly_retained':True,'model':'facebook/sam2.1-hiera-tiny','runtime':transformers.__version__,'prompt':spec,'initial_anchor_only':True,'alpha_threshold':0.0,'elapsed_seconds':round(time.monotonic()-t,3),'areas':areas,'bboxes':bboxes,'contacts':[f'native-quarter-contact-{i}.png' for i in (1,2,3)],'review_pass_claimed':False};(q/'receipt.json').write_text(json.dumps(r,indent=2));all_receipts.append({k:r[k] for k in ['name','frames','elapsed_seconds','rgba','initial_anchor_only']});(p/'green-blue-progress.json').write_text(json.dumps(all_receipts,indent=2));print('END',name,len(areas),r['elapsed_seconds'],flush=True);del session,sources,frames;gc.collect();torch.cuda.empty_cache()
(p/'green-blue-receipt.json').write_text(json.dumps({'clips':all_receipts,'elapsed_seconds':round(time.monotonic()-start,3),'review_pass_claimed':False},indent=2));print('BATCH END',flush=True)
