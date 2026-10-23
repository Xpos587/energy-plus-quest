"""Resumable RTX pipeline. Requires explicit pilot or full approval mode."""
from pathlib import Path
import subprocess,json,time,argparse,shutil
from PIL import Image
P=Path(__file__).resolve().parent

def validate(path,expected):
 with Image.open(path) as image:
  image.load()
  if image.size!=expected or image.mode!='RGBA':raise RuntimeError(f'Invalid PNG {path}: {image.size} {image.mode}')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--full-approved',action='store_true');parser.add_argument('--first',type=int,default=1);parser.add_argument('--last',type=int,default=1537);parser.add_argument('--pilot',action='store_true');args=parser.parse_args()
 if not args.full_approved and not args.pilot:parser.error('Choose --pilot or explicitly authorized --full-approved')
 if args.full_approved and args.pilot:parser.error('Choose one mode')
 if not 1<=args.first<=args.last<=1537:parser.error('Frame range outside 1..1537')
 batches=[list(range(start,min(start+48,args.last+1))) for start in range(args.first,args.last+1,48)] if args.full_approved else [[1,384,768]]
 blender=shutil.which('blender');prime=shutil.which('prime-run')
 if not blender or not prime:raise RuntimeError('Blender and prime-run must be installed')
 receipts=[];started=time.time()
 receipt_path=P/f'launcher-receipt-{args.first:04}.json'
 if receipt_path.exists():receipts=json.loads(receipt_path.read_text())
 for frames in batches:
  for script,folder,expected in [('render_map.py','turn-vehicles',(3840,2668)),('render_shadow.py','turn-shadow',(1920,1334))]:
   dest=P/folder;dest.mkdir(exist_ok=True)
   for f in frames:
    output=dest/f'{f:04}.png'
    if output.exists():validate(output,expected)
   remaining=[f for f in frames if not (dest/f'{f:04}.png').exists()]
   begin=time.monotonic();code=0
   if remaining:
    with (P/f'{script}-{frames[0]:04}.log').open('a') as log:
     r=subprocess.run([prime,blender,'-b',str(P/'v22-4k-source.blend'),'--python',str(P/script),'--',*[str(f) for f in remaining]],stdout=log,stderr=subprocess.STDOUT);code=r.returncode
   missing=[f for f in frames if not (dest/f'{f:04}.png').exists()]
   if not missing:
    for f in frames:validate(dest/f'{f:04}.png',expected)
   row={'script':script,'first':frames[0],'last':frames[-1],'rendered_frames':remaining,'exit':code,'missing':missing,'seconds':time.monotonic()-begin,'decoded':not missing};receipts.append(row)
   receipt_path.write_text(json.dumps(receipts,indent=2));print(json.dumps(row),flush=True)
   (P/'full-progress.json').write_text(json.dumps({'last_batch':row,'vehicles':len(list((P/'turn-vehicles').glob('[0-9][0-9][0-9][0-9].png'))),'shadows':len(list((P/'turn-shadow').glob('[0-9][0-9][0-9][0-9].png'))),'requested_first':args.first,'requested_last':args.last,'started_epoch':started,'updated_epoch':time.time()},indent=2))
   if code or missing:raise SystemExit(code or 1)
 allframes=[f for batch in batches for f in batch]
 for folder,expected in [('turn-vehicles',(3840,2668)),('turn-shadow',(1920,1334))]:
  for f in allframes:validate(P/folder/f'{f:04}.png',expected)
 (P/'full-complete.json').write_text(json.dumps({'frames_checked':allframes,'both_passes_decoded':True,'vehicle_dimensions':[3840,2668],'shadow_dimensions':[1920,1334],'frames_deliverable':[1,1536],'boundary_frame':1537,'fps':24,'duration_seconds':64,'started_epoch':started,'finished_epoch':time.time()},indent=2));print('FULL_COMPLETE',flush=True)

if __name__=='__main__':main()
