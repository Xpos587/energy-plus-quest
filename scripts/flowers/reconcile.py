"""Read-only crash recovery audit. Never regenerates, deletes, hashes or sizes files."""
import argparse,json,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[2]
def same_pixels(a,b):
 with Image.open(a)as left,Image.open(b)as right:
  if left.size!=right.size:return False
  # RGBA getbbox can ignore RGB when alpha is equal: compare RGB and A separately.
  left=left.convert('RGBA');right=right.convert('RGBA')
  return ImageChops.difference(left.convert('RGB'),right.convert('RGB')).getbbox()is None and ImageChops.difference(left.getchannel('A'),right.getchannel('A')).getbbox()is None

def candidate_roots(asset):
 roots=[ROOT/asset['outputRoot']];ident=asset['id'];owner=asset['owner']
 if owner=='intro':roots.append(ROOT/f'docs/reviews/intro-2026-10-20-flowers/prepared/{ident}')
 if owner=='ending':roots.append(ROOT/f'docs/reviews/ending-2026-10-20-flowers/prepared/{ident}')
 if owner=='lastmile'and asset.get('peerId'):roots.append(ROOT/f"docs/reviews/lastmile-2026-10-20-flowers/prepared/{asset['peerId']}")
 return roots

def audit(manifest):
 rows=[]
 for asset in manifest['assets']:
  root=ROOT/asset['outputRoot'];job_file=root/'job.json'
  if not job_file.exists():continue
  row={'id':asset['id'],'owner':asset['owner'],'freezeStatus':asset['freezeStatus'],'issues':[],'savedCandidatesAlreadyRegistered':0,'unmatchedSavedCandidates':[],'candidateSearchRoots':[str(p.relative_to(ROOT))for p in candidate_roots(asset)]}
  try:job=json.loads(job_file.read_text())
  except Exception as e:row['issues'].append({'kind':'job_json_unreadable','error':str(e)});rows.append(row);continue
  tiles=job['tiles']+job['rois'];recorded={};tile_attempt_paths={}
  for tile in tiles:
   paths=[]
   for attempt in tile['attempts']:
    file=root/attempt.get('candidate','missing-candidate');recorded[file.resolve()]=True;paths.append(file)
    try:
     with Image.open(file)as image:
      image.load();dimensions=list(image.size)
     if attempt.get('nativeGeneratedDimensions')and dimensions!=attempt['nativeGeneratedDimensions']:row['issues'].append({'kind':'native_dimensions_mismatch','file':str(file.relative_to(ROOT)),'actual':dimensions,'recorded':attempt['nativeGeneratedDimensions']})
    except Exception as e:row['issues'].append({'kind':'recorded_native_missing_or_decode_failed','file':str(file.relative_to(ROOT)),'error':str(e)})
   tile_attempt_paths[tile['id']]=paths
  row['registeredAttemptsChecked']=sum(len(t['attempts'])for t in tiles)
  frozen=root/'source.png'
  if frozen.exists():
   try:
    with Image.open(frozen)as im:im.load();row['frozenDimensions']=list(im.size)
    if row['frozenDimensions']!=job['sourceDimensions']:row['issues'].append({'kind':'frozen_dimensions_mismatch'})
    if not same_pixels(frozen,ROOT/asset['source']):row['issues'].append({'kind':'canonical_source_differs_from_frozen','action':'owner verifies revision; do not attribute old processing to changed source'})
    if job.get('sourceHasAlpha')and not(root/'source-alpha.png').exists():row['issues'].append({'kind':'missing_frozen_alpha'})
   except Exception as e:row['issues'].append({'kind':'frozen_source_decode_failed','error':str(e)})
  else:row['issues'].append({'kind':'missing_frozen_source'})
  pending_next=root/'job.next.json'
  if pending_next.exists():
   try:
    next_job=json.loads(pending_next.read_text());row['atomicNextCheckpoint']={'path':str(pending_next.relative_to(ROOT)),'sameAsset':next_job.get('id')==job['id'],'registeredAttempts':sum(len(t['attempts'])for t in next_job['tiles']+next_job['rois']),'action':'owner reconcile before any new generation; audit does not replace state'}
   except FileNotFoundError:pass
   except Exception as e:row['atomicNextCheckpoint']={'error':str(e),'action':'owner inspect, never regenerate automatically'}
  seen=set()
  for directory in candidate_roots(asset):
   if not directory.exists():continue
   for file in directory.glob('*.png'):
    if not re.search(r'-(?:native|ai)(?:-\d+)?\.png$',file.name)or file.resolve()in recorded or file.resolve()in seen:continue
    seen.add(file.resolve());matching=[t['id']for t in tiles if file.name.startswith(t['id']+'-')]
    if not matching:continue
    tile_id=max(matching,key=len)
    try:
     matched=any(p.exists()and same_pixels(file,p)for p in tile_attempt_paths[tile_id])
     if matched:row['savedCandidatesAlreadyRegistered']+=1
     else:row['unmatchedSavedCandidates'].append({'tile':tile_id,'file':str(file.relative_to(ROOT)),'action':'owner checks existing native/receipt and records it if appropriate; NEVER auto-regenerate'})
    except Exception as e:row['issues'].append({'kind':'saved_candidate_decode_pending_or_failed','file':str(file.relative_to(ROOT)),'error':str(e)})
  rows.append(row)
 return{'recordedAt':datetime.now(timezone.utc).isoformat(),'policy':'Read-only evidence. No E calls, no file hashes/sizes, no deletion/state replacement. Concurrent owner writes can make unmatched candidates transient; owner rechecks before action. Default image_gen files outside these known project roots are reconciled by each owner from exact tool receipts.','summary':{'preparedJobsChecked':len(rows),'registeredAttemptsChecked':sum(r.get('registeredAttemptsChecked',0)for r in rows),'savedCandidatesAlreadyRegistered':sum(r['savedCandidatesAlreadyRegistered']for r in rows),'unmatchedSavedCandidates':sum(len(r['unmatchedSavedCandidates'])for r in rows),'jobsWithIssues':sum(bool(r['issues'])for r in rows),'atomicNextCheckpoints':sum('atomicNextCheckpoint'in r for r in rows)},'rows':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='docs/reviews/flowers-all-2026-10-20/reconciliation-2026-10-21.json');a=p.parse_args();result=audit(json.loads((ROOT/'docs/reviews/flowers-all-2026-10-20/manifest.json').read_text()));(ROOT/a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['summary'],indent=2))
