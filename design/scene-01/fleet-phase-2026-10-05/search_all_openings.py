from pathlib import Path
import json,itertools
import cv2,numpy as np
cv2.setNumThreads(1)
ROOT=Path('/home/michael/Github/energy-plus-quest');OUT=Path(__file__).resolve().parent
G=ROOT/'design/scene-01/kling-green-loop-2026-10-05/assembly/candidate-22.75s';B=ROOT/'design/scene-01/kling-blue-keys-2026-10-05/assembly/candidate-20s'
e=np.load(OUT/'envelopes.npz');m=np.load(OUT/'opaque-pair-matrices.npz');gg=m['gg'];ov=m['ggov'];cross=m['cross'];cov=m['cov'];n=np.arange(1092);gi=n%546
def stable(a):return a & np.roll(a,3)&np.roll(a,-3)
gst=stable(e['green_straight']);bst=stable(e['blue_straight']);starts=np.where(gst)[0][::3];starts=np.unique(np.r_[0,starts]);bstarts=np.where(bst)[0][::3]
sgap=np.array([gg[np.arange(546),(np.arange(546)+d)%546].min() for d in range(546)])
comb=[];fars=[]
for g,r,y in itertools.combinations(starts,3):
 far=min(sgap[(r-g)%546],sgap[(y-g)%546],sgap[(y-r)%546])
 if far>=4:comb.append((g,r,y));fars.append(far)
comb=np.array(comb);fars=np.array(fars);best=None
def blue_metrics(b):
 bi=(np.floor(n*480/1092).astype(int)+b)%480
 d=np.array([cross[(gi+p)%546,bi].min() for p in range(546)])
 o=np.array([cov[(gi+p)%546,bi].sum() for p in range(546)])
 f=np.array([(cov[(gi+p)%546,bi]>0).sum() for p in range(546)])
 return d,o,f
bm={}
for b in bstarts:
 d,o,f=blue_metrics(b);bm[int(b)]=(d,o,f)
 score=np.minimum(fars,d[comb].min(axis=1));pixels=o[comb].sum(axis=1);frames=f[comb].sum(axis=1)
 k=int(np.lexsort((-fars,frames,pixels,-score))[0]);rank=(float(score[k]),-int(pixels[k]),-int(frames[k]),float(fars[k]))
 if best is None or rank>best[0]:best=(rank,(*map(int,comb[k]),int(b)))
coarse=best
# Exhaustive local integer-frame neighborhood around all four coarse phases.
for b in [(coarse[1][3]+d)%480 for d in range(-3,4) if bst[(coarse[1][3]+d)%480]]:
 if b not in bm:bm[b]=blue_metrics(b)
 d,o,f=bm[b]
 lanes=[[(p+k)%546 for k in range(-3,4) if gst[(p+k)%546]] for p in coarse[1][:3]]
 for g,r,y in itertools.product(*lanes):
  far=min(sgap[(r-g)%546],sgap[(y-g)%546],sgap[(y-r)%546])
  if far<4:continue
  rank=(float(min(far,d[g],d[r],d[y])),-int(o[g]+o[r]+o[y]),-int(f[g]+f[r]+f[y]),float(far))
  if rank>best[0]:best=(rank,(g,r,y,b))
print('UNRESTRICTED',best,'coarse combos',len(comb),flush=True)
g,r,y,b=best[1];idx={'green':(gi+g)%546,'red':(gi+r)%546,'yellow':(gi+y)%546,'blue':(np.floor(n*480/1092).astype(int)+b)%480};pairs=[]
for a,z in itertools.combinations(idx,2):
 d=cross[idx[a],idx[z]] if z=='blue' else gg[idx[a],idx[z]];o=cov[idx[a],idx[z]] if z=='blue' else ov[idx[a],idx[z]];k=int(d.argmin());ko=int(o.argmax())
 pairs.append({'pair':[a,z],'conservative_body_gap_px':float(d[k]),'min_gap_time_s':k/24,'opaque_overlap_frames':int((o>0).sum()),'total_overlap_pixels_across_frames':int(o.sum()),'max_overlap_pixels':int(o.max()),'max_overlap_time_s':ko/24,'source_frames_at_max_overlap':[int(idx[a][ko]),int(idx[z][ko])]})
