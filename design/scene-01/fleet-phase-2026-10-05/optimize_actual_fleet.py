"""Actual four-model phase optimizer; local diagnostics only, no runtime edits."""
from pathlib import Path
import argparse,json,itertools,time
import cv2,numpy as np
from scipy.spatial import cKDTree
cv2.setNumThreads(1)
ROOT=Path('/home/michael/Github/energy-plus-quest');HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--config',default=str(HERE/'actual-fleet-config.json'));args=p.parse_args();cfg=json.loads(Path(args.config).read_text());N=cfg['period_frames'];scale=cfg['scale'];margin=cfg['margin_px'];OUT=HERE/cfg['output_subdirectory'];OUT.mkdir(exist_ok=True);COLORS=list(cfg['colors']);data={};metrics={}
for color,entry in cfg['colors'].items():
 folder=ROOT/entry['directory'];track=json.loads((folder/entry['tracking']).read_text());raw=track['rows'];count=len(raw)
 mapping=np.arange(N) if count==N else (np.rint(np.arange(N)*(count-1)/(N-1)).astype(int) if cfg['blue_mapping']=='endpoint-inclusive' else np.floor(np.arange(N)*count/N).astype(int))
 rows=[];geometry=[];straight=[];heading=[];sourcepaths=[]
 for i,j in enumerate(mapping):
  path=folder/'rgba-frames'/f'{j+entry["first_file_index"]:04d}.png';a=cv2.imread(str(path),-1)
  if a is None:raise RuntimeError(f'Missing actual frame {path}')
  row=dict(raw[j]);row.update(common_frame=i,normalized_source_row=int(j));rows.append(row);sourcepaths.append(str(path));y,x=np.where(a[:,:,3]>0);x0=max(0,int(x.min())-2);y0=max(0,int(y.min())-2);x1=min(1280,int(x.max())+3);y1=min(720,int(y.max())+3);crop=a[y0:y1,x0:x1];anchor=np.array(row['cab_px'])-[x0,y0];mat=np.array([[scale,0,(1-scale)*anchor[0]],[0,scale,(1-scale)*anchor[1]]],dtype='float32');alpha=cv2.warpAffine(crop[:,:,3],mat,(crop.shape[1],crop.shape[0]),flags=cv2.INTER_LINEAR);mask=alpha>127;y,x=np.where(mask);box=np.array([x.min()+x0,y.min()+y0,x.max()+x0,y.max()+y0]);sub=mask[box[1]-y0:box[3]-y0+1,box[0]-x0:box[2]-x0+1];contours,_=cv2.findContours(mask.astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE);pts=np.vstack(contours).reshape(-1,2)+[x0,y0];geometry.append((box,sub,pts,cKDTree(pts)))
  # Opening straightness is measured on unscaled actual cab/trailer geometry.
  hsv=cv2.cvtColor(crop[:,:,:3],cv2.COLOR_BGR2HSV);trailer=((crop[:,:,3]>127)&(hsv[:,:,1]<65)&(hsv[:,:,2]>160)).astype('uint8');cc,l,stats,cent=cv2.connectedComponentsWithStats(trailer)
  if cc<2:raise RuntimeError(f'No visible trailer in {path}')
  k=1+np.argmax(stats[1:,4]);yy,xx=np.where(l==k);_,vectors=np.linalg.eigh(np.cov(np.column_stack([xx,yy]).T));axis=vectors[:,-1];v=anchor-cent[k];v=v/np.linalg.norm(v);art=float(np.degrees(np.arccos(np.clip(abs(v@axis),0,1))));card=float(np.degrees(np.arccos(np.clip(max(abs(axis)),0,1))));heading.append({'articulation_deg':art,'cardinal_axis_deviation_deg':card});straight.append(art<=8 and card<=12)
 straight=np.array(straight);stable=straight&np.roll(straight,3)&np.roll(straight,-3);data[color]={'rows':rows,'geometry':geometry,'straight':stable,'heading':heading,'mapping':mapping,'paths':sourcepaths};metrics[color]={'source_directory':str(folder),'tracking_path':str(folder/entry['tracking']),'source_row_count':count,'source_index_mapping':mapping.tolist(),'eligible_straight_opening_frames':np.where(stable)[0].tolist(),'raw_closed_roof_track_distance_px':float(np.linalg.norm(np.roll(np.array([r['cab_px'] for r in rows]),-1,axis=0)-np.array([r['cab_px'] for r in rows]),axis=1).sum())};print('loaded',color,len(rows),'straight',int(stable.sum()),flush=True)
def gap(a,b):
 dx=np.maximum(np.maximum(a[...,0]-b[...,2],b[...,0]-a[...,2]),0);dy=np.maximum(np.maximum(a[...,1]-b[...,3],b[...,1]-a[...,3]),0);return np.hypot(dx,dy)
