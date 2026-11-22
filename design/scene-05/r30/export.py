"""Register painted vehicles, export r29-compatible WebPs, and check the map/hit-test contract.
Run: python export.py .tmp-work/scene5-r30 public/scene-art/lastmile-family-v1/revision-30
"""
import json,sys
from pathlib import Path
import cv2 as cv
import numpy as np
from PIL import Image,ImageDraw

work,dst=map(Path,sys.argv[1:3]); old=dst.with_name('revision-29'); dst.mkdir(exist_ok=True)
render=work/'locked'; paint=work/'paint'; review=work/'review'; review.mkdir(exist_ok=True)
base='scene-art/lastmile-family-v1/revision-30'; pal=json.loads((render/'palette.json').read_text()); A={}; Z={}; markers={}; report={}
vehicles=('helicopter','rover','pipe_carrier','robot'); hubs={'tall':(398,1516),'wide':(679,1308)}

def box_dict(x,y,w,h):return dict(x=int(x),y=int(y),w=int(w),h=int(h))
def ext(mask,margin=0):
    x,y,w,h=cv.boundingRect(mask);H,W=mask.shape; l,t=max(x-margin,0),max(y-margin,0)
    return l,t,min(x+w+margin,W)-l,min(y+h+margin,H)-t

def point(m):return cv.minMaxLoc(cv.distanceTransform(m,cv.DIST_L2,5))[3]
def save_sprite(img,filename,size):
    im=Image.fromarray(img,'RGBA').resize(size,Image.Resampling.LANCZOS);im.save(dst/filename,'WEBP',lossless=True,method=5)

