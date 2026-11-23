"""Local finishing on the approved r30 plates; no regeneration of untouched scenery.
Run from checkout root with the ComfyUI venv. Requires the inspected RGBA sheet.
"""
from bend import finish_bend
from quay import move_crane
from io import BytesIO
from pathlib import Path
import json, shutil
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

root = Path('public/scene-art/lastmile-family-v1')
old, dst = root/'revision-30', root/'revision-31'
src = Path('.tmp-work/scene5-r30'); work = Path('.tmp-work/scene5-r31'); review = work/'review'
dst.mkdir(exist_ok=True); review.mkdir(exist_ok=True)
layout = json.loads((old/'layout.json').read_text().replace('revision-30/', 'revision-31/'))
palette = json.loads((src/'locked/palette.json').read_text())
details = Image.open(work/'paint/details-1.png').convert('RGBA'); pieces = {}
keys = ['helicopter','rover','pipe-carrier','gift']
for i,key in enumerate(keys):
    x,y=i%2*768,i//2*512
    piece=details.crop((x,y,x+768,y+512)); alpha=piece.getchannel('A').point(lambda a: 0 if a<26 else min(255,round(a*255/253)))
    piece.putalpha(alpha); pieces[key]=piece.crop(alpha.getbbox())

# Inner-bank traces at both confluences. Clone matching r30 tundra through the retired channel;
# the winding outer arm on the far left and the icy crossing at the end of the tyre tracks stay.
views = {
    'wide': dict(cut=[(995,294),(1070,282),(1137,274),(1181,264),(1242,238),(1285,221),(1290,309),(920,591),(771,672),(710,657),(704,640),(686,620),(655,606),(612,595),(570,585),(515,573),(503,540),(755,369)],
        oldrig=(1810,130,2088,379), newrig=(1344,231,225,202), rigdonor=-310, rigoutline=[(1967,145),(2003,141),(1984,284),(2043,285),(2054,301),(2050,321),(2090,350),(2077,362),(1852,365),(1825,328),(1826,282),(1922,282)],
        objects=[(512,1254,263,142),(876,1312,157,86),(1120,1300,196,109),(1119,1452,55,58)],
        hub=(679,1308), camp=(438,340,178,101), herd=(621,388,125,67)),
    'tall': dict(cut=[(610,388),(690,380),(747,372),(799,362),(845,347),(900,319),(931,303),(950,389),(620,637),(468,810),(397,800),(390,775),(379,754),(361,740),(333,729),(301,721),(260,713),(220,701),(210,663),(424,425)],
        oldrig=(1394,246,1698,489), newrig=(979,335,247,199), rigdonor=-315, rigoutline=[(1533,257),(1571,252),(1552,387),(1601,386),(1622,409),(1617,424),(1694,420),(1690,461),(1424,469),(1407,439),(1406,386),(1499,387)],
        objects=[(229,1463,238,137),(545,1515,150,84),(755,1506,183,104),(755,1661,52,55)],
        hub=(398,1516), camp=(149,460,159,95), herd=(314,512,85,49)),
}

def marker(bounds):
    x,y,w,h=bounds; px,py=x+w//2,y+h//2
    return dict(px=[px,py],x=px/W,y=py/H,bounds=bounds)

def topology(mask):
    _,land=cv.connectedComponents(1-mask, connectivity=8)
    parts={k:int(land[marks[k]['px'][1],marks[k]['px'][0]]) for k in ('gift','chums','reindeer','helipad','abk','industry')}
    assert parts['chums'] and all(parts[k]==parts['chums'] for k in ('reindeer','helipad','abk','industry')), (view,parts)
    assert parts['gift'] not in (0,parts['chums']), (view,parts)
    return parts

