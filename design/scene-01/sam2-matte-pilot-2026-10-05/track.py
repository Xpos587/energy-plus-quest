import os,time,json
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_PROGRESS_BARS']='1'
import torch,numpy as np,transformers
from PIL import Image
from transformers import Sam2VideoModel,Sam2VideoProcessor
from pathlib import Path
p=Path(__file__).resolve().parent;start=time.monotonic();torch.set_num_threads(4);cache='/home/michael/.cache/huggingface/hub/models--facebook--sam2.1-hiera-tiny/snapshots/de431c4043854a71d8101e17995dfe596bf101a5';crop=(730,155,1045,640)
files=sorted((p/'video-source').glob('*.png'));sources=[Image.open(f).convert('RGB') for f in files];frames=[x.crop(crop) for x in sources];model=Sam2VideoModel.from_pretrained(cache,local_files_only=True).to('cuda').eval();processor=Sam2VideoProcessor.from_pretrained(cache,local_files_only=True)
session=processor.init_video_session(video=frames,inference_device='cuda',inference_state_device='cpu',processing_device='cpu',video_storage_device='cpu',max_vision_features_cache_size=1,dtype=torch.float16)
anchors=json.loads((p/'pilot-receipt.json').read_text())['frames'];areas={};ious={}
with torch.inference_mode(),torch.autocast('cuda',dtype=torch.float16):
 for r in anchors:
  f=r['frame'];pts=[[x-crop[0],y-crop[1]] for x,y in r['positive_points']+r['negative_points']];labels=[1]*len(r['positive_points'])+[0]*len(r['negative_points']);b=r['box'];box=[b[0]-crop[0],b[1]-crop[1],b[2]-crop[0],b[3]-crop[1]]
  processor.add_inputs_to_inference_session(session,frame_idx=f,obj_ids=1,input_points=[[pts]],input_labels=[[labels]],input_boxes=[[box]])
  model(inference_session=session,frame_idx=f)
 for out in model.propagate_in_video_iterator(session,start_frame_idx=0,max_frame_num_to_track=len(files),show_progress_bar=False):
  f=out.frame_idx;m=processor.post_process_masks([out.pred_masks.cpu()],original_sizes=[[crop[3]-crop[1],crop[2]-crop[0]]])[0][0,0].numpy().astype(np.uint8)*255
  full=Image.new('L',(1280,720));full.paste(Image.fromarray(m),(crop[0],crop[1]));rgba=sources[f].copy();rgba.putalpha(full);rgba.save(p/'video-layers'/f'{f:04}.png');areas[str(f)]=int(np.count_nonzero(m))
  assert np.array_equal(np.array(rgba)[...,:3],np.array(sources[f]))
  if f in (0,12,30,60,90,120):
   a=np.array(full)>0;b=np.array(Image.open(p/f'matte-{f:03}.png'))>0;ious[str(f)]=float(np.count_nonzero(a&b)/np.count_nonzero(a|b))
   yy,xx=np.indices((720,1280));check=np.where(((xx//12+yy//12)%2)[...,None],np.array([224,230,233]),np.array([166,177,184])).astype(np.uint8);im=Image.fromarray(check);im.paste(sources[f],(0,0),full);im.save(p/f'tracked-checker-{f:03}.png')
  if f%24==0:print('FRAME',f,'elapsed',round(time.monotonic()-start,3),flush=True)
r={'model':'facebook/sam2.1-hiera-tiny','runtime':transformers.__version__,'source':'../kling-fleet-corners-2026-10-05/red-3-0.mp4','native_dimensions':[1280,720],'frames':len(areas),'required_frames':len(files),'fps':24,'crop':crop,'rgba_directory':'video-layers','alpha_threshold':0.0,'source_rgb_exactly_retained_all_frames':True,'six_corrective_point_box_anchors':[0,12,30,60,90,120],'anchor_iou_to_still_pilot':ious,'mask_pixel_counts':areas,'elapsed_seconds':round(time.monotonic()-start,3),'peak_cuda_memory_mib':round(torch.cuda.max_memory_allocated()/1024**2,1),'cpu_video_and_state_offload':True,'review_pass_claimed':False,'docs':'https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/sam2_video.md'};(p/'tracking-receipt.json').write_text(json.dumps(r,indent=2));print('TRACKED',r['frames'],r['elapsed_seconds'],flush=True)
