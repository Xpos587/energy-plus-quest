"""Lossless, local-only rollout candidates; public media and manifest are never written.
Inputs and review gates: design/scene-05/LIVERY-ROLLOUT.md.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, json, shutil, sys
from geometry import pts, S
from portholes import fix_flight_porthole

def aa_polygon(size, points):
 m=Image.new('L',(size[0]*8,size[1]*8));ImageDraw.Draw(m).polygon([(x*8,y*8) for x,y in points],fill=255)
 return np.asarray(m.resize(size,Image.Resampling.LANCZOS))/255

def grey_tips(a,boxes):
 for x,y,w,h in boxes:
  rgb=a[y:y+h,x:x+w];mask=(rgb[:,:,0]>130)&(rgb[:,:,1]<175)&(rgb[:,:,2]<120)&(rgb[:,:,0]-rgb[:,:,2]>55)
  grey=(rgb@[.299,.587,.114])*.6;rgb[mask]=np.stack([grey*.95,grey,grey*1.05],axis=-1)[mask]


def main(workspace, map_workspace, boat_sample):
    R = Path(workspace)
    B = R/'before'
    C = R/'candidates'
    R3 = Path(map_workspace)
    rows = json.loads((R/'inventory.json').read_text())
    # Darken only the two requested portholes, not the already approved wide curves.
    wide=Image.open(R3/'candidates/choice-wide.webp').convert('RGB')
    box=(803,1714,854,1752);glass=wide.crop(box).resize((408,304),Image.Resampling.NEAREST);d=ImageDraw.Draw(glass)
    for cx,cy,rx,ry in [(815.5,1735,9.6,13.7),(840,1731,10.6,14.6)]:
     def ellipse(inset):return tuple((v-box[j%2])*8 for j,v in enumerate((cx-rx+inset,cy-ry+inset,cx+rx-inset,cy+ry-inset)))
     d.ellipse(ellipse(0),fill=(25,34,45));d.ellipse(ellipse(.9),fill=(43,55,73))
     d.arc(ellipse(1.8),180,265,fill=(70,82,98),width=6)
    wide.paste(glass.resize((51,38),Image.Resampling.LANCZOS),box)
    wide.crop((590,1580,920,1810)).resize((990,690)).save(R/'sheets/wide-dark-glass-detail.png')

    checks=[]
    for row in rows:
     rel=row['path'].removeprefix('public/');src=B/rel;dst=C/rel;dst.parent.mkdir(parents=True,exist_ok=True)
     orig=Image.open(src).convert('RGB');a=np.array(orig).astype(float);name=src.name;allowed=np.zeros(a.shape[:2],bool);note='local curved livery'
     if 'helicopter-ground-' in name:
      shutil.copyfile(src,dst);note='no helicopter → unchanged'
     elif name.startswith('choice-'):
      fmt=name.split('-')[1];s=S[fmt];k=orig.width/s['width']
      old=np.array(Image.open(B/f'scene-art/lastmile-family-v1/revision-18/choice-{fmt}-alva.webp').convert('RGB'))
      donor=np.array(wide if fmt=='wide' else Image.open(R3/'candidates/choice-tall.webp').convert('RGB'))
      changed=np.any(donor!=old,axis=2)
      house=Image.new('L',orig.size);ImageDraw.Draw(house).polygon([(round(x*k),round(y*k)) for x,y in s['house']],fill=255);house=np.array(house)>0
      tent=Image.new('L',orig.size);ImageDraw.Draw(tent).polygon([(round(x*k),round(y*k)) for x,y in s['patches'][3]],fill=255);tent=np.array(tent.filter(ImageFilter.GaussianBlur(k)))>0
      # Transfer local additions/cleanup only, never Alva's whole composition or trim.
      changed[house&~tent]=False;a[changed]=donor[changed];allowed|=changed
      red,green,blue=a[:,:,0],a[:,:,1],a[:,:,2]
      trim=house&(red>180)&(green>100)&(green<235)&(blue<90)&(red-green>10)
      a[trim,1]=np.minimum(a[trim,1],120);a[trim,2]=np.minimum(a[trim,2],25);allowed|=trim
      note='approved local map patches; original recipient/foreground retained'
     elif name.startswith('flight-'):
      if 'boat' in name:
       donor=np.array(Image.open(boat_sample).convert('RGB'))
       a[738:848,1034:1120]=donor[738:848,1034:1120];allowed[738:848,1034:1120]=True
      else:
       # Old low white swash is separate from the new contour. Recolour only its skin pixels.
       x0,y0,x1,y1=977,798,1046,843;rgb=a[y0:y1,x0:x1];yy,xx=np.mgrid[y0:y1,x0:x1]
       removal=aa_polygon((x1-x0,y1-y0),[(x-x0,y-y0) for x,y in [(978,798),(1008,798),(1029,800),(1041,809),(1045,827),(1043,843),(978,843)]])
       # Match the intact adjacent skin row, stopping above the real fuselage silhouette.
       orange=np.median(a[y0:y1,1047:1053],axis=1)[:,None,:]
       rgb[:]=rgb*(1-removal[:,:,None])+orange*removal[:,:,None];allowed[y0:y1,x0:x1]=True
       x0,y0,x1,y1=1034,755,1120,847;rgb=a[y0:y1,x0:x1];yy,xx=np.mgrid[y0:y1,x0:x1]
       alpha=aa_polygon((x1-x0,y1-y0),[(1110-64*x-x0,758+84*y-y0) for x,y in pts])
       glass=((xx-1065)/11.2)**2+((yy-786)/11.2)**2<1
       alpha[glass|(rgb[:,:,0]<100)|(rgb[:,:,2]>rgb[:,:,0])]=0
       shade=246-(yy-760)*.20
       rgb[:]=rgb*(1-alpha[:,:,None])+np.stack([shade,shade,shade*.995],axis=-1)*alpha[:,:,None];allowed[y0:y1,x0:x1]=True
      boxes=[(609,578,36,14),(1232,596,34,18),(440,609,17,18),(334,634,16,18),(491,668,29,13),(1310,682,29,13),(360,724,17,16)]
      grey_tips(a,boxes)
      for x,y,w,h in boxes:allowed[y:y+h,x:x+w]=True
      note='local fuselage + seven rotor caps; door/cargo/sling/load outside masks'
     elif name=='intro-wide.webp':
      x0,y0,x1,y1=1618,204,1665,258;rgb=a[y0:y1,x0:x1];yy,xx=np.mgrid[y0:y1,x0:x1]
      # Two original dark panes remain intact; remove only the former straight white swash.
      glass=(((xx-1639)/5.8)**2+((yy-228)/7.1)**2<1)|(((xx-1654)/5.8)**2+((yy-225)/7.1)**2<1)
      body=yy<260-.34*(xx-1618)
      neutral=(rgb[:,:,2]>100)&(rgb[:,:,0]-rgb[:,:,2]<100)&~glass&(body|(rgb.min(axis=2)>205))
      orange=np.stack([239-(yy-211)*.22,92-(yy-211)*.30,29-(yy-211)*.20],axis=-1)
      weight=np.clip((rgb[:,:,2]-40)/100,0,1)*neutral
      rgb[:]=rgb*(1-weight[:,:,None])+orange*weight[:,:,None]
      alpha=aa_polygon((x1-x0,y1-y0),[(1623+39*x-2*y-x0,211+45*y-4*x-y0) for x,y in pts]);alpha[glass|~body]=0
      shade=246-(yy-211)*.18;rgb[:]=rgb*(1-alpha[:,:,None])+shade[:,:,None]*alpha[:,:,None];allowed[y0:y1,x0:x1]=True
      boxes=[(1479,155,13,10),(1558,83,14,11),(1776,77,17,12),(1840,181,18,12),(1842,59,12,14),(1871,106,17,14)]
      grey_tips(a,boxes)
      for x,y,w,h in boxes:allowed[y:y+h,x:x+w]=True
     elif 'route-v1' in rel:
      x0,y0,x1,y1=112,29,133,51;rgb=a[y0:y1,x0:x1]
      alpha=aa_polygon((x1-x0,y1-y0),[(118+11*x-3*y-x0,35+12*y-5*x-y0) for x,y in pts])
      alpha[(rgb[:,:,0]<rgb[:,:,2]+12)|(rgb[:,:,0]<100)]=0
      rgb[:]=rgb*(1-alpha[:,:,None])+np.array([242,242,239])*alpha[:,:,None];allowed[y0:y1,x0:x1]=True
     elif 'stage-icons-v1' in rel:
      shutil.copyfile(src,dst);note='progress icon → unchanged by Michael'
     else:raise AssertionError(rel)
     if 'helicopter-ground-' not in name and 'stage-icons-v1' not in rel:
      out=Image.fromarray(np.clip(a,0,255).astype('uint8'))
      if name.startswith('flight-'):out=fix_flight_porthole(out, parcel='parcel' in name)
      out.save(dst,lossless=True,method=4)
      assert np.array_equal(np.array(Image.open(dst)),np.array(out)),'lossless decode'
     after=np.array(Image.open(dst).convert('RGB'));before=np.array(orig);diff=np.any(after!=before,axis=2)
     assert not diff[~allowed].any(),(name,'outside authorized local masks')
     assert after.shape==before.shape
     checks.append({'path':row['path'],'note':note,'dimensions':orig.size,'changed_pixels':int(diff.sum()),'unchanged_percent':round(float((~diff).mean()*100),4),'outside_masks_identical':True})
     print(checks[-1],flush=True)
    (R/'locality-check.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('usage: rollout.py ROLLOUT_WORKSPACE R3_WORKSPACE APPROVED_BOAT_SAMPLE')
    main(*sys.argv[1:])