def intersect(a,b):
 ba,ma,pa,tree=a;bb,mb,pb,_=b;x0=max(ba[0],bb[0]);x1=min(ba[2],bb[2]);y0=max(ba[1],bb[1]);y1=min(ba[3],bb[3]);ov=0
 if x1>=x0 and y1>=y0:ov=int((ma[y0-ba[1]:y1-ba[1]+1,x0-ba[0]:x1-ba[0]+1]&mb[y0-bb[1]:y1-bb[1]+1,x0-bb[0]:x1-bb[0]+1]).sum())
 d=0.0 if ov else max(0,float(tree.query(pb,k=1)[0].min())-np.sqrt(2));return d,ov
pairdata={};arrays={};idx=np.arange(N)
for c,z in itertools.combinations(COLORS,2):
 a=data[c]['geometry'];b=data[z]['geometry'];ab=np.array([v[0]for v in a]);bb=np.array([v[0]for v in b]);dist=gap(ab[:,None],bb[None,:]);over=np.zeros(dist.shape,dtype='int32')
 for x,y in zip(*np.where(dist<margin+2)):dist[x,y],over[x,y]=intersect(a[x],b[y])
 mins=np.array([dist[idx,(idx+d)%N].min()for d in range(N)]);sums=np.array([over[idx,(idx+d)%N].sum()for d in range(N)]);frames=np.array([(over[idx,(idx+d)%N]>0).sum()for d in range(N)]);pairdata[(c,z)]=(mins,sums,frames);arrays[c+'_'+z+'_distance']=dist;arrays[c+'_'+z+'_overlap']=over;print('pair',c,z,'valid relative phases',int((mins>=margin).sum()),'best gap',float(mins.max()),flush=True)
np.savez(OUT/'actual-pair-matrices.npz',**arrays)
def rotatebits(v,d):
 return sum(1<<int(i) for i in np.where(np.roll(v,-d))[0])
g,r,y,b=COLORS;G=rotatebits(data[g]['straight'],0);Rb={i:rotatebits(data[r]['straight'],i)for i in range(N)};Yb={i:rotatebits(data[y]['straight'],i)for i in range(N)};Bb={i:rotatebits(data[b]['straight'],i)for i in range(N)};best=None;solutions=0;offsetsets={pair:np.where(v[0]>=margin)[0]for pair,v in pairdata.items()}
for dr in offsetsets[(g,r)]:
 origin=G&Rb[int(dr)]
 if not origin:continue
 for dy in offsetsets[(g,y)]:
  if pairdata[(r,y)][0][(dy-dr)%N]<margin:continue
  origins=origin&Yb[int(dy)]
  if not origins:continue
  possible=offsetsets[(g,b)];possible=possible[(pairdata[(r,b)][0][(possible-dr)%N]>=margin)&(pairdata[(y,b)][0][(possible-dy)%N]>=margin)]
  for db in possible:
   starts=origins&Bb[int(db)]
   if not starts:continue
   deltas={(g,r):dr,(g,y):dy,(g,b):db,(r,y):(dy-dr)%N,(r,b):(db-dr)%N,(y,b):(db-dy)%N};minimum=min(pairdata[p][0][d]for p,d in deltas.items());far=min(pairdata[p][0][d]for p,d in deltas.items()if b not in p);rank=(float(minimum),float(far));solutions+=starts.bit_count()
   if best is None or rank>best[0]:
    origin0=(starts&-starts).bit_length()-1;phases=dict(zip(COLORS,[origin0,(origin0+int(dr))%N,(origin0+int(dy))%N,(origin0+int(db))%N]));best=(rank,phases)
