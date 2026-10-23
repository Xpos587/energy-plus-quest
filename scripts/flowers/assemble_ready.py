"""General's measured runner for explicitly owner-ready assembly; no generation."""
import argparse,json,resource,subprocess,sys,time,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('--pass',dest='pass_number',required=True,type=int,choices=[1,2]);args=p.parse_args()
 manifest=json.loads((ROOT/'docs/reviews/flowers-all-2026-10-20/manifest.json').read_text());asset=next(a for a in manifest['assets']if a['id']==args.id);root=ROOT/asset['outputRoot'];job=json.loads((root/'job.json').read_text())
 requested=job['tiles']if args.pass_number==1 else job['rois']
 if not requested or any(t['status']not in['accepted','retained']for t in requested):raise ValueError('Owner job is not ready; no assembly started')
 if job.get('passProtection',{}).get(str(args.pass_number),job['protection'])['status']!='owner_approved':raise ValueError('Owner protection approval required')
 if asset['freezeStatus'].startswith('hold'):raise ValueError('Source HOLD forbids assembly')
 output=ROOT/'docs/reviews/flowers-all-2026-10-20/general-assemblies';output.mkdir(parents=True,exist_ok=True);stem=f'{args.id}-P{args.pass_number}';latest=output/f'{stem}.json'
 versions=[int(file.stem.rsplit('-',1)[1])for file in output.glob(f'{stem}-run-*.json')]
 if latest.exists()and not versions:shutil.copyfile(latest,output/f'{stem}-run-001.json');versions=[1]
 run=max(versions,default=0)+1;history=output/f'{stem}-run-{run:03}.json'
 start=time.monotonic();log=ROOT/f'.tmp-work/general-assemble-{stem}-run-{run:03}.log'
 with log.open('w')as out:result=subprocess.run([sys.executable,str(ROOT/'scripts/flowers/pipeline.py'),'assemble',args.id,'--pass',str(args.pass_number)],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
 receipt={'id':args.id,'pass':args.pass_number,'operation':'General deterministic assembly of explicitly owner-ready job','exitCode':result.returncode,'wallSeconds':time.monotonic()-start,'childPeakRSSKiB':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'nativeGenerationCalls':0,'sourceOrRoiEdited':False,'log':str(log.relative_to(ROOT)),'ownerVisualReview':'required before promotion'}
 receipt['historyReceipt']=str(history.relative_to(ROOT));history.write_text(json.dumps(receipt,indent=2)+'\n');latest.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));subprocess.run([sys.executable,str(ROOT/'scripts/flowers/progress.py'),'--sync'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL);sys.exit(result.returncode)
