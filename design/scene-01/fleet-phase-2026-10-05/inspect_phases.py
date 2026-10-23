from pathlib import Path
import json, itertools
import cv2, numpy as np

cv2.setNumThreads(1)
ROOT=Path('/home/michael/Github/energy-plus-quest')
OUT=Path(__file__).resolve().parent
G=ROOT/'design/scene-01/kling-green-loop-2026-10-05/assembly/candidate-22.75s'
B=ROOT/'design/scene-01/kling-blue-keys-2026-10-05/assembly/candidate-20s'

def extract(folder, tracking):
    rows=json.loads((folder/tracking).read_text())['rows']; boxes=[]; outer=[]; straight=[]; axes=[]
    for i,row in enumerate(rows):
        a=cv2.imread(str(folder/'rgba-frames'/f'{i+1:04}.png'),-1)
        alpha=a[:,:,3]; hsv=cv2.cvtColor(a[:,:,:3],cv2.COLOR_BGR2HSV)
        def bounds(mask):
            y,x=np.where(mask); return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]
        boxes.append(bounds(alpha>127));outer.append(bounds(alpha>16))
        trailer=((alpha>127)&(hsv[:,:,1]<65)&(hsv[:,:,2]>160)).astype('uint8')
        n,labels,stats,cent=cv2.connectedComponentsWithStats(trailer)
        j=1+np.argmax(stats[1:,4]); yy,xx=np.where(labels==j); pts=np.column_stack([xx,yy])
        cov=np.cov(pts.T); _,vec=np.linalg.eigh(cov); axis=vec[:,-1]
        cab=np.array(row['cab_px']); v=cab-cent[j]; v=v/np.linalg.norm(v)
        articulation=np.degrees(np.arccos(np.clip(abs(v@axis),0,1)))
        cardinal=np.degrees(np.arccos(np.clip(max(abs(axis)),0,1)))
        straight.append(bool(articulation<=8 and cardinal<=12));axes.append([float(articulation),float(cardinal)])
    return np.array(boxes),np.array(outer),np.array(straight),axes,rows

def gap(a,b):
    dx=np.maximum(np.maximum(a[...,0]-b[...,2],b[...,0]-a[...,2]),0)
    dy=np.maximum(np.maximum(a[...,1]-b[...,3],b[...,1]-a[...,3]),0)
    return np.hypot(dx,dy)

gb,go,gs,ga,gr=extract(G,'green-tracking.json');bb,bo,bs,ba,br=extract(B,'blue-tracking.json')
np.savez(OUT/'envelopes.npz',green=gb,green_soft=go,blue=bb,blue_soft=bo,green_straight=gs,blue_straight=bs)
ng=len(gb);nb=len(bb);n=np.arange(1092); gi=n%ng
selfgap=np.array([gap(gb,np.roll(gb,-d,axis=0)).min() for d in range(ng)])
selfsoft=np.array([gap(go,np.roll(go,-d,axis=0)).min() for d in range(ng)])
cross=gap(gb[:,None,:],bb[None,:,:]); crosssoft=gap(go[:,None,:],bo[None,:,:])
def stable(a):return a & np.roll(a,3)&np.roll(a,-3)
gp=np.where(stable(gs))[0][::6];bp=np.where(stable(bs))[0][::6]
# Green opening fixed at its original straight key; red/yellow are phase copies of actual green geometry.
gp=np.unique(np.r_[0,gp]);gp=gp[gp!=0]
best=None
for blue in bp:
    bi=(np.floor(n*nb/1092).astype(int)+blue)%nb
    cg=np.array([cross[(gi+p)%ng,bi].min() for p in np.r_[0,gp]])
    cs=np.array([crosssoft[(gi+p)%ng,bi].min() for p in np.r_[0,gp]])
    for i,p in enumerate(gp):
        q=gp[i+1:]
        if not len(q):continue
        scores=np.minimum.reduce([np.full(len(q),cg[0]),np.full(len(q),cg[i+1]),cg[i+2:],np.full(len(q),selfgap[p]),selfgap[q],selfgap[(q-p)%ng]])
        k=int(np.argmax(scores)); score=float(scores[k]); yellow=int(q[k])
        soft=float(min(cs[0],cs[i+1],cs[i+2+k],selfsoft[p],selfsoft[yellow],selfsoft[(yellow-p)%ng]))
        candidate=(score,soft,int(p),yellow,int(blue))
        if best is None or candidate[:2]>best[:2]:best=candidate
