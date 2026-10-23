"""General-only activation after source/master/100% visual acceptance."""
import argparse,json,os,shutil
from pathlib import Path
from PIL import Image
from freshness import assembly_is_current
ROOT=Path(__file__).resolve().parents[2]
def promote(root,asset,review_path):
 root=Path(root);job_root=root/asset['outputRoot'];review_path=str(review_path)
 if not review_path.startswith('docs/reviews/')or'..'in Path(review_path).parts:raise ValueError('Review must be a repository review receipt')
 if asset.get('freezeStatus','').startswith('hold'):raise ValueError('Semantic source HOLD forbids runtime integration')
 review=json.loads((root/review_path).read_text())
 if review.get('decision')!='accepted_for_runtime'or review.get('passes')!=2:raise ValueError('Explicit accepted two-pass runtime review required')
 job=json.loads((job_root/'job.json').read_text());p1=json.loads((job_root/'pass1-assembly.json').read_text());p2=json.loads((job_root/'pass2-assembly.json').read_text())
 if not job['status'].startswith('master_'):raise ValueError('Both assembled passes required')
 retained=p1.get('retainedPriorTiles',[])+p2.get('retainedPriorTiles',[])+p2.get('inheritedPass1Retentions',[])
 if retained and not review.get('acceptsRetainedRegions'):raise ValueError('Explicit review acceptance of retained regions required; never imply full reconstruction')
 if not assembly_is_current(job,p1,1)or not assembly_is_current(job,p2,2):raise ValueError('Assembly is stale relative to current ROI/attempt/protection inputs')
 mode=review.get('processingMode','two_pass_flowers')
 if len(job.get('rois',[]))<4 and mode!='selective_flowers':
  exception=review.get('p2RoiException',{})
  if not all(exception.get(k)for k in ['justification','ownerReceipt','disclosure']):raise ValueError('Recipe requires at least4 meaningful P2 ROIs; a genuine fewer-area exception must be justified and disclosed')
 if p1.get('acceptedNativeTiles',0)+p2.get('acceptedNativeTiles',0)==0:raise ValueError('No accepted native reconstruction; cannot promote a resize-only master')
 master=job_root/'pass2-master.png'
 with Image.open(master)as im:
  dimensions=list(im.size);source_dimensions=job['sourceDimensions']
  if max(dimensions)!=8192:raise ValueError('Expected assembled longest-edge8192 master')
  if abs(dimensions[0]/dimensions[1]*source_dimensions[1]-source_dimensions[0])>1:raise ValueError('Master changed source aspect ratio')
  with Image.open(root/asset['source'])as original:
   if'A'in original.getbands()and'A'not in im.getbands():raise ValueError('Original alpha was lost')
 registry_path=root/'src/media/flowers-masters.json';registry_path.parent.mkdir(parents=True,exist_ok=True)
 registry=json.loads(registry_path.read_text())if registry_path.exists()else{}
 previous=registry.get(asset['source'])
 if previous and previous['reviewReceipt']==review_path and(root/previous['master']).exists():return previous
 version=(previous.get('version',0)if previous else 0)+1;destination=f"public/flowers-2pass-2026-10-20/{asset['id']}-v{version}.png";(root/destination).parent.mkdir(parents=True,exist_ok=True)
 if(root/destination).exists():raise ValueError('Versioned master already exists; refusing overwrite')
 shutil.copyfile(master,root/destination)
 row={'id':asset['id'],'master':destination,'passes':2,'processingMode':mode,'p2RoiCount':len(job.get('rois',[])),'version':version,'masterDimensions':dimensions,'reviewReceipt':review_path,'retainedRegionsDisclosed':bool(retained),'sourceAlphaPreserved':job.get('sourceHasAlpha',False)};registry[asset['source']]=row;tmp=registry_path.with_suffix('.next.json');tmp.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,registry_path)
 (job_root/f'runtime-promotion-v{version}.json').write_text(json.dumps({'canonicalSource':asset['source'],**row,'integrationState':'alias_registered_build_runtime_verification_pending'},ensure_ascii=False,indent=2)+'\n');return row
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--review',required=True);args=p.parse_args();manifest=json.loads((ROOT/'docs/reviews/flowers-all-2026-10-20/manifest.json').read_text());asset=next(a for a in manifest['assets']if a['id']==args.id);print(json.dumps(promote(ROOT,asset,args.review),indent=2))
