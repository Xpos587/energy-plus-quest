"""General-owned durable progress index; owner job.json files are authoritative."""
import argparse,json,os
from freshness import assembly_is_current
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'docs/reviews/flowers-all-2026-10-20';p=argparse.ArgumentParser();p.add_argument('--sync',action='store_true');args=p.parse_args();manifest=json.loads((D/'manifest.json').read_text());totals={'assets':len(manifest['assets']),'preparedAssets':0,'registeredNativeAttempts':0,'acceptedNativeTiles':0,'retainedTiles':0,'p1Assembled':0,'p2Assembled':0,'integratedAssets':0};owners={}
for a in manifest['assets']:
 root=ROOT/a['outputRoot'];job_path=root/'job.json';o=owners.setdefault(a['owner'],{'assets':0,'prepared':0,'registeredNativeAttempts':0,'acceptedNativeTiles':0,'retainedTiles':0,'p2Assembled':0});o['assets']+=1
 if not job_path.exists():continue
 j=json.loads(job_path.read_text());tiles=j['tiles']+j['rois'];c={'registeredNativeAttempts':sum(len(t['attempts'])for t in tiles),'acceptedNativeTiles':sum(t['status']=='accepted'for t in tiles),'rejectedTiles':sum(t['status']=='rejected'for t in tiles),'retainedTiles':sum(t['status']=='retained'for t in tiles),'pendingTiles':sum(t['status']=='pending'for t in tiles)};a['processingStatus']=j['status'];a['progress']=c;a['jobReceipt']=str(job_path.relative_to(ROOT));totals['preparedAssets']+=1;o['prepared']+=1
 for key in ['registeredNativeAttempts','acceptedNativeTiles','retainedTiles']:totals[key]+=c[key];o[key]+=c[key]
 for pass_number in [1,2]:
  requested=j['tiles']if pass_number==1 else j['rois']
  assembly=root/f'pass{pass_number}-assembly.json'
  if assembly.exists()and assembly_is_current(j,json.loads(assembly.read_text()),pass_number):totals[f'p{pass_number}Assembled']+=1;o['p2Assembled']+=int(pass_number==2)
registry=ROOT/'src/media/flowers-masters.json'
if registry.exists():
 aliases=json.loads(registry.read_text());totals['aliasRegisteredAssets']=len(aliases);totals['integratedAssets']=sum(bool(r.get('runtimeVerified'))for r in aliases.values())
 for a in manifest['assets']:
  if a['source']in aliases:
   row=aliases[a['source']];a['integrationStatus']='runtime_verified'if row.get('runtimeVerified')else'alias_registered_runtime_pending';a['runtimeAliasRegistry']='src/media/flowers-masters.json'
totals['selectiveFlowersRuntimeAssets']=sum(bool(r.get('runtimeVerified'))for r in aliases.values())if registry.exists()else 0
conventional=ROOT/'src/media/conventional-enlargements.json'
conventional_rows=json.loads(conventional.read_text())if conventional.exists()else{}
totals['conventionalEnlargementRuntimeAssets']=sum(bool(r.get('runtimeVerified'))for r in conventional_rows.values())
verified_flowers={source for source,row in aliases.items()if row.get('runtimeVerified')}if registry.exists()else set()
verified_conventional={source for source,row in conventional_rows.items()if row.get('runtimeVerified')}
totals['runtimeQualityVerifiedAssets']=len(verified_flowers|verified_conventional)
for asset in manifest['assets']:
 if asset['source']in verified_conventional and asset['source']not in verified_flowers:
  asset['integrationStatus']='runtime_verified_conventional_interpolation';asset['runtimeAliasRegistry']='src/media/conventional-enlargements.json'
report={'recordedAt':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'policy':'2026-10-22 throughput reset: no mandatory Flowers coverage of all manifest assets; selective accepted work and measured conventional enlargement have separate counters.','evidence':'Registered attempts only; retained regions are not native reconstruction. Assembly and alias registration do not prove runtime quality. Runtime-verified Flowers count includes accepted historical two-pass work reused selectively.','totals':totals,'owners':owners}
if args.sync:
 manifest['updatedAt']=report['recordedAt'];tmp=D/'manifest.next.json';tmp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,D/'manifest.json');tmp=D/'progress.next.json';tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,D/'progress.json')
print(json.dumps(report,ensure_ascii=False,indent=2))
