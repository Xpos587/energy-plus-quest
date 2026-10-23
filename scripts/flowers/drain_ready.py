"""Drain General's explicit ready list serially; stop at pause/BUSY, never generate."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--queue',required=True);args=p.parse_args();queue=json.loads((ROOT/args.queue).read_text());pause=ROOT/'.tmp-work/flowers-general-assembly.pause'
 for item in queue:
  if pause.exists():print(json.dumps({'event':'paused_at_boundary','next':item}),flush=True);break
  root=ROOT/'.tmp-work/flowers-all-2026-10-20'/item['id'];job=json.loads((root/'job.json').read_text());number=item['pass']
  if number==1 and(root/'pass1-assembly.json').exists():continue
  if number==2 and job['status'].startswith('master_'):continue
  requested=job['tiles']if number==1 else job['rois']
  if not requested or job['protection']['status']!='owner_approved'or any(t['status']not in['accepted','retained']for t in requested):print(json.dumps({'event':'not_ready_skipped','id':item['id']}),flush=True);continue
  print(json.dumps({'event':'starting','id':item['id'],'pass':number}),flush=True)
  result=subprocess.run([sys.executable,str(ROOT/'scripts/flowers/assemble_ready.py'),item['id'],'--pass',str(number)],cwd=ROOT)
  print(json.dumps({'event':'finished','id':item['id'],'pass':number,'exitCode':result.returncode}),flush=True)
  if result.returncode:print(json.dumps({'event':'stopped_no_retry','id':item['id']}),flush=True);break