gr=json.loads((G/'green-tracking.json').read_text())['rows'];br=json.loads((B/'blue-tracking.json').read_text())['rows']
result={'status':'no opaque overlap found' if sum(p['opaque_overlap_frames'] for p in pairs)==0 else 'NO PASS: opaque overlap remains','period_seconds':45.5,'fps':24,'frames_checked':1092,'phases_source_frames':dict(zip(idx,[g,r,y,b])),'phases_source_seconds':dict(zip(idx,[g/24,r/24,y/24,b/24])),'blue_phase_output_seconds':b/480*45.5,'pairs':pairs,'opening_cab_px':{c:(br if c=='blue' else gr)[int(j[0])]['cab_px'] for c,j in idx.items()},'search':{'green_opening_anchor':'unrestricted','source_phase_lattice_stride':3,'valid_far3_combinations_min4px':len(comb),'green_opening_candidates':len(starts),'blue_opening_candidates':len(bstarts),'local_refinement':'all eligible +-3 integer source frames around coarse four-phase winner','coverage':'bounded coarse lattice and local exact search, not a mathematical impossibility proof'},'geometry_reference':'refined-phase-report.json geometry/assumptions; same actual alpha pixel and contour matrices','limitations':['Far3 uses actual green geometry for future red/yellow; newly generated appearance edits must be rechecked.','Clearance includes all opaque alpha, including extraction fringes. Blue fringe cleanup may alter tiny intersections but has not been assumed.','Opaque no-overlap is not sufficient for comfortable visible spacing; enforce positive margin before acceptance.','Phases alone do not change lane positions or speed within source footage.']}
# Quantify soft alpha overlap at the final phases directly, no AABB false-positive.
mask=[]
for folder,count in [(G,546),(B,480)]:
 masks=[]
 for i in range(count):
  a=cv2.imread(str(folder/'rgba-frames'/f'{i+1:04}.png'),-1)[:,:,3]>16
  yy,xx=np.where(a);box=(xx.min(),yy.min(),xx.max(),yy.max());masks.append((box,a[box[1]:box[3]+1,box[0]:box[2]+1]))
 mask.append(masks)
for p in pairs:
 a,z=p['pair'];total=0;frames=0;maxp=0
 for ia,iz in zip(idx[a],idx[z]):
  ba,ma=mask[0][ia];bz,mz=mask[1 if z=='blue' else 0][iz];x0=max(ba[0],bz[0]);x1=min(ba[2],bz[2]);y0=max(ba[1],bz[1]);y1=min(ba[3],bz[3]);v=0
  if x1>=x0 and y1>=y0:v=int((ma[y0-ba[1]:y1-ba[1]+1,x0-ba[0]:x1-ba[0]+1]&mz[y0-bz[1]:y1-bz[1]+1,x0-bz[0]:x1-bz[0]+1]).sum())
  total+=v;frames+=v>0;maxp=max(maxp,v)
 p.update(soft_overlap_frames=int(frames),soft_overlap_pixels_across_frames=int(total),max_soft_overlap_pixels=int(maxp))
(OUT/'final-phase-report.json').write_text(json.dumps(result,indent=2))
base=cv2.imread(str(ROOT/'design/scene-01/kling-layer-extract-2026-10-05/empty-map-padded.png'));colors={'green':(60,165,35),'red':(40,50,225),'yellow':(30,205,245),'blue':(230,125,35)}
times=sorted(set([0,1091]+[int(p['max_overlap_time_s']*24) for p in pairs]+[int(p['min_gap_time_s']*24) for p in pairs]+list(range(0,1092,120))));tiles=[]
for k in times:
 frame=base.copy();layers={}
 for c,j in idx.items():
  source=B if c=='blue' else G;i=int(j[k]);a=cv2.imread(str(source/'rgba-frames'/f'{i+1:04}.png'),-1);layers[c]=a;alpha=a[:,:,3:4]/255;frame=(a[:,:,:3]*alpha+frame*(1-alpha)).astype('uint8')
  contours,_=cv2.findContours((a[:,:,3]>127).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(frame,contours,-1,colors[c],2)
  cab=(br if c=='blue' else gr)[i]['cab_px'];cv2.putText(frame,c,(int(cab[0])+10,int(cab[1])-10),0,.4,colors[c],1,cv2.LINE_AA)
 cv2.putText(frame,f't={k/24:.3f}s | green geometry proxies for red/yellow | NOT PASS',(10,20),0,.45,(25,25,25),1)
 if k==0:cv2.imwrite(str(OUT/'final-opening.png'),frame)
 tiles.append(cv2.resize(frame,(640,360)))
 for p in pairs:
  if p['max_overlap_pixels'] and int(p['max_overlap_time_s']*24)==k:
   a,z=p['pair'];hit=(layers[a][:,:,3]>127)&(layers[z][:,:,3]>127);ys,xs=np.where(hit);x=max(0,int(xs.mean())-130);y=max(0,int(ys.mean())-130);tile=frame[y:y+260,x:x+260].copy();tile[hit[y:y+260,x:x+260]]=(255,0,255);cv2.imwrite(str(OUT/f'overlap-{a}-{z}.png'),cv2.resize(tile,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
while len(tiles)%3:tiles.append(np.full_like(tiles[0],245))
cv2.imwrite(str(OUT/'final-contact-sheet.png'),np.vstack([np.hstack(tiles[i:i+3]) for i in range(0,len(tiles),3)]))
print(json.dumps(result,indent=2),flush=True)