report={'label':cfg['label'],'actual_models':True,'scale':scale,'period_seconds':N/cfg['fps'],'fps':cfg['fps'],'frames_checked_per_pair':N,'margin_px':margin,'status':'actual alpha>127 zero-overlap and2px-margin phase candidate' if best else 'NO PASS: no phase combination meets actual alpha>127 and2px margin','qualifying_opening_combinations':solutions,'phases_common_frames':best[1]if best else None,'minimum_conservative_body_gap_px':best[0][0]if best else None,'minimum_far3_gap_px':best[0][1]if best else None,'source_evidence':metrics,'pair_relative_phase_metrics':{c+'_'+z:{'minimum_body_gap_by_relative_phase':v[0].tolist(),'overlap_pixels_by_relative_phase':v[1].tolist(),'overlap_frames_by_relative_phase':v[2].tolist()}for(c,z),v in pairdata.items()},'body_criteria':'ALL actual source alpha>127 pixels included. No manual fringe suppression. Near-envelope gap uses closest contour pixel-center distance minus sqrt(2), a conservative pixel-square extent bound; distant AABB separation is conservative. Not a physical collision claim.','opening_criteria':'Actual source trailer PCA axis within12deg cardinal; cab-to-trailer alignment within8deg; source/common neighbors+-3frames must also qualify. Uniform rig scale around actual cab roof preserves articulation.','matte_caveat':'green/blue cleanup state recorded in config label; alpha>16 soft/fringe check will be separately reported for selected candidate; no arbitrary alpha cropping.'}
if best:
 phases=best[1];pairs=[];critical=[]
 for c,z in itertools.combinations(COLORS,2):
  ci=(idx+phases[c])%N;zi=(idx+phases[z])%N;d=arrays[c+'_'+z+'_distance'][ci,zi];ov=arrays[c+'_'+z+'_overlap'][ci,zi];k=int(d.argmin());critical.append(k);pairs.append({'pair':[c,z],'minimum_body_gap_px':float(d[k]),'minimum_gap_output_frame':k,'minimum_gap_time_s':k/cfg['fps'],'source_normalized_frames':[int(ci[k]),int(zi[k])],'actual_source_rows':[int(data[c]['mapping'][ci[k]]),int(data[z]['mapping'][zi[k]])],'opaque_overlap_frames':int((ov>0).sum()),'max_opaque_overlap_pixels':int(ov.max())})
 report['selected_pairs']=pairs;report['opening_geometry']={c:dict(data[c]['heading'][phases[c]],source_row=int(data[c]['mapping'][phases[c]]),cab_px=data[c]['rows'][phases[c]]['cab_px'])for c in COLORS}
 # Final renderer gets explicit actual source path and anchor per output frame.
 plan=[]
 for k in range(N):
  frame={'output_frame':k,'time':k/cfg['fps'],'layers':{}}
  for c in COLORS:
   j=(k+phases[c])%N;frame['layers'][c]={'path':data[c]['paths'][j],'cab_anchor_px':data[c]['rows'][j]['cab_px'],'uniform_scale':scale,'normalized_frame':j,'source_row':int(data[c]['mapping'][j])}
  plan.append(frame)
 (OUT/'render-plan.json').write_text(json.dumps({'status':'local candidate plan; parent owns rendering/integration','config':cfg,'rows':plan},indent=2))
 base=cv2.imread(str(ROOT/'design/scene-01/kling-layer-extract-2026-10-05/empty-map-padded.png'));tiles=[];softmetrics={c+'_'+z:[]for c,z in itertools.combinations(COLORS,2)};softboxes={}
 def layer(c,j):
  a=cv2.imread(data[c]['paths'][j],-1).astype('float32');anchor=data[c]['rows'][j]['cab_px'];mat=np.array([[scale,0,(1-scale)*anchor[0]],[0,scale,(1-scale)*anchor[1]]],dtype='float32');a[:,:,:3]*=a[:,:,3:4]/255;a=cv2.warpAffine(a,mat,(1280,720),flags=cv2.INTER_LINEAR);a[:,:,:3]=np.divide(a[:,:,:3],a[:,:,3:4]/255,out=np.zeros_like(a[:,:,:3]),where=a[:,:,3:4]>1e-6);return np.clip(np.rint(a),0,255).astype('uint8')
 for c in COLORS:
  soft=[]
  for j in range(N):
   a=layer(c,j)[:,:,3]>16;yy,xx=np.where(a);box=[xx.min(),yy.min(),xx.max(),yy.max()];soft.append((box,a[box[1]:box[3]+1,box[0]:box[2]+1]))
  softboxes[c]=soft
 for c,z in itertools.combinations(COLORS,2):
  hits=[]
  for k in range(N):
   ba,ma=softboxes[c][(k+phases[c])%N];bb,mb=softboxes[z][(k+phases[z])%N];x0=max(ba[0],bb[0]);x1=min(ba[2],bb[2]);y0=max(ba[1],bb[1]);y1=min(ba[3],bb[3]);hit=0
   if x1>=x0 and y1>=y0:hit=int((ma[y0-ba[1]:y1-ba[1]+1,x0-ba[0]:x1-ba[0]+1]&mb[y0-bb[1]:y1-bb[1]+1,x0-bb[0]:x1-bb[0]+1]).sum())
   hits.append(hit)
  softmetrics[c+'_'+z]={'soft_alpha_overlap_frames':sum(v>0 for v in hits),'maximum_soft_overlap_pixels':max(hits)}
 report['selected_soft_alpha_metrics']=softmetrics
 for k in sorted(set([0,N-1]+critical+list(range(0,N,72)))):
  frame=base.copy()
  for c in COLORS:
   j=(k+phases[c])%N;a=layer(c,j);alpha=a[:,:,3:4]/255;frame=(a[:,:,:3]*alpha+frame*(1-alpha)).astype('uint8');cab=data[c]['rows'][j]['cab_px'];cv2.putText(frame,c,(int(cab[0])+10,int(cab[1])-10),0,.4,(25,25,25),1)
  cv2.putText(frame,f'ACTUAL4 | t={k/cfg["fps"]:.3f}s | scale{scale:.2f}',(10,20),0,.45,(25,25,25),1);tiles.append(cv2.resize(frame,(640,360)));cv2.imwrite(str(OUT/f'diagnostic-{k:04d}.png'),frame)
 while len(tiles)%3:tiles.append(np.full_like(tiles[0],245))
 cv2.imwrite(str(OUT/'actual-fleet-contact-sheet.png'),np.vstack([np.hstack(tiles[i:i+3])for i in range(0,len(tiles),3)]))
(OUT/'phase-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k]for k in ['label','scale','status','phases_common_frames','minimum_conservative_body_gap_px','minimum_far3_gap_px','qualifying_opening_combinations']},indent=2),flush=True)
