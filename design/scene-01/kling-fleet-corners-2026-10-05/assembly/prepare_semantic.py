"""Consume verified source RGB+SAM2 alpha. Project local jobs premultiplied into the common city camera."""
from pathlib import Path
import argparse,json,cv2,numpy as np
cv2.setNumThreads(1)
r=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('color');p.add_argument('segment');p.add_argument('input_directory');args=p.parse_args();color,seg=args.color,args.segment;inp=Path(args.input_directory).resolve();out=r/'semantic-layers'/f'{color}-{seg}';out.mkdir(parents=True,exist_ok=True);rd=out/'rgba-frames';rd.mkdir(exist_ok=True)
tracks=json.loads((r/'source-roof-tracking'/f'{color}-{seg}.json').read_text());M=np.array(tracks['projection'],np.float32);local=seg in ['1-mid','mid-2'];empty=cv2.imread(str(r.parents[1]/'four-truck-loop-2026-10-04/v2b-empty-map.png'));base=np.full((720,1280,3),255,np.uint8);base[:,121:1158]=cv2.resize(empty,(1037,720),interpolation=cv2.INTER_LANCZOS4)
source=cv2.VideoCapture(str(r.parent/f'{color}-{seg}.mp4'));panels=[];metrics=[];bad=[]
for i in range(121):
 ok,f=source.read();assert ok;layer=cv2.imread(str(inp/f'{i:04d}.png'),cv2.IMREAD_UNCHANGED);assert layer is not None and layer.shape==(720,1280,4),(i,inp);mask=layer[:,:,3];same=np.array_equal(layer[:,:,:3][mask>0],f[mask>0]);assert same,('Source RGB mismatch',color,seg,i)
 # A soft one-pixel edge is only a matte feather; no erosion, hallucinated pixels or copied street shadow.
 alpha=cv2.GaussianBlur(mask.astype(np.float32)/255,(3,3),.5);alpha[mask==255]=1
 premul=f.astype(np.float32)*alpha[:,:,None]
 if local:alpha=cv2.warpAffine(alpha,M,(1280,720));premul=cv2.warpAffine(premul,M,(1280,720))
 rgb=np.divide(premul,alpha[:,:,None],out=np.zeros_like(premul),where=alpha[:,:,None]>1e-6);a=np.dstack((rgb.clip(0,255).round().astype(np.uint8),(alpha*255).round().astype(np.uint8)));cv2.imwrite(str(rd/f'{i:04d}.png'),a)
 cx,cy=np.array(tracks['rows'][i]['cab_px']).round().astype(int);cabalpha=int(a[cy,cx,3]);ys,xs=np.where(a[:,:,3]>127);metrics.append({'frame':i,'cab_roof_alpha':cabalpha,'opaque_pixels':int((a[:,:,3]>230).sum()),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]})
 if cabalpha<128:bad.append(i)
 if i%6==0:
  iso=(premul+230*(1-alpha[:,:,None])).clip(0,255).astype(np.uint8);comp=(premul+base*(1-alpha[:,:,None])).clip(0,255).astype(np.uint8);x=int(np.clip((xs.min()+xs.max())/2-100,0,1080));y=int(np.clip((ys.min()+ys.max())/2-90,0,540));tile=np.hstack([iso[y:y+180,x:x+200],comp[y:y+180,x:x+200]]);tile=cv2.resize(tile,(800,360),interpolation=cv2.INTER_NEAREST);cv2.putText(tile,f'{color} {seg} {i/24:.2f}s / isolated | city',(8,23),0,.6,(0,0,0),1);panels.append(tile)
source.release();cv2.imwrite(str(out/'quarter-alpha-composite.jpg'),np.vstack([np.hstack(panels[j:j+3]) for j in range(0,21,3)]));cv2.imwrite(str(out/'empty-map-padded.png'),base)
report={'source':str(r.parent/f'{color}-{seg}.mp4'),'semantic_rgba_source':str(inp),'source_rgb_exact_all121':True,'frames':121,'fps':24,'dimensions':[1280,720],'projection':M.tolist(),'added_ground_shadow':False,'edge_feather_sigma_px':.5,'cab_roof_alpha_failures':bad,'gate':'PENDING native quarter alpha/composite visual acceptance','metrics':metrics};(out/'gate-report.json').write_text(json.dumps(report,indent=2));print(color,seg,'projected121, cab roof alpha failures',bad,flush=True)
