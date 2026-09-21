"""Register the wholly redrawn city, never restore old architectural pixels."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
P = Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-13')
OUT = Path('/home/michael/Github/energy-plus-quest/public/review/map-geometry/pass-13')
S = 2
# Pairs are (repaired composition, generated composition), in 1440x1000 coordinates.
# Include both ends of the open gate and every main building corner, not roof-only masks.
anchors = [
((0,0),(0,0)),((1440,0),(1440,0)),((1440,1000),(1440,1000)),((0,1000),(0,1000)),
((150,27),(145,18)),((138,88),(132,83)),((118,245),(116,251)),
((102,445),(97,438)),((92,584),(91,595)),((88,780),(83,793)),
((373,93),(369,86)),((635,105),(628,104)),((351,281),(344,280)),((613,297),(609,298)),
((350,376),(344,385)),((618,396),(609,404)),
((382,386),(373,393)),((588,399),(577,406)),((376,438),(362,454)),((583,453),(570,474)),
((326,357),(315,358)),((644,386),(640,391)),((632,571),(625,590)),
((286,745),(275,758)),((286,778),(282,802)),((601,807),(574,830)),((616,773),(592,797)),((617,674),(595,687)),
((814,81),(785,75)),((916,89),(894,84)),((792,265),(759,265)),((900,274),(871,274)),
((788,415),(755,425)),((894,418),(870,431)),
((919,117),(894,109)),((1006,122),(983,115)),((911,211),(889,207)),((997,217),(974,215)),
((1011,112),(983,105)),((1110,121),(1083,114)),((993,317),(960,313)),((1085,332),(1061,330)),((984,421),(951,432)),((1091,431),(1056,441)),
((795,418),(762,426)),((1091,437),(1060,444)),((788,492),(758,507)),((1081,511),(1052,523)),((786,531),(756,547)),((1076,548),(1047,565)),
((782,656),(752,674)),((1048,674),(1025,693)),((774,741),(744,766)),((1040,756),(1017,784)),((776,805),(744,835)),((1040,822),(1008,852)),
((293,52),(287,54)),((455,30),(433,29)),((461,92),(439,95)),((278,80),(275,80)),((245,138),(244,140)),((271,166),(269,167)),
((356,454),(347,464)),((514,477),(499,486)),((506,543),(493,561)),((345,499),(339,510)),((326,578),(319,592)),((363,588),(355,603)),
((1169,267),(1139,280)),((1205,273),(1174,286)),((1175,417),(1145,423)),((1140,407),(1114,416)),((1130,481),(1104,493)),((1169,490),(1140,505)),
((658,608),(635,620)),((807,551),(778,566)),((824,622),(795,638)),((648,650),(625,667)),((632,716),(610,738)),((669,728),(649,750)),
((1280,163),(1257,165)),((1418,175),(1418,175)),((1252,505),(1214,530)),
((1275,520),(1238,529)),((1241,670),(1209,694)),((1250,853),(1215,896)),
((1090,752),(1059,778)),((1200,756),(1169,786)),
((305,891),(295,905)),((451,902),(434,916)),((464,902),(447,916)),((576,911),(559,925)),
((739,918),(711,938)),((857,926),(827,946)),((870,930),(840,953)),((983,938),(951,961)),
]
anchors += [((x,y),(x,y)) for x,y in [(x,y) for x in range(80,1440,80) for y in (0,1000)]+[(x,y) for y in range(80,1000,80) for x in (0,1440)]]
target=np.array([a for a,b in anchors],float)/1000
source=np.array([b for a,b in anchors],float)/1000
# Thin-plate displacement gives a continuous image, including roads and fence joins.
def kernel(a,b):
    d=((a[:,None]-b[None,:])**2).sum(axis=2)
    return d*np.log(np.maximum(d,1e-20))
k=kernel(target,target); linear=np.c_[np.ones(len(target)),target]
system=np.block([[k,linear],[linear.T,np.zeros((3,3))]])
weights=np.linalg.solve(system,np.r_[source-target,np.zeros((3,2))])
def base_mapping(points):
    points=np.asarray(points,float)/1000
    return (points+np.c_[kernel(points,target),np.ones(len(points)),points]@weights)*1000
assert np.max(np.abs(base_mapping(target*1000)-source*1000))<1e-6
# Keep architecture projective, with the continuous displacement reserved for open space.
# Blending the coordinate field outside silhouettes avoids doubled/pasted building edges.
rigid_regions = [
([(373,93),(635,105),(618,396),(350,376)],[(369,86),(628,104),(609,404),(344,385)]),
([(814,81),(916,89),(894,418),(788,415)],[(785,75),(894,84),(870,431),(755,425)]),
([(1011,112),(1110,121),(1091,431),(984,421)],[(983,105),(1083,114),(1056,441),(951,432)]),
([(795,418),(1091,437),(1076,548),(786,531)],[(762,426),(1060,444),(1047,565),(756,547)]),
([(782,656),(1048,674),(1040,822),(776,805)],[(752,674),(1025,693),(1008,852),(744,835)]),
]
# Peripheral buildings and complete trucks also keep straight authored edges.
rigid_regions += [
([(-40,72),(138,88),(108,429),(-40,420)],[(-40,72),(132,83),(106,434),(-40,425)]),
([(-40,432),(102,445),(88,780),(-40,771)],[(-40,426),(97,438),(83,793),(-40,780)]),
([(1280,163),(1490,178),(1460,515),(1252,505)],[(1257,165),(1467,180),(1422,540),(1214,530)]),
([(1275,520),(1480,535),(1470,870),(1241,853)],[(1238,529),(1450,544),(1430,913),(1215,896)]),
([(919,117),(1006,122),(988,404),(900,399)],[(894,109),(983,115),(965,417),(878,411)]),
([(270,30),(466,28),(465,169),(240,174)],[(267,29),(440,27),(444,170),(238,173)]),
([(309,450),(523,454),(522,593),(311,595)],[(303,460),(507,465),(505,610),(307,608)]),
([(629,538),(834,550),(835,734),(624,733)],[(606,554),(805,566),(806,757),(603,754)]),
([(1125,262),(1211,268),(1184,499),(1117,493)],[(1098,275),(1180,283),(1156,514),(1094,508)]),
([(305,891),(451,902),(440,1050),(283,1040)],[(295,905),(434,916),(423,1064),(273,1054)]),
([(464,902),(576,911),(568,1050),(446,1040)],[(447,916),(559,925),(551,1064),(429,1054)]),
([(739,918),(857,926),(846,1050),(722,1044)],[(711,938),(827,946),(816,1070),(694,1064)]),
([(870,930),(983,938),(975,1050),(854,1040)],[(840,953),(951,961),(943,1073),(824,1063)]),
([(1230,906),(1400,923),(1390,1060),(1200,1040)],[(1201,935),(1382,955),(1372,1092),(1171,1069)]),
([(385,-60),(691,-45),(681,38),(397,26)],[(370,-58),(670,-44),(650,41),(383,28)]),
([(835,-65),(1113,-51),(1106,50),(831,37)],[(790,-62),(1080,-51),(1066,52),(790,38)]),
]
def projective(target,source):
    a=[];b=[]
    for (x,y),(u,v) in zip(target,source):
        a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
    return np.r_[np.linalg.solve(a,b),1].reshape(3,3)
def mapping(points):
    points=np.asarray(points,float)
    result=base_mapping(points)
    for index in [*range(5,len(rigid_regions)),*range(5)]:
        target,source=rigid_regions[index]
        poly=np.array([(373,93),(635,105),(615,458),(344,449)] if index==0 else target,float);distances=[]
        for start,end in zip(poly,np.roll(poly,-1,axis=0)):
            edge=end-start;rel=points-start
            distances.append((edge[0]*rel[:,1]-edge[1]*rel[:,0])/np.linalg.norm(edge))
        blend=80 if index>=5 else 20
        weight=np.clip((np.min(distances,axis=0)+blend)/blend,0,1)[:,None]
        warped=np.c_[points,np.ones(len(points))]@projective(target,source).T
        result=result*(1-weight)+warped[:,:2]/warped[:,2:]*weight
    for start,end in [((326,357),(286,745)),((286,745),(286,778)),((286,778),(601,807)),((601,807),(616,773)),((616,773),(617,674)),((644,386),(632,571))]:
        start=np.array(start);end=np.array(end);edge=end-start
        t=np.clip(((points-start)*edge).sum(axis=1)/(edge@edge),0,1)
        distance=np.linalg.norm(points-start-t[:,None]*edge,axis=1)
        weight=np.clip((65-distance)/60,0,1)[:,None]
        result=result*(1-weight)+base_mapping(points)*weight
    return result
im=Image.open(P/'map-raw.png').convert('RGB').resize((1440*S,1000*S),Image.Resampling.LANCZOS)
# Admit only the new, style-matched front-glass repair, not the old pass12 crew pixels.
crew=Image.open(P/'crew-raw.png').convert('RGB').resize((680,880),Image.Resampling.LANCZOS)
src=[(134,352),(431,387),(418,560),(114,521)]
dst=[((1090+x/8)*S,(410+y/8)*S) for x,y in [(149,377),(427,404),(413,568),(128,539)]]
a=[];b=[]
for (x,y),(u,v) in zip(dst,src):
    a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
coeff=np.linalg.solve(a,b)
patch=crew.transform(im.size,Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(dst,fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(.6));im.paste(patch,(0,0),mask)
# Extend a narrow generated-texture bleed beyond the frame, never old-city pixels.
pad=120
bleed=Image.new('RGB',(im.width+2*pad,im.height+2*pad),(157,185,205))
bleed.paste(im,(pad,pad))
bleed.paste(ImageOps.flip(im.crop((0,0,im.width,pad))),(pad,0))
# Only repeat the last 16 display rows: a taller repeat duplicates roof parapets.
strip=32
for offset in range(0,pad,strip):
    bleed.paste(im.crop((0,im.height-strip,im.width,im.height)),(pad-round(.1*(offset+strip)),pad+im.height+offset))
bleed.paste(ImageOps.mirror(bleed.crop((pad,0,2*pad,bleed.height))),(0,0))
bleed.paste(ImageOps.mirror(bleed.crop((im.width,0,im.width+pad,bleed.height))),(im.width+pad,0))
# PIL's native mesh samples the smooth inverse map. No environment pixel comes from pass12.
xs=np.arange(0,1441,8);ys=np.arange(0,1001,8)
grid=np.array([(x,y) for y in ys for x in xs]);mapped=mapping(grid).reshape(len(ys),len(xs),2)
mesh=[]
for j in range(len(ys)-1):
    for i in range(len(xs)-1):
        corners=mapped[[j,j+1,j+1,j],[i,i,i+1,i+1]]
        mesh.append(((int(xs[i]*S),int(ys[j]*S),int(xs[i+1]*S),int(ys[j+1]*S)),tuple((corners*S+pad).ravel())))
# No folds or mirrored image patches are allowed.
dx=np.diff(mapped,axis=1)[:-1];dy=np.diff(mapped,axis=0)[:,:-1]
jacobian=(dx[:,:,0]*dy[:,:,1]-dx[:,:,1]*dy[:,:,0])/64
assert jacobian.min()>.25, (jacobian.min(),np.unravel_index(jacobian.argmin(),jacobian.shape))
im=bleed.transform(im.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)
im.save(P/'map.png');im.save(OUT/'map.jpg',quality=96,subsampling=0)
im.resize((1440,1000),Image.Resampling.LANCZOS).save(P/'map-screen.png')
(P/'registration.json').write_text(json.dumps({'method':'continuous thin-plate displacement of entire generated painting; native PIL mesh sampling','oldEnvironmentPixelsInserted':0,'anchorPairs':anchors,'maximumBackgroundAnchorResidualPixels':float(np.max(np.abs(base_mapping(target*1000)-source*1000))),'rigidRegions':rigid_regions,'minimumJacobian':float(jacobian.min()),'crewPatch':'new generated front glass only; projectively fitted before registration'},indent=2))
# The reference remains the original pixels plus its pre-existing alpha mask.
cut=Image.open(OUT.parent/'pass-12/professional-cutout.png').convert('RGBA')
original=Image.open('design/scene-01/assets/current/choices/professional.webp').convert('RGB')
assert np.array_equal(np.asarray(cut)[:,:,:3],np.asarray(original))
girl=cut.crop((450,55,1110,1855))
fontpath='/usr/share/fonts/TTF/DejaVuSans.ttf'
if not Path(fontpath).exists(): fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(fontpath,30);small=ImageFont.truetype(fontpath,22)
# Side-by-side with an outside-frame girl: no critical map detail is hidden.
for name,art in [('before',Image.open(OUT.parent/'pass-12/map-a.jpg')),('after',im)]:
    board=Image.new('RGB',(1810,1080),'#f5f0e6');board.paste(art.resize((1440,1000)),(0,60))
    figure=girl.resize((350,954),Image.Resampling.LANCZOS);board.paste(figure,(1450,80),figure)
    ImageDraw.Draw(board).text((20,15),'12 / BEFORE' if name=='before' else '13 / INK + OPAQUE PAINT',font=font,fill='#233a50')
    board.save(OUT/f'comparison-{name}.jpg',quality=95)
before=Image.open(OUT/'comparison-before.jpg');after=Image.open(OUT/'comparison-after.jpg')
contact=Image.new('RGB',(1810,2160),'#f5f0e6');contact.paste(before,(0,0));contact.paste(after,(0,1080));contact.save(OUT/'comparison.jpg',quality=95)
regions={'Roof / 6 skylights + 2 HVAC':(346,86,646,301),'Tower / 6 floors':(774,260,920,428),'Retail / separate entry':(773,480,1099,560),'Business / separate floors':(760,728,1070,833),'Fence + open gate':(270,345,675,835),'East road / one crossing':(1070,711,1241,819),'Crew / two people under glass':(1120,422,1202,502),'Dock / 6 doors + 7 lines':(352,330,612,460)}
board=Image.new('RGB',(1600,1680),'#f5f0e6');draw=ImageDraw.Draw(board)
for i,(label,box) in enumerate(regions.items()):
    crop=im.crop(tuple(v*S for v in box));crop.save(OUT/f'detail-{i+1}.png')
    crop.thumbnail((760,350),Image.Resampling.LANCZOS)
    x=(i%2)*800+(800-crop.width)//2;y=(i//2)*420+50
    board.paste(crop,(x,y));draw.text(((i%2)*800+20,(i//2)*420+12),label,font=small,fill='#233a50')
board.save(OUT/'details.jpg',quality=95)
# Normal-size and thumbnail diagnostics are generated from the actual final art.
thumb=im.resize((720,500),Image.Resampling.LANCZOS);thumb.save(P/'thumbnail.png')
print('Whole-city registration, crew repair and comparison exports complete')
