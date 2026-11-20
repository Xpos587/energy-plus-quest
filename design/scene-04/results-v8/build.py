"""Rebuild the Scene 4 result candidates from local, already painted game art.
Run with ~/.local/share/comfyui/venv/bin/python build.py (no GPU required).
Coordinates are native pixels of the current two orthographic camera angles.
"""
from pathlib import Path
import numpy as np
import cv2 as cv
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ART = HERE.parents[1] / 'public/scene-art'
SRC = ART / 'barge-v7'
DEST = HERE / 'candidates'
QA = HERE / 'review'
DEST.mkdir(exist_ok=True); QA.mkdir(exist_ok=True)
FORMATS = {'wide':'','tall':'-portrait','mid':'-rail'}
BOX = {'wide':(2610,375,3070,925),'tall':(1090,690,1510,1370)}
OFFICE={'wide':(685,904,1110,1409),'tall':(355,2435,780,2940)}
FAR={'wide':(1547,1070,1847,1390),'tall':(953,2115,1253,2435)}

def rgb(p): return Image.open(p).convert('RGB')
def source(f,b): return rgb(SRC / f'outcome-{b}{FORMATS[f]}.webp')
def mask(size,pts,blur=0):
    m=Image.new('L',size); ImageDraw.Draw(m).polygon(pts,fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m

def aff(im, m, size):
    a=np.asarray(im); res=cv.warpAffine(a,np.asarray(m,np.float64),size,flags=cv.INTER_CUBIC)
    return Image.fromarray(res)

def place(im, anchor, scale, size):
    x,y=anchor; sx,sy=scale if isinstance(scale,tuple) else (scale,scale)
    if min(sx,sy)<.5: # low-pass the painted figure before reducing it to cab scale
        small=im.resize((round(im.width*sx),round(im.height*sy)),Image.Resampling.LANCZOS)
        dst=Image.new(im.mode,size);dst.paste(small,(round(x),round(y)));return dst
    return aff(im,[[sx,0,x],[0,sy,y]],size)

def mix(dst,src,pts,blur=0): dst.paste(src,(0,0),mask(dst.size,pts,blur))
def quad(x,y,r,b):return [(x,y),(r,y),(r,b),(x,b)]

def alpha(im):return im.getchannel('A')
def overlay(dst,fg):dst.paste(fg,(0,0),alpha(fg))

def translated(im,dx,dy): return aff(im,[[1,0,dx],[0,1,dy]],im.size)

def heal(base, donor, points):
    m=np.asarray(mask(base.size,points));x,y,w,h=cv.boundingRect(m)
    return Image.fromarray(cv.seamlessClone(np.asarray(donor),np.asarray(base),m, (x+w//2,y+h//2),cv.NORMAL_CLONE))

def bridge(im,x0,x1,slope):
    # Draw through an obstruction with intact edge colours from the two ends.
    # Each donor is a single affine stretch of a clean 5px strip, never a mesh/flow warp.
    w,h=im.size;k=5/(x1-x0); cols=[]
    for x in (x0-5, x1):
        T=np.float32([[k,0,x-k*x0],[slope*(k-1),1,slope*(x-k*x0)]])
        cols.append(np.asarray(aff(im,cv.invertAffineTransform(T),im.size)).astype('float32'))
    a=np.clip((np.arange(w)-x0)/(x1-x0),0,1)[None,:,None]
    return Image.fromarray(np.uint8(cols[0]*(1-a)+cols[1]*a))

def actor(petr=False):
    # Ivan already seated, elbows bent, hand on joystick, from the family painting.
    pic=rgb(ART/'barge-family-v1/outcome-remote-neutral-v1.webp').crop((0,0,570,934))
    p=[(42,419),(51,332),(63,315),(84,310),(112,311),(138,323),(150,342),(154,367),(165,366),(166,351),(174,342),(190,340),(207,346),(215,344),(212,332),(205,336),(207,316),(191,318),(187,311),(194,305),(194,280),(202,255),(211,236),(224,223),(243,212),(266,205),(289,204),(314,208),(334,219),(342,230),(350,260),(367,263),(374,266),(374,270),(353,279),(341,282),(348,294),(344,301),(341,306),(342,315),(354,329),(353,333),(345,338),(342,351),(337,356),(340,364),(338,374),(332,379),(310,377),(298,385),(300,391),(322,399),(323,408),(316,423),(327,445),(335,469),(346,487),(351,506),(374,508),(381,515),(405,502),(415,499),(422,491),(436,490),(445,496),(448,504),(445,514),(438,518),(439,526),(430,534),(429,546),(423,551),(419,551),(424,558),(432,561),(433,569),(420,576),(393,578),(385,575),(390,560),(378,559),(372,565),(354,566),(358,575),(382,585),(417,595),(432,592),(475,606),(487,603),(498,596),(511,589),(528,593),(539,593),(549,605),(553,620),(551,631),(545,633),(551,638),(547,645),(534,646),(525,641),(509,640),(501,644),(478,649),(464,660),(450,669),(443,675),(449,688),(472,687),(496,693),(517,704),(529,724),(536,748),(542,803),(546,841),(553,887),(562,912),(556,933),(94,933),(84,864),(77,818),(77,706),(65,643),(50,589),(36,513),(31,468),(31,447),(39,434),(54,427)]
    if petr:
        # Reuse the white hard-hat/bearded head from the *current* Petr, not the earlier blue-cap design.
        src=Image.open(SRC/'tall/far.webp').convert('RGBA')
        head=src.crop((10,3,61,62)); hp=[(5,24),(8,13),(13,7),(22,3),(32,3),(39,6),(45,17),(47,23),(44,25),(43,33),(46,38),(42,42),(42,48),(37,52),(30,52),(26,57),(19,52),(16,45),(11,43),(11,35),(6,31)]
        head.putalpha(mask(head.size,hp,.6)); pic=pic.convert('RGBA'); pic.putalpha(mask(pic.size,p,1));
        m=Image.new('L',pic.size);ImageDraw.Draw(m).polygon([(179,200),(380,190),(378,384),(300,395),(206,350),(171,336)],fill=255); a=np.array(alpha(pic));a[np.array(m)>0]=0;pic.putalpha(Image.fromarray(a));
        hd=place(head,(168,186),(4.05,3.85),pic.size); pic.alpha_composite(hd)
    else: pic.putalpha(mask(pic.size,p,1))
    return pic.crop((28,185,565,933))

def repair_ladder(im,f):
    out=im.copy(); w,h=im.size
    if f=='wide':
        # The approved v5 desk plate is the same camera but has no ladder baked into its portal.
        plate=rgb(ART/'barge-v5/desk/plate.webp'); old=(726.7,664); ratio=.777
        clean=place(plate,(150-ratio*old[0]*2,494-ratio*old[1]*2),ratio,im.size)
        pts=[(124,264),(163,262),(166,460),(164,480),(161,497),(141,493),(138,454),(122,452)]
        mix(out,clean,pts,1)
        # Continue the three bolts to the uprights. Their slopes come from the visible bracket ends.
        for y,slope in [(291,-.48),(361,-.30),(425,-.055)]:
            mix(out,translated(im,-25,-25*slope),[(150,y-3),(169,y-3+19*slope),(169,y+3+19*slope),(150,y+3)],.5)
        # Sample the pad face below the obstruction, not the paving under the plate.
        pad=Image.new('RGB',im.size,im.getpixel((146,500)));mix(out,pad,[(121,483),(155,472),(174,487),(174,497),(145,508)],.5)
        lad=Image.open(ART/'barge-v5/desk/ladder.webp').convert('RGBA'); lad=place(lad,(121,172),(.76,.78),im.size)
        matte=mask(im.size,[(120,255),(139,266),(161,263),(165,258),(166,501),(118,501)],.5)
    else:
        # Rebuild only the pixels hidden by the old cage. Each backdrop plane is a straight
        # translation along its existing edges; the building, rails and cab are not warped.
        pts=[(138,341),(188,340),(199,354),(199,523),(188,528),(187,563),(148,560),(148,525),(135,522)]
        clean=translated(im,81,12); mix(clean,translated(im,-9,2),[(146,540),(190,543),(187,565),(146,563)],0)
        # Inclined portal leg and brace behind the cage; registration fixed from visible ends.
        leg=translated(im,-23,-69)
        mix(clean,leg,[(179,340),(203,342),(217,467),(191,421),(178,382),(162,343)],.6)
        rail=translated(im,79,10)
        mix(clean,rail,[(126,374),(190,382),(195,409),(126,400)],.5)
        mix(out,clean,pts,.8)
        # A straight footpad face, with its original paint sampled inside the pad.
        d=ImageDraw.Draw(out); d.polygon([(148,538),(198,544),(190,575),(141,569)],fill=im.getpixel((146,564)))
        lad=Image.open(ART/'barge-v5/tall/ladder.webp').convert('RGBA');lad=place(lad,(132,228),(1.10,1.035),im.size)
        matte=mask(im.size,[(132,339),(187,344),(200,342),(205,565),(132,565)],.45)
    a=np.minimum(np.asarray(alpha(lad)),np.asarray(matte)); lad.putalpha(Image.fromarray(a)); overlay(out,lad);return out

def occupy(im,f,person):
    tall=f=='tall'; out=im.copy()
    panes=([[(181,97),(207,129),(208,183),(181,152)],[(217,130),(286,112),(286,177),(217,194)]] if not tall else [[(108,149),(210,175),(210,227),(108,203)],[(227,179),(244,164),(243,195),(226,224)]])
    size=im.size
    # A lit interior, with the seat on the rear wall and the console against the water-side pane.
    h,w=im.height,im.width; xx,yy=np.meshgrid(np.arange(w),np.arange(h));light=np.clip((xx-123)*.0015+(195-yy)*.004,0,1)
    glass=Image.fromarray(np.uint8(np.array([44,58,73])+light[...,None]*np.array([39,54,65]))); g=ImageDraw.Draw(glass,'RGBA')
    if tall:
        g.polygon([(181,216),(211,211),(234,215),(208,225),(188,224)],fill=(106,126,137,255));g.polygon([(181,216),(208,222),(234,215),(232,222),(209,229),(181,223)],fill=(57,75,88,255));g.ellipse((205,214,207,216),fill=(241,175,73,255))
    else:
        g.polygon([(175,150),(206,179),(227,181),(212,194),(178,170)],fill=(47,56,70,230))
    op=actor(person=='petr')
    # Keep the painted chair back, two arms and bent thigh. The panel and sill hide the boots.
    if not tall: sprite=place(op,(204,126),(.148,.130),size)
    else: sprite=place(op,(124,166),(.151,.122),size)
    overlay(glass,sprite);g=ImageDraw.Draw(glass,'RGBA')
    # Back wall/window reflections, not an opaque decal. Existing posts and control console stay in front.
    if not tall:
        g.polygon([(180,104),(191,116),(188,170),(182,159)],fill=(183,225,242,40))
        g.polygon([(280,112),(286,110),(286,117),(252,179),(248,181)],fill=(195,231,244,27))
    else:g.polygon([(112,147),(125,151),(113,200),(108,202)],fill=(185,225,240,32))
    # Glazing tints the clothing and the chair as well as the cabin interior.
    glass=Image.blend(glass,Image.new('RGB',size,(116,158,180)),.135)
    if tall:
        g=ImageDraw.Draw(glass,'RGBA');g.polygon([(190,177),(196,178),(165,219),(159,218)],fill=(208,232,244,19));g.polygon([(224,208),(247,184),(247,202),(225,226)],fill=(139,184,206,55))
    for pts in panes:mix(out,glass,pts,.35)
    # Near front control panel occludes wrists and seat at window bottom.
    if not tall: mix(out,im,[(220,185),(271,173),(280,177),(279,186),(223,200)],.5)
    return out

def badge(im,f,id):
    # Small in-world reaction using the game's existing icon language, targeted at the cab, not the foot.
    k=3; W,H=78,79; a=Image.new('RGBA',(W*k,H*k));d=ImageDraw.Draw(a)
    def pts(v):return [(int(x*k),int(y*k)) for x,y in v]
    ink='#203d4c';d.polygon(pts([(30,48),(61,46),(53,75)]),fill=ink);d.rounded_rectangle((3*k,4*k,73*k,55*k),radius=12*k,fill='white',outline=ink,width=3*k);d.polygon(pts([(35,50),(56,48),(51,65)]),fill='white')
    if id=='rush':
        for x in (20,42):d.arc((x*k,23*k,(x+12)*k,31*k),5,170,fill=ink,width=2*k)
        d.arc((28*k,29*k,47*k,40*k),8,168,fill=ink,width=2*k);d.polygon(pts([(66,0),(70,10),(72,14),(70,18),(66,20),(61,18),(60,14),(62,8)]),fill='#58b8e6',outline=ink,width=2*k)
    else:
        for x,s in [(24,1),(45,-1)]:d.line(pts([(x-4,20+2*s),(x+4,20-2*s)]),fill=ink,width=2*k);d.ellipse(((x-2)*k,25*k,(x+2)*k,29*k),fill=ink)
        d.arc((29*k,36*k,47*k,46*k),194,346,fill=ink,width=2*k)
    a=a.resize((66,65),Image.Resampling.LANCZOS); x,y=((143,58) if f=='wide' else (85,88));im.paste(a,(x,y),a)

def far_empty(scene,f):
    b=FAR[f]; im=scene.crop(b)
    # A second portal of identical dimensions supplies a clean rail/leg and painted ground.
    dx,dy=(1286,-439) if f=='wide' else (300,-1238)
    clean=scene.crop(tuple(i+(dx if n%2==0 else dy) for n,i in enumerate(b)))
    if f=='wide':
        pts=[(132,85),(157,84),(167,103),(164,118),(171,142),(170,176),(161,185),(166,202),(172,220),(178,218),(227,207),(234,209),(218,224),(170,233),(127,237),(124,220),(129,195),(120,176),(114,154),(117,132),(125,120)]
    else:pts=[(130,73),(164,73),(177,94),(175,113),(179,138),(183,168),(181,192),(172,207),(175,221),(186,228),(183,247),(145,253),(132,243),(132,229),(129,218),(130,192),(124,181),(122,158),(126,135),(128,120)]
    if f=='wide':
        # Continue the painting's horizontal features through the old position. The diagonal
        # shadow on the paving is a second plane; paint it from its original lit/shaded ends.
        clean=translated(im,65,-22.3)
        pts0=[(127,83),(162,82),(175,109),(170,143),(167,171),(161,185),(157,197),(123,201),(115,182),(111,147),(114,123)]
        im=heal(im,clean,pts0)
        # Reinstate just the interrupted steel web from a straight contour. The lower
        # rail and cap are drawn separately, with their own original widths and slopes.
        mix(im,clean,[(122,87),(167,73),(169,84),(125,103)],.7)
        clean=im.copy()
        rail=bridge(im,120,170,-.321)
        mix(clean,rail,[(117,193),(170,177),(172,198),(117,216)],.7)
        edge=bridge(im,115,245,-.343)
        mix(clean,edge,[(115,217),(245,172),(248,228),(115,263)],.5)
        # The seated worker no longer casts a shadow along the cap.
        pts=[(130,86),(159,86),(167,100),(163,117),(169,142),(168,175),(162,180),(162,199),(175,207),(202,205),(238,205),(238,224),(177,234),(128,238),(122,226),(128,201),(127,186),(117,178),(116,155),(119,132),(125,117)]
    else:
        # Extend the painted kerb on its own plane; one affine from a clean strip below the boots.
        # Inverse: source y = .27*y + 245; centreline x changes -.229 pixels for every y pixel.
        sy=.27;ty=245;slope=-.229;T=np.float32([[1,slope*(sy-1),slope*ty],[0,sy,ty]])
        floor=aff(im,cv.invertAffineTransform(T),im.size)
        # This transom and yellow buffer are shared by both portal bases, independent of the load.
        mach=aff(clean,cv.invertAffineTransform(np.float32([[.98669,-.00688,-1.469],[-.01722,.98346,-2.763]])),im.size)
        mix(floor,mach,[(123,69),(158,69),(151,106),(137,160),(121,231),(107,249),(107,159)],1.2);clean=floor
    mix(im,clean,pts,1.0);return im

def office_img(scene,f,occupied):
    b=OFFICE[f]; im=scene.crop(b)
    if f=='wide':
        old=(315.9,465.5);r=.777
        # Crop from the v5 empty office, same camera and physical dimensions. Main registry: centre of roof.
        orig=rgb(ART/'barge-v5/desk/plate.webp'); clean=place(orig,(150-r*old[0]*2,94-r*old[1]*2),r,im.size)
        # Remove the outside shadow first. Copy from the same band of unoccupied quay,
        # then reinstate the round office wall and cut the whole v5 door on its actual silhouette.
        canvas=scene.crop((b[0]-250,b[1]-60,b[2]+250,b[3]+90))
        paved=canvas.crop((250-151,60+54,250-151+im.width,60+54+im.height))
        mix(im,paved,[(223,387),(292,386),(343,412),(363,424),(365,440),(327,451),(229,455),(211,443)],2)
        # Cylindrical band: its opposite side has exactly the missing curved profile.
        wall=aff(scene.crop(b),[[-1,0,299],[0,1,0]],im.size)
        mix(im,wall,[(236,284),(258,277),(278,287),(280,312),(288,335),(289,355),(283,379),(232,391),(226,348)],1)
        # Reuse the full painted door and its three individual stair risers; no rail pixels.
        cl=np.array(clean,dtype='float32');cl=np.clip(cl*np.array([1.035,1.035,1.06])+[2,2,4],0,255);clean=Image.fromarray(cl.astype('uint8'))
        pts=[(182,330),(251,307),(264,319),(264,367),(273,374),(274,381),(281,386),(281,394),(288,399),(288,405),(214,430),(207,425),(207,419),(200,416),(199,408),(192,405),(182,397)]
        # A narrow warm contact shadow under the new bottom riser, not the track in the v5 donor.
        sh=Image.new('RGB',im.size,(129,114,126));mix(im,sh,[(211,424),(287,401),(289,405),(214,433)],1.0)
        mix(im,clean,pts,.45)
        # Paint out the old portal's tiny exposed left lintel above the replacement.
        mix(im,clean,[(179,325),(231,307),(245,306),(251,310),(182,336)],.7)
        win=[(132,204),(184,202),(184,253),(131,255)];sp=place(actor(),(133,202),(.082,.085),im.size)
    else:
        # Restore the two crossing straight paving joints under Ivan with clones along each joint.
        p=[(238,279),(269,276),(283,298),(278,320),(291,348),(297,389),(287,414),(303,433),(294,449),(276,447),(272,459),(238,456),(229,428),(232,398),(221,381),(224,345),(232,322)]
        # Ground from the right of the porch; rail-side landing stays untouched.
        clean=translated(im,-93,-13)
        # Keep the long straight joint from the untouched paving above and below the worker.
        # Only the hairline itself is missing here; continue the line between its two exposed ends.
        xy=np.indices((im.height,im.width),dtype='float32'); dist=np.abs(xy[1]-(351.3-.225*xy[0]));stroke=np.maximum(0,1-dist/1.0)*.30
        clean=Image.fromarray(np.uint8(np.asarray(clean)*(1-stroke[...,None])+np.array([112,106,116])*stroke[...,None]))
        mix(im,clean,p,1.3)
        win=[(64,331),(121,309),(120,348),(105,358),(65,374)];sp=place(actor(),(66,321),(.084,.083),im.size)
    if occupied:
        occ=im.copy();overlay(occ,sp);mix(im,Image.blend(occ,Image.new('RGB',im.size,(129,177,208)),.19),win,.45)
    return im

def rail_affine(wide,mid):
    # Two cameras have the same orientation. Estimate only uniform scale + translation, not a flow field.
    s=.924; a=cv.resize(np.asarray(wide),(0,0),fx=s,fy=s,interpolation=cv.INTER_AREA); dst=np.asarray(mid); pairs=[]
    for x,y in [(2750,800),(1450,1100),(2250,540),(2500,460),(3200,650),(3130,800)]:
        ax,ay=round(x*s),round(y*s);tpl=a[ay:ay+88,ax:ax+88];_,score,_,pos=cv.minMaxLoc(cv.matchTemplate(dst,tpl,cv.TM_CCOEFF_NORMED));
        if score>.94:pairs.append(((x,y),pos))
    assert len(pairs)>=3,pairs
    ab=np.array([p[0] for p in pairs]);cd=np.array([p[1] for p in pairs]);s=((ab-ab.mean(0))*(cd-cd.mean(0))).sum()/((ab-ab.mean(0))**2).sum();dx,dy=(cd-s*ab).mean(0);print('rail affine',s,dx,dy);return s,dx,dy

def port(scene,patch,box,mat):
    s,dx,dy=mat;x=round(box[0]*s+dx);y=round(box[1]*s+dy);w,h=patch.size
    if s!=1:patch=patch.resize((round(w*s),round(h*s)),Image.Resampling.LANCZOS)
    # Feather patch perimeter into the native screenshot (especially the parallel rail-camera painting).
    border=mask(patch.size,quad(5,5,patch.width-6,patch.height-6),2);scene.paste(patch,(x,y),border)

def generate():
    bases={f:source(f,'remote') for f in FORMATS}; mats={'wide':(1,0,0),'tall':(1,0,0),'mid':rail_affine(bases['wide'],bases['mid'])}
    for fmt in FORMATS:
        f='wide' if fmt=='mid' else fmt;mat=mats[fmt];scene=bases[f];nb=BOX[f]; crane=repair_ladder(scene.crop(nb),f);empty=far_empty(scene,f)
        for id in ('rush','petr','remote'):
            original=source(fmt,id); result=original.copy()
            # Remote is a clean state source for the old walker/balloons. Preserve the gift and HUD elsewhere.
            near=crane.copy()
            if id!='remote':near=occupy(near,f,id);badge(near,f,id)
            port(result,near,nb,mat)
            if id=='petr':
                # Clear the old reaction above Petr with the same-frame, same-camera remote branch.
                bb=tuple(v+(-36 if i%2==0 else -150) if i<2 else v+36 for i,v in enumerate(FAR[f]));r=bases[f].crop(bb);r.paste(empty,(FAR[f][0]-bb[0],FAR[f][1]-bb[1]));port(result,r,bb,mat)
            if id in ('rush','remote'):port(result,office_img(scene,f,id=='remote'),OFFICE[f],mat)
            path=DEST/f'outcome-{id}{FORMATS[fmt]}.webp';assert result.size==original.size
            result.save(path,'WEBP',quality=94,method=6);print(path.name,result.size,flush=True)

if __name__=='__main__': generate()
