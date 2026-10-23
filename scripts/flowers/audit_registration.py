"""Read-only revalidation of accepted native files; never generates or changes jobs."""
import argparse,importlib.util,json
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('registration',Path(__file__).with_name('registration.py'));reg=importlib.util.module_from_spec(spec);spec.loader.exec_module(reg)
p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--output',required=True);args=p.parse_args();manifest=json.loads((ROOT/'docs/reviews/flowers-all-2026-10-20/manifest.json').read_text());registry=json.loads((ROOT/'src/media/flowers-masters.json').read_text());integrated={r['id']for r in registry.values()if r.get('runtimeVerified')};rows=[]
for a in manifest['assets']:
 root=ROOT/a['outputRoot'];path=root/'job.json'
 if not path.exists():continue
 job=json.loads(path.read_text())
 for t in job['tiles']+job['rois']:
  if t['status']!='accepted':continue
  receipt=t['attempts'][-1];matrix=receipt.get('affineGeneratedToReference');ref=cv2.imread(str(root/t['reference']));gen=cv2.imread(str(root/receipt['candidate']))
  if matrix is None or ref is None or gen is None:rows.append({'id':a['id'],'tile':t['id'],'accepted':False,'reason':'missing input'});continue
  guard=reg.geometry_guard(np.asarray(matrix),(ref.shape[1],ref.shape[0]),(gen.shape[1],gen.shape[0]));row={'id':a['id'],'tile':t['id'],'attempt':receipt.get('attempt'),'runtimeVerifiedSource':a['id']in integrated,'geometryGuard':guard,'accepted':guard['accepted']}
  if args.full and guard['accepted']:
   _,metric=reg.register(ref,gen,t['referencePixelsPerSourcePixel']);row['revalidation']=metric;row['accepted']=metric['accepted']
  rows.append(row)
report={'mode':'full_inlier_spatial_revalidation'if args.full else'affine_dimension_scan','readOnly':True,'nativeGenerationCalls':0,'acceptedTilesChecked':len(rows),'failures':[r for r in rows if not r['accepted']],'runtimeFailures':[r for r in rows if r['runtimeVerifiedSource']and not r['accepted']],'rows':rows};output=ROOT/args.output;output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['rows','failures','runtimeFailures']}));print('failures',len(report['failures']),'runtimeFailures',len(report['runtimeFailures']));print([(r['id'],r['tile'])for r in report['failures']])