checks={}
for view,v in views.items():
    art=Image.open(old/f'choice-{view}.webp').convert('RGB'); W,H=art.size
    expanded=layout['expandedArtwork'][view]; regions=layout['segmentedContours'][view]['regions']; marks=layout['landmarks'][view]; motion=expanded['motion']
    # Copy the rig, including its original daylight and shadow, before restoring the empty old site.
    x,y,r,b=v['oldrig']; patch=art.crop((x,y,r,b)); dx=v['rigdonor']
    outline=Image.new('L',art.size);ImageDraw.Draw(outline).polygon(v['rigoutline'],fill=255)
    patchmask=outline.crop((x,y,r,b)).filter(ImageFilter.GaussianBlur(4))
    art.paste(art.crop((x+dx,y,r+dx,b)),(x,y),patchmask)
    cut=Image.new('L',art.size);ImageDraw.Draw(cut).polygon(v['cut'],fill=255); mask=cut.filter(ImageFilter.GaussianBlur(3))
    ids=np.array(Image.open(src/f'locked/{view}-id.png'));original=np.uint8(np.all(ids==palette['river'],axis=-1)|np.all(ids==palette['ice'],axis=-1))
    corridor=cv.dilate(original,np.ones((43,43),'uint8'));mask=Image.fromarray(np.minimum(np.array(mask),corridor*255)).filter(ImageFilter.GaussianBlur(1))
    # Sample tundra at the same depth, in reverse x to preserve brush shape without duplicating a landmark.
    a,b,c,d=mask.getbbox();samples=np.array(art); yy,xx=np.mgrid[b:d,a:c];sourceX=(2860 if view=='wide' else 1880)-xx
    art.paste(Image.fromarray(samples[yy,sourceX]),(a,b),mask.crop((a,b,c,d)))
    nx,ny,nw,nh=v['newrig'];art.paste(patch.resize((nw,nh),Image.Resampling.LANCZOS),(nx,ny),patchmask.resize((nw,nh)))
    ox,oy,ow,oh=marks['industry']['bounds']; sx,sy=nw/(r-x),nh/(v['oldrig'][3]-y)
    marks['industry']=marker([round(nx+(ox-x)*sx),round(ny+(oy-y)*sy),round(ow*sx),round(oh*sy)])
    marks['chums']=marker(v['camp']);marks['reindeer']=marker(v['herd'])
    oldMasks=np.load(src/f'paint/{view}-masks.npz'); oldPaint=np.array(art)
    erase=np.zeros((H,W),'uint8')
    for k in keys[:3]:erase |= oldMasks[k.replace('-','_')]
    # r30's SAM omits thin tail blades and the ends of the wheels. Clear those painted fragments too.
    for cx,cy,rx,ry in ([(510,1276,20,23),(651,1384,11,10),(723,1403,9,11),(678,1383,7,9)] if view=='wide' else [(224,1493,18,24),(359,1590,12,12),(446,1600,9,9)]):
        cv.ellipse(erase,(cx,cy),(rx,ry),0,0,360,1,-1)
    # Remove the old silhouettes, leaving their quay contact shadows and the painted pad intact.
    erase=cv.dilate(erase,np.ones((7,7),'uint8')); art=Image.fromarray(cv.inpaint(oldPaint,erase,4,cv.INPAINT_TELEA))
    newMasks={};hitMasks=[]
    for k,(left,top,w,h) in zip(keys,v['objects']):
        layer=pieces[k].resize((w,h),Image.Resampling.LANCZOS);alpha=layer.getchannel('A');m=(np.array(alpha)>90).astype('uint8'); xx,yy,ww,hh=cv.boundingRect(m)
        if k=='gift':
            art.paste('#6c6664',(left+5,top+4,left+w+5,top+h+4),alpha.filter(ImageFilter.GaussianBlur(2)).point(lambda a: a*.56))
            marks['gift']=marker([left+xx,top+yy,ww,hh])
        art.paste(layer,(left,top),alpha)
        if k=='gift':continue
        full=np.zeros((H,W),'uint8');full[top:top+h,left:left+w]=m;newMasks[k]=full
        inset=12 if view=='wide' else 10
        padded=cv.dilate(full,cv.getStructuringElement(cv.MORPH_ELLIPSE,(inset*2+1,inset*2+1)))
        contour=max(cv.findContours(padded,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)[0],key=cv.contourArea)
        contour=cv.approxPolyDP(contour,1,True);regions[k]={'path':'M'+' L'.join(f'{x},{y}' for x,y in contour[:,0])+' Z'}
        cx,cy=cv.minMaxLoc(cv.distanceTransform(full,cv.DIST_L2,5))[3]; assert cv.pointPolygonTest(contour,(cx,cy),False)>0
        assert not (padded & oldMasks['robot']).any() and all(not (padded & hm).any() for hm in hitMasks); hitMasks.append(padded)
        hotspot=next(it for it in expanded['hotspots'] if it['id']==k);hotspot.update(x=cx/W,y=cy/H)
    # Derive the static vehicle sprites from the original r31 encode. Re-encoding an unrelated
    # WebP region can change quantization elsewhere; the accepted sprites must stay byte-identical.
    base=BytesIO();art.save(base,format='WEBP',quality=94,method=6);base.seek(0)
    sprite_art=Image.open(base).convert('RGB')
    for k in ('rover','pipe-carrier'):
        x,y,w,h=cv.boundingRect(newMasks[k]); x-=2;y-=2;w+=4;h+=4
        layer=sprite_art.crop((x,y,x+w,y+h)).convert('RGBA');layer.putalpha(Image.fromarray(newMasks[k][y:y+h,x:x+w]*255).filter(ImageFilter.GaussianBlur(.5)))
        name=f'{view}-{k}.webp';layer.resize(Image.open(old/name).size,Image.Resampling.LANCZOS).save(dst/name,lossless=True,method=5)
        motion[k].update(x=x,y=y,w=w,h=h)
    finish_bend(art,view,Image.open(work/'paint/bend-1.png').convert('RGB'))
    if view=='wide': marks['crane']=marker(move_crane(art))
    art.save(dst/f'choice-{view}.webp',quality=94,method=6)
    art=Image.open(dst/f'choice-{view}.webp').convert('RGB')
    # Hub measured in returned full RGBA sheet, not the centre of its matted bounding rectangle.
    x,y,w,h=v['objects'][0]; hub=(round(x+(475-44)/661*w),round(y+(163-79)/356*h));ox,oy=v['hub']
    motion['rotor']['x']+=hub[0]-ox;motion['rotor']['y']+=hub[1]-oy
    for k in ('rotor','barge','floes'):shutil.copyfile(old/f'{view}-{k}.webp',dst/f'{view}-{k}.webp')
    boxes=[m['bounds'] for m in marks.values()]+[tuple(motion[k][i] for i in 'xywh') for k in ('rotor','barge')]
    left=min(bb[0] for bb in boxes)-16;top=min(bb[1] for bb in boxes)-16;right=max(bb[0]+bb[2] for bb in boxes)+16;bottom=max(bb[1]+bb[3] for bb in boxes)+16
    expanded.update(original=dict(x=left,y=top,width=right-left,height=bottom-top),framing=[dict(x=left/W,y=top/H),dict(x=right/W,y=bottom/H)])
    wet=original.copy();wet[H*2//3:]=0;wet[np.array(cut)>0]=0
    # Independent check on decoded final colours across the *whole* route. Sky-blue roofs and isolated bog pools may be wet by this classifier, but cannot divide dry-land components.
    rgb=np.array(Image.open(dst/f'choice-{view}.webp').convert('RGB'));hsv=cv.cvtColor(rgb,cv.COLOR_RGB2HSV);h,s,val=cv.split(hsv)
    painted=np.uint8(((h>=89)&(h<=126)&(s>48)&(val>62))|((s<45)&(val>193)));painted[H*2//3:]=0
    # Do not treat buildings as water: restrict to the ORIGINAL r30 river corridor, including the removed branch.
    painted &= cv.dilate(original,np.ones((39,39),'uint8'));painted=cv.morphologyEx(painted,cv.MORPH_CLOSE,np.ones((3,3),'uint8'))
    checks[view]=dict(idDryLandComponents=topology(wet),paintDryLandComponents=topology(painted),giftBounds=marks['gift']['bounds'],industryBounds=marks['industry']['bounds'],rotorHub=hub)
    frame=art.convert('RGBA');rot=motion['rotor'];strip=Image.open(dst/f'{view}-rotor.webp'); frame.alpha_composite(strip.crop((0,0,strip.width//12,strip.height)).resize((rot['w'],rot['h']),Image.Resampling.LANCZOS),(rot['x'],rot['y']));frame.convert('RGB').save(review/f'{view}-frame0.jpg',quality=96)
    print(view,checks[view],flush=True)
assert {f.name for f in old.glob('*.webp')}=={f.name for f in dst.glob('*.webp')}
for f in dst.glob('*.webp'): assert Image.open(f).size==Image.open(old/f.name).size
(dst/'layout.json').write_text(json.dumps(layout,indent=2)+'\n');(review/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