print('BEST',best,flush=True)
score,soft,r,y,b=best
indices={'green':gi,'red':(gi+r)%ng,'yellow':(gi+y)%ng,'blue':(np.floor(n*nb/1092).astype(int)+b)%nb}
boxes={'green':gb,'red':gb,'yellow':gb,'blue':bb};softboxes={'green':go,'red':go,'yellow':go,'blue':bo}
pairs=[]
for x,z in itertools.combinations(indices,2):
    dist=gap(boxes[x][indices[x]],boxes[z][indices[z]]);ds=gap(softboxes[x][indices[x]],softboxes[z][indices[z]])
    k=int(dist.argmin());ks=int(ds.argmin())
    pairs.append({'pair':[x,z],'opaque_aabb_min_gap_px':float(dist[k]),'opaque_min_time_s':k/24,'soft_aabb_min_gap_px':float(ds[ks]),'soft_min_time_s':ks/24,'opaque_box_overlap_frames':int((dist==0).sum()),'soft_box_overlap_frames':int((ds==0).sum()),'source_frames_at_opaque_min':[int(indices[x][k]),int(indices[z][k])]})
result={'period_seconds':45.5,'output_fps':24,'output_frames':1092,'green_source_frames':ng,'blue_source_frames':nb,'phases_source_frames':{'green':0,'red':r,'yellow':y,'blue':b},'phases_source_seconds':{'green':0,'red':r/24,'yellow':y/24,'blue':b/24},'blue_phase_output_seconds':b/480*45.5,'minimum_opaque_aabb_gap_px':score,'minimum_soft_aabb_gap_px':soft,'pairs':pairs,'opening_geometry':{c:{'source_frame':int(idx[0]),'cab_px':(br if c=='blue' else gr)[int(idx[0])]['cab_px'],'articulation_deg':(ba if c=='blue' else ga)[int(idx[0])][0],'trailer_cardinal_deviation_deg':(ba if c=='blue' else ga)[int(idx[0])][1]} for c,idx in indices.items()},'search':{'green_anchor_frame':0,'green_start_candidates':len(gp)+1,'blue_start_candidates':len(bp),'candidate_stride':6,'straight_max_articulation_deg':8,'straight_max_cardinal_deviation_deg':12,'stability_neighbor_frames':3,'method':'maximin distance between all-alpha-threshold AABBs at every 24fps output frame; no translation or route editing'},'assumptions':['Red and yellow use green frame geometry with phase only; future generated videos may differ and must be revalidated.','Alpha above127 for opaque envelope, above16 for soft envelope; all alpha pixels included, including extraction fringe.','AABB envelopes include all cab/trailer pixels; AABB separation is sufficient for no alpha overlap and conservative for articulated vehicles.','Blue uses whole20s source slowed to45.5s, floor source-frame sampling, phase in source frames.','Rendered poses, not native route coordinates; no physical world collision claim.']}
(OUT/'phase-report.json').write_text(json.dumps(result,indent=2))
# Diagnostic colored proxy contours use green actual alpha for red/yellow, not fabricated appearance footage.
base=cv2.imread(str(ROOT/'design/scene-01/kling-layer-extract-2026-10-05/empty-map-padded.png'))
times=sorted(set([0,1091]+[int(p['opaque_min_time_s']*24) for p in pairs]+list(range(0,1092,120))))
colors={'green':(60,165,35),'red':(40,50,225),'yellow':(30,205,245),'blue':(230,125,35)}
tiles=[]
for k in times:
    frame=base.copy()
    for c,idx in indices.items():
        src=B if c=='blue' else G;i=int(idx[k]);a=cv2.imread(str(src/'rgba-frames'/f'{i+1:04}.png'),-1)
        alpha=a[:,:,3:4]/255;frame=(a[:,:,:3]*alpha+frame*(1-alpha)).astype('uint8')
        contours,_=cv2.findContours((a[:,:,3]>127).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(frame,contours,-1,colors[c],2)
        cab=(br if c=='blue' else gr)[i]['cab_px']; cv2.putText(frame,c,(int(cab[0])+10,int(cab[1])-10),0,.4,colors[c],1,cv2.LINE_AA)
    cv2.putText(frame,f't={k/24:.3f}s | green/red/yellow use observed green geometry',(10,20),0,.45,(25,25,25),1)
    if k==0:cv2.imwrite(str(OUT/'opening-diagnostic.png'),frame)
    tiles.append(cv2.resize(frame,(640,360)))
while len(tiles)%3:tiles.append(np.full_like(tiles[0],245))
sheet=np.vstack([np.hstack(tiles[i:i+3]) for i in range(0,len(tiles),3)])
cv2.imwrite(str(OUT/'diagnostic-contact-sheet.png'),sheet)
print(json.dumps(result,indent=2),flush=True)
