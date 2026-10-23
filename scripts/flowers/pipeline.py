"""Resumable two-pass Flowers. Generation remains explicit built-in image_gen calls.
No source hashes, byte-size metrics, synthetic success or automatic runtime promotion.
"""
import argparse,importlib.util,json,os,shutil,sys,fcntl,subprocess
from pathlib import Path
import cv2,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'docs/reviews/flowers-all-2026-10-20/manifest.json'
OLD=Path(__file__).with_name('registration.py')
spec=importlib.util.spec_from_file_location('prior_flowers_registration',OLD);prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
def save_job(root,job):
 root=Path(root);tmp=root/'job.next.json';tmp.write_text(json.dumps(job,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,root/'job.json')
def load_job(root):return json.loads((Path(root)/'job.json').read_text())
def master_size(job):
 w,h=job['sourceDimensions'];scale=job['exportLongestEdge']/max(w,h);return round(w*scale),round(h*scale)
def prepare_job(root,source,ident,freeze_receipt):
 root=Path(root)
 if (root/'job.json').exists():return load_job(root)
 if not freeze_receipt:raise ValueError('Explicit owner freeze receipt required')
 root.mkdir(parents=True,exist_ok=True);original=Image.open(source);has_alpha='A'in original.getbands();im=original.convert('RGBA'if has_alpha else'RGB');im.save(root/'source.png');w,h=im.size
 if has_alpha:im.getchannel('A').save(root/'source-alpha.png')
 job={'schemaVersion':1,'id':ident,'source':str(source),'freezeReceipt':str(freeze_receipt),'sourceDimensions':[w,h],'sourceHasAlpha':has_alpha,'passes':2,'exportLongestEdge':8192,'status':'p1_prepared','protection':{'status':'owner_review_required'},'tiles':[],'rois':[]}
 for y in range(3):
  for x in range(3):
   core=[w*x//3,h*y//3,w*(x+1)//3,h*(y+1)//3];px=round((core[2]-core[0])*.2);py=round((core[3]-core[1])*.2);box=[max(0,core[0]-px),max(0,core[1]-py),min(w,core[2]+px),min(h,core[3]+py)];tid=f'p1-{y}{x}'
   im.crop(box).save(root/f'{tid}-source.png');prompt=f'Flowers high-detail reconstruction, pass 1. Full source S is authoritative scene context. Reconstruct fine details only inside the supplied padded tile {tid}; preserve camera, silhouettes, identity, materials, object count, lettering and exact composition. Do not add objects or move edges. Return only this tile, no labels, no grid. Its bounds in S are {box}; S dimensions {w}x{h}. Preserve existing transparency separately if applicable. This is an illustration, retain its existing style. The assembled master will have longest edge8192; do not claim native full-scene8192. Use source S plus this tile as image references.'
   (root/f'{tid}-prompt.txt').write_text(prompt);job['tiles'].append({'id':tid,'pass':1,'core':core,'box':box,'reference':f'{tid}-source.png','referencePixelsPerSourcePixel':1.0,'status':'pending','attempts':[]})
 save_job(root,job);return job

def record(root,tile_id,candidate,prompt=None,tool_receipt=None):
 root=Path(root);job=load_job(root);tile=next(t for t in job['tiles']+job['rois'] if t['id']==tile_id)
 if tile['status']in['accepted','retained']:raise ValueError('Already resolved; refusing duplicate candidate registration')
 if len(tile['attempts'])>=3:raise ValueError('Maximum three native attempts (first plus two retries) reached; owner must retain/disclose')
 candidate=Path(candidate);ref=cv2.imread(str(root/tile['reference']));gen=cv2.imread(str(candidate))
 if ref is None or gen is None:raise ValueError('Input image failed decode')
 attempt=len(tile['attempts'])+1;output=root/f'{tile_id}-attempt-{attempt}-native.png';Image.open(candidate).save(output)
 if prompt:shutil.copyfile(prompt,root/f'{tile_id}-attempt-{attempt}-prompt.txt')
 if tool_receipt:shutil.copyfile(tool_receipt,root/f'{tile_id}-attempt-{attempt}-tool-receipt.json')
 try:matrix,metric=prior.register(ref,gen,tile['referencePixelsPerSourcePixel'])
 except (TypeError,ValueError,cv2.error) as e:matrix=None;metric={'accepted':False,'reason':'registration failed: '+str(e)}
 metric.update(candidate=str(output.name),nativeGeneratedDimensions=[gen.shape[1],gen.shape[0]],referenceDimensions=[ref.shape[1],ref.shape[0]],tileId=tile_id,attempt=attempt)
 if matrix is not None:metric['affineGeneratedToReference']=matrix.tolist()
 (root/f'{tile_id}-attempt-{attempt}-registration.json').write_text(json.dumps(metric,indent=2)+'\n');tile['attempts'].append(metric);tile['status']='accepted'if metric['accepted']else'rejected';job['status']=f"p{tile['pass']}_in_progress";save_job(root,job);return metric

def retain(root,tile_id,reason,owner_receipt):
 root=Path(root);job=load_job(root);tile=next(t for t in job['tiles']+job['rois']if t['id']==tile_id)
 if tile['status']!='rejected'or not tile['attempts']:raise ValueError('Retention requires a real rejected candidate, not skipped generation')
 if not reason or not owner_receipt:raise ValueError('Explicit reason and owner receipt required')
 tile['status']='retained';tile['retention']={'reason':reason,'ownerReceipt':str(owner_receipt),'nativeReconstructionAccepted':False,'retains':'original source pixels for P1; accepted P1 pixels for P2'};save_job(root,job);return tile

def visual_reject(root,tile_id,reason,owner_receipt):
 root=Path(root);job=load_job(root);tile=next(t for t in job['tiles']+job['rois']if t['id']==tile_id)
 if tile['status']!='accepted'or not tile['attempts']:raise ValueError('Visual rejection requires a numerically accepted native candidate')
 if not reason or not owner_receipt:raise ValueError('Explicit visual reason and owner receipt required')
 if tile['pass']==1 and job['rois']:raise ValueError('P2 already references P1; append P2 repair ROIs or create a new P1 revision rather than invalidate accepted P2')
 tile.setdefault('visualReviews',[]).append({'decision':'rejected','reason':reason,'ownerReceipt':str(owner_receipt),'attempt':len(tile['attempts']),'numericRegistrationPreserved':True});tile['status']='rejected';job['status']=f"p{tile['pass']}_in_progress";save_job(root,job);return tile

def set_protection(root,mask,receipt):
 root=Path(root);job=load_job(root);im=Image.open(mask).convert('L')
 if list(im.size)!=job['sourceDimensions']:raise ValueError('Protection mask must use original source dimensions')
 number=2 if job['rois'] else 1;revision=job.get('protection',{}).get('revision',0)+1;name=f'protection-p{number}-r{revision}.png';im.save(root/name);job['protection']={'status':'owner_approved','mask':name,'receipt':str(receipt),'revision':revision,'pass':number};job.setdefault('passProtection',{})[str(number)]=dict(job['protection']);save_job(root,job)

def set_rois(root,roi_file,append=False):
 root=Path(root);job=load_job(root)
 if not(root/'pass1-master.png').exists():raise ValueError('Accepted assembled pass1 required before pass2')
 if job['rois']and not append:raise ValueError('ROIs already prepared; use explicit --append for new repair IDs, never reset accepted work')
 data=json.loads(Path(roi_file).read_text());rois=data['rois']if isinstance(data,dict)else data
 if not rois:raise ValueError('At least one meaningful owner-selected ROI required')
 incoming=[r.get('id',f'p2-{n:02d}')for n,r in enumerate(rois)];existing={r['id']for r in job['rois']}
 if len(set(incoming))!=len(incoming)or any(i in existing for i in incoming):raise ValueError('ROI IDs must be new and unique; accepted work cannot be overwritten')
 master=Image.open(root/'pass1-master.png');w,h=job['sourceDimensions'];sx=master.width/w;sy=master.height/h
 for n,r in enumerate(rois):
  ident=r.get('id',f'p2-{n:02d}');box=r['sourceBox'];l,t,rr,b=box
  if not(0<=l<rr<=w and 0<=t<b<=h):raise ValueError('ROI sourceBox out of bounds')
  mb=[round(l*sx),round(t*sy),round(rr*sx),round(b*sy)];ref=f'{ident}-source.png';master.crop(mb).save(root/ref);job['rois'].append({'id':ident,'pass':2,'box':mb,'sourceBox':box,'reference':ref,'referencePixelsPerSourcePixel':sx,'status':'pending','attempts':[],'purpose':r.get('purpose','owner-selected salient detail')});(root/f'{ident}-prompt.txt').write_text('Flowers pass2: reconstruct only this salient padded crop using original full scene S as authoritative context and this accepted P1 crop. Keep exact geometry, silhouette, identity, object count, lettering, materials and style. No new objects. Return only the supplied crop, no collage or labels. Purpose: '+r.get('purpose','salient detail'))
 job['roiRevision']=job.get('roiRevision',0)+1;job['status']='p2_prepared';save_job(root,job);return job

def assemble(root,pass_number):
 root=Path(root);job=load_job(root);tiles=job['tiles']if pass_number==1 else job['rois']
 if not tiles or any(t['status']not in['accepted','retained']for t in tiles):raise ValueError('All requested tiles must be accepted or explicitly retained after rejection; fallback never counts as processed')
 protection=job.get('passProtection',{}).get(str(pass_number),job['protection'])
 if protection['status']!='owner_approved':raise ValueError('Owner-approved source-space protection mask required (explicit empty mask is allowed)')
 source=cv2.imread(str(root/'source.png'));h,w=source.shape[:2];W,H=master_size(job)
 base=cv2.resize(source,(W,H),interpolation=cv2.INTER_LANCZOS4);out=base.copy()if pass_number==1 else cv2.imread(str(root/'pass1-master.png'))
 if out is None:raise ValueError('Missing pass1 master')
 rows=[]
 for tile in tiles:
  if tile['status']=='retained':rows.append({'id':tile['id'],'accepted':False,'retention':tile['retention'],'attempts':tile['attempts']});continue
  receipt=tile['attempts'][-1];gen=cv2.imread(str(root/receipt['candidate']));M=np.array(receipt['affineGeneratedToReference'],np.float64)
  reference_dimensions=receipt.get('referenceDimensions')
  if reference_dimensions is None:
   with Image.open(root/tile['reference'])as reference:reference_dimensions=list(reference.size)
  guard=prior.geometry_guard(M,reference_dimensions,[gen.shape[1],gen.shape[0]])
  if not guard['accepted']:raise ValueError(f"Invalid registration geometry for {tile['id']}: {guard['failures']}")
  spatial_guard=receipt.get('geometryGuard')
  if spatial_guard is None:
   reference=cv2.imread(str(root/tile['reference']));_,revalidated=prior.register(reference,gen,tile['referencePixelsPerSourcePixel']);spatial_guard=revalidated.get('geometryGuard',{'accepted':False})
  if not spatial_guard['accepted']:raise ValueError(f"Invalid registration spatial support for {tile['id']}")
  if pass_number==1:
   l,t,r,b=tile['box'];target=[round(l*W/w),round(t*H/h),round(r*W/w),round(b*H/h)];matrix=M.copy();matrix[0]*=W/w;matrix[1]*=H/h
  else:target=tile['box'];matrix=M
  l,t,r,b=target;tw,th=r-l,b-t
  small_matrix=matrix.copy();small_matrix[0]*=96/tw;small_matrix[1]*=96/th
  small_gen=cv2.warpAffine(gen,small_matrix,(96,96),flags=cv2.INTER_AREA).astype(np.float32);small_old=cv2.resize(out[t:b,l:r],(96,96)).astype(np.float32)
  delta=np.clip(np.median((small_old-small_gen).reshape(-1,3),axis=0),-8,8)
  ax=np.minimum(np.clip(np.arange(tw)/(tw*.2),0,1)if l>0 else np.ones(tw),np.clip((tw-1-np.arange(tw))/(tw*.2),0,1)if r<W else np.ones(tw));sigma=max(1.0,2*W/w);halo=int(np.ceil(4*sigma))
  # A 8192 square master must not allocate several full float32 padded tiles.
  # Process bounded stripes, with Gaussian halo and immutable per-tile prior.
  prior_patch=out[t:b,l:r].copy();gen_valid=np.ones(gen.shape[:2],np.float32)
  for scan in range(0,th,128):
   end=min(th,scan+128);top=max(0,scan-halo);bottom=min(th,end+halo);sm=matrix.copy();sm[1,2]-=top
   warped=cv2.warpAffine(gen,sm,(tw,bottom-top),flags=cv2.INTER_LANCZOS4).astype(np.float32);warped=np.clip(warped+delta,0,255);valid=cv2.warpAffine(gen_valid,sm,(tw,bottom-top),flags=cv2.INTER_LINEAR)
   patch=prior_patch[top:bottom].astype(np.float32);yy=np.arange(top,bottom);ay=np.minimum(np.clip(yy/(th*.2),0,1)if t>0 else np.ones(len(yy)),np.clip((th-1-yy)/(th*.2),0,1)if b<H else np.ones(len(yy)));alpha=(ay[:,None]*ax[None,:]*valid)[:,:,None].astype(np.float32)
   if pass_number==1:
    low=cv2.GaussianBlur(warped,(0,0),sigma);old_low=cv2.GaussianBlur(patch,(0,0),sigma);mix=patch+(low-old_low)*alpha+((warped-low)-(patch-old_low))*(alpha**8)
   else:mix=patch*(1-alpha)+warped*alpha
   out[t+scan:t+end,l:r]=np.clip(mix[scan-top:end-top],0,255).astype(np.uint8)
  del prior_patch,warped,valid,patch,alpha,mix
  if pass_number==1:del low,old_low
  rows.append({'id':tile['id'],'accepted':True,'broadColorOffsetBGR':delta.tolist(),'registration':receipt})
 # Neighbour overlap must not silently reconstruct an explicitly retained core.
 retained=[tile for tile in tiles if tile['status']=='retained']
 retention_base=base if pass_number==1 else (cv2.imread(str(root/'pass1-master.png'))if retained else None)
 for tile in retained:
  if pass_number==1:
   l,t,r,b=tile['core'];l,t,r,b=round(l*W/w),round(t*H/h),round(r*W/w),round(b*H/h)
  else:l,t,r,b=tile['box']
  out[t:b,l:r]=retention_base[t:b,l:r]
 mask=cv2.imread(str(root/protection['mask']),cv2.IMREAD_GRAYSCALE);mask=cv2.resize(mask,(W,H),interpolation=cv2.INTER_NEAREST)
 # Strip-wise protection preserves fully masked pixels exactly from the ordinary baseline.
 for top in range(0,H,128):
  mm=mask[top:top+128].astype(np.float32)[:,:,None]/255;out[top:top+128]=np.clip(out[top:top+128]*(1-mm)+base[top:top+128]*mm,0,255).astype(np.uint8)
 # Preserve the source silhouette/alpha independently of generated RGB detail.
 if job.get('sourceHasAlpha'):
  alpha=cv2.imread(str(root/'source-alpha.png'),cv2.IMREAD_GRAYSCALE);alpha=cv2.resize(alpha,(W,H),interpolation=cv2.INTER_LANCZOS4);encoded=cv2.cvtColor(out,cv2.COLOR_BGR2BGRA);encoded[:,:,3]=alpha
 else:encoded=out
 filename=f'pass{pass_number}-master.png';cv2.imwrite(str(root/filename),encoded);check=cv2.imread(str(root/filename))
 if check is None or check.shape[:2]!=(H,W):raise ValueError('Saved master decode failed')
 cv2.imwrite(str(root/f'pass{pass_number}-preview.png'),cv2.resize(out,(w,h),interpolation=cv2.INTER_AREA))
 retained=[t['id']for t in tiles if t['status']=='retained'];inherited=json.loads((root/'pass1-assembly.json').read_text()).get('retainedPriorTiles',[])if pass_number==2 else[]
 receipt={'id':job['id'],'pass':pass_number,'roiRevision':job.get('roiRevision',0),'exportDimensions':[W,H],'sourceDimensions':[w,h],'nativeFullScene8192':False,'opencvThreads':cv2.getNumThreads(),'blendBoundaryPolicy':'feather internal tile/ROI boundaries only; canvas edges retain full candidate weight; validity and source protection still apply','method':'accepted native AI tiles; similarity registration; bounded color correction; two-band feather P1 / ROI feather P2; owner protection mask','tiles':rows,'acceptedNativeTiles':len(tiles)-len(retained),'retainedPriorTiles':retained,'inheritedPass1Retentions':inherited,'fullNativeReconstruction':not(retained or inherited),'protection':protection,'sourceAlphaPreserved':job.get('sourceHasAlpha',False),'status':'requires_visual_review','master':filename};(root/f'pass{pass_number}-assembly.json').write_text(json.dumps(receipt,indent=2)+'\n');job['status']='p1_assembled'if pass_number==1 else('master_partial_reconstruction_ready_for_visual_review'if retained or inherited else'master_ready_for_visual_review');save_job(root,job);return receipt

def locked_assemble(root,pass_number):
 lock_path=ROOT/'.tmp-work/flowers-global-assembly.lock';lock_path.parent.mkdir(exist_ok=True)
 with lock_path.open('a+')as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:raise RuntimeError('Global8192 assembly slot busy; no assembly started. Wait for owner handoff.')
  lock.seek(0);lock.truncate();lock.write(json.dumps({'pid':os.getpid(),'asset':Path(root).name,'pass':pass_number}));lock.flush()
  return assemble(root,pass_number)

def main():
 if len(sys.argv)>1 and sys.argv[1] in ['prepare','record','assemble']:
  bun=shutil.which('bun')
  if not bun:raise RuntimeError('Bun is required for the local storage preflight')
  subprocess.run([bun,'scripts/repository-budget.ts','--local-only'],cwd=ROOT,check=True)
 p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','record','retain','reject-visual','protection','rois','assemble','status']);p.add_argument('id');p.add_argument('tile',nargs='?');p.add_argument('--candidate');p.add_argument('--freeze-receipt');p.add_argument('--prompt');p.add_argument('--tool-receipt');p.add_argument('--file');p.add_argument('--receipt');p.add_argument('--reason');p.add_argument('--append',action='store_true');p.add_argument('--pass',dest='pass_number',type=int,choices=[1,2]);args=p.parse_args();manifest=json.loads(MANIFEST.read_text());asset=next(a for a in manifest['assets']if a['id']==args.id);root=ROOT/asset['outputRoot']
 if asset.get('freezeStatus','').startswith('hold')and args.command in ['prepare','rois','assemble']:raise ValueError('Asset is on semantic source HOLD: '+asset.get('holdReason','owner source correction pending'))
 if args.command=='prepare':result=prepare_job(root,ROOT/asset['source'],asset['id'],args.freeze_receipt)
 elif args.command=='record':result=record(root,args.tile,args.candidate,args.prompt,args.tool_receipt)
 elif args.command=='retain':result=retain(root,args.tile,args.reason,args.receipt)
 elif args.command=='reject-visual':result=visual_reject(root,args.tile,args.reason,args.receipt)
 elif args.command=='protection':set_protection(root,args.file,args.receipt);result=load_job(root)
 elif args.command=='rois':result=set_rois(root,args.file,args.append)
 elif args.command=='assemble':result=locked_assemble(root,args.pass_number)
 else:result=load_job(root)
 if args.command in ['prepare','status','rois']:result={'id':result['id'],'status':result['status'],'outputRoot':str(root),'nextPending':[t['id']for t in result['tiles']+result['rois']if t['status']!='accepted'],'protection':result['protection']}
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