def composite(path,v,motion):
    im=Image.open(path/f'choice-{v}.webp').convert('RGBA')
    for k,s in motion.items():
        layer=Image.open(path/f'{v}-{k}.webp').convert('RGBA');
        if k=='rotor':layer=layer.crop((0,0,layer.width//12,layer.height))
        im.alpha_composite(layer.resize((s['w'],s['h']),Image.Resampling.LANCZOS),(s['x'],s['y']))
    return im.convert('RGB')

for view in ('wide','tall'):
    art=np.array(Image.open(paint/f'{view}-master.png').convert('RGB'));H,W=art.shape[:2]
    ids=np.asarray(Image.open(render/f'{view}-id.png'));D={k:np.all(ids==c,axis=2).astype('uint8') for k,c in pal.items()}
    masks=dict(np.load(paint/f'{view}-masks.npz')); vs={}; regions={}; hotspots=[]; motion={}; checks={}
    for k in vehicles:
        vs[k]=masks[k]
        iou=(vs[k]&D[k]).sum()/(vs[k]|D[k]).sum();assert iou>.55,(view,k,iou)
        x,y,w,h=ext(vs[k]);a,b,c,d=ext(D[k]); offset=(round(x+(w-c)/2-a,1),round(y+(h-d)/2-b,1))
        assert abs(offset[0])<W*.015 and abs(offset[1])<H*.01,(view,k,offset)
        checks[k]={'idPaintIoU':round(iou,3),'paintBox':ext(vs[k]),'centerOffsetPx':offset}
        cx,cy=point(vs[k]);name=k.replace('_','-');hotspots.append(dict(id=name,x=cx/W,y=cy/H))
        # Accessibility padding without touching the adjacent vehicle. The pin stays inside the paint itself.
        mask=cv.morphologyEx(vs[k],cv.MORPH_CLOSE,np.ones((5,5),'uint8')); pad=10 if view=='tall' else 12
        mask=cv.dilate(mask,cv.getStructuringElement(cv.MORPH_ELLIPSE,(pad*2+1,pad*2+1)))
        contour=max(cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[0],key=cv.contourArea)
        contour=cv.approxPolyDP(contour,1,True);assert cv.pointPolygonTest(contour,(cx,cy),False)>=0
        for other in vehicles:
            if other!=k: assert not (mask&D[other]).any(),(view,k,other)
        regions[name]={'path':'M'+' L'.join(f'{x},{y}' for x,y in contour[:,0])+' Z'}
    # Protect the actual 0.57 m parcel instead of letting the generated red spot define its size.
    x,y,w,h=ext(D['gift']); l,t=x-13,y-10;ww,hh=w+38,h+25
    yy,xx=np.mgrid[:hh,:ww];opacity=np.clip(np.minimum.reduce([xx,ww-1-xx,yy,hh-1-yy])/6,0,1)[...,None]
    area=art[t:t+hh,l:l+ww];area[:]=np.rint(area*(1-opacity)+art[t:t+hh,l-42:l-42+ww]*opacity)
    raw=np.asarray(Image.open(render/f'{view}-neutral.png'));g=D['gift'].astype('float32');shadow=cv.GaussianBlur(np.roll(g,(2,2),axis=(0,1)),(0,0),1.1)[...,None]*.25
    art=np.rint(art*(1-shadow)).astype('uint8');alpha=cv.GaussianBlur(g,(0,0),.35)[...,None];art=np.rint(art*(1-alpha)+raw*alpha).astype('uint8')
    Image.fromarray(art).save(dst/f'choice-{view}.webp',quality=94,method=6)
    art=np.array(Image.open(dst/f'choice-{view}.webp').convert('RGB')); hsv=cv.cvtColor(art,cv.COLOR_RGB2HSV)
    # Ice is identified on the finished painting, limited to harbour water. Shores, ship and tundra excluded.
    harbor=cv.morphologyEx(D['harbor_water']|D['ice'],cv.MORPH_CLOSE,np.ones((7,7),'uint8'));harbor[:np.nonzero(D['harbor_water'])[0].min()]=0
    ice=((hsv[:,:,2]>154)&(hsv[:,:,1]<73)&(art[:,:,2]>=art[:,:,0])).astype('uint8') & harbor
    n,lab,stats,_=cv.connectedComponentsWithStats(ice);floes=np.zeros_like(ice)
    for j in range(1,n):
        x,y,w,h,a=stats[j]
        if not 22<a<7500 or w<5 or h<3 or w>h*5:continue
        sl=np.s_[max(0,y-2):min(H,y+h+2),max(0,x-2):min(W,x+w+2)];m=(lab[sl]==j).astype('uint8');ring=cv.dilate(m,np.ones((5,5),'uint8'))-m
        if (ring*D['harbor_water'][sl]).sum()>=.6*ring.sum():floes[sl]|=m
    for k,m in [('rover',vs['rover']),('pipe-carrier',vs['pipe_carrier']),('barge',masks['barge']),('floes',floes)]:
        x,y,w,h=ext(m,2);name=f'{view}-{k}.webp';alpha=cv.GaussianBlur(m*255,(3,3),.55)
        save_sprite(np.dstack((art[y:y+h,x:x+w],alpha[y:y+h,x:x+w])),name,Image.open(old/name).size)
        motion[k]={**box_dict(x,y,w,h),'image':f'{base}/{name}'}
    frames=[np.array(Image.open(render/f'{view}-blade-{i:02}.png')) for i in range(12)]
    al=np.stack([im[:,:,3] for im in frames]);y0,x0=np.nonzero(al.min(axis=0)>25);ox,oy=round(x0.mean()),round(y0.mean());x,y,w,h=ext((al.max(axis=0)>3).astype('uint8'),2)
    name=f'{view}-rotor.webp';sw,sh=Image.open(old/name).size;strip=Image.new('RGBA',(sw,sh));
    # Brief exposure over neighbouring true poses softens the rotating blades, as on r29.
    rgbas=[np.asarray(Image.fromarray(im[y:y+h,x:x+w]).resize((sw//12,sh),Image.Resampling.LANCZOS)).astype(np.float32)/255 for im in frames]
    pm=[np.dstack((f[:,:,:3]*f[:,:,3:],f[:,:,3])) for f in rgbas]
    for i in range(12):
        f=.6*pm[i]+.2*pm[(i+1)%12]+.2*pm[(i-1)%12]; fg=np.dstack((f[:,:,:3]/np.maximum(f[:,:,3:],1e-5),f[:,:,3]))
        strip.paste(Image.fromarray((fg.clip(0,1)*255).round().astype('uint8')),(i*sw//12,0))
    painted_hub=hubs[view]
    strip.save(dst/name,lossless=True,method=6);motion['rotor']={**box_dict(x+painted_hub[0]-ox,y+painted_hub[1]-oy,w,h),'frames':12,'image':f'{base}/{name}'}
    # Flood on finished water colours independently; bounded search excludes blue roofs/vehicles, not gaps in water.
    wet=(D['river']|D['ice']);wet[np.nonzero(D['harbor_water'])[0].min():]=0
    blue=((hsv[:,:,0]>=89)&(hsv[:,:,0]<=126)&(hsv[:,:,1]>48)&(hsv[:,:,2]>62)).astype('uint8')
    allowed=cv.dilate(wet,np.ones((37,37),'uint8'));painted=(blue|((hsv[:,:,1]<45)&(hsv[:,:,2]>193)).astype('uint8'))&allowed
    # Fill anti-aliased colour boundaries (1 px) on the contiguous channel; no inferring or painting a crossing.
    painted=cv.morphologyEx(painted,cv.MORPH_CLOSE,np.ones((3,3),'uint8'))
    for n,m in [('id',wet),('paint',painted)]:
        _,lands=cv.connectedComponents(1-m,connectivity=8);parts={k:int(lands[point(D[k])[1],point(D[k])[0]]) for k in ('chums','gift','abk')}
        assert parts['chums'] not in (parts['gift'],parts['abk'],0),(view,n,parts)
        checks[n+'DryLandComponents']=parts
    framing=vs['helicopter']|D['chums']|D['industry']|D['helipad']|D['abk']|D['helideck']|D['gift']|masks['barge']|vs['robot']; fx,fy,fw,fh=ext(framing,16)
    A[view]=dict(width=W,height=H,original=dict(x=fx,y=fy,width=fw,height=fh),framing=[dict(x=fx/W,y=fy/H),dict(x=(fx+fw)/W,y=(fy+fh)/H)],hotspots=hotspots,motion=motion)
    Z[view]=dict(width=W,height=H,source=f'{base}/choice-{view}.webp',regions=regions)
    markers[view]={}
    for k in ('gift','chums','abk','helipad','industry','reindeer','windsock'):
        px,py=point(D[k]);markers[view][k]={'px':[px,py],'x':px/W,'y':py/H,'bounds':ext(D[k])}
    checks['giftPixelBox']=ext(D['gift']);checks['rotorHub']=painted_hub;checks['floesPixels']=int(floes.sum());report[view]=checks
    overlay=art.copy()
    for k in ('chums','abk','industry','helipad','river','gift',*vehicles):cv.drawContours(overlay,cv.findContours(D[k],cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[0],-1,(0,235,146),1)
    for k in vehicles:cv.drawContours(overlay,cv.findContours(vs[k],cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[0],-1,(255,66,125),1)
    Image.fromarray(overlay).resize((W//2,H//2)).save(review/f'{view}-id-overlay.jpg',quality=92)
    # r29 already bakes the static vehicles into the plate; add only its first rotor cell.
    oldrot=(602,943,257,195) if view=='wide' else (508,1210,170,155)
    oldim=composite(old,view,{'rotor':box_dict(*oldrot)}); final=composite(dst,view,motion);final.save(review/f'{view}-frame0.png')
    rw,rh=W//2,H//2;sheet=Image.new('RGB',(rw*2,rh+34),'#243744');draw=ImageDraw.Draw(sheet)
    for j,(title,im) in enumerate([('r29 / '+view,oldim),('r30 / '+view,final)]):draw.text((j*rw+8,9),title,fill='white');sheet.paste(im.resize((rw,rh),Image.Resampling.LANCZOS),(j*rw,34))
    sheet.save(review/f'r29-r30-{view}.jpg',quality=91)

assert {p.name for p in old.glob('*.webp')}=={p.name for p in dst.glob('*.webp')}
for p in old.glob('*.webp'):
    im=Image.open(dst/p.name);assert im.format=='WEBP' and im.size==Image.open(p).size;im.load()
metadata=dict(expandedArtwork=A,segmentedContours=Z,landmarks=markers)
(dst/'layout.json').write_text(json.dumps(metadata,indent=2)+'\n');(review/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
