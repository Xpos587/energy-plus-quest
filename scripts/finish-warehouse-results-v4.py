# /// script
# dependencies = ["pillow", "numpy", "opencv-python-headless"]
# ///
"""R25: straight original warehouse masters, current people, correctly seated gifts.
Run from repository root: uv run scripts/finish-warehouse-results-v4.py
No dense optical flow, image generation, or changes to the accepted choice art.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT=Path('public/scene-art')
SOURCE=Path('design/scene-03/results-v4')
OUT=ROOT/'warehouse-results-v4'
REVIEW=Path('.tmp-work/r25-warehouse-lines')
spec=importlib.util.spec_from_file_location('gifts','scripts/finish-warehouse-gifts.py')
gifts=importlib.util.module_from_spec(spec);spec.loader.exec_module(gifts)
# Tight, reviewed silhouette envelopes retain the accepted v3 uniforms, faces and tools.
PEOPLE={
 'alphabet-camera':[(736,242),(760,237),(784,239),(802,244),(814,243),(832,252),(851,267),(869,275),(885,297),(897,310),(898,322),(889,333),(869,345),(849,355),(820,367),(817,400),(838,413),(849,422),(850,434),(835,443),(818,444),(799,438),(798,482),(796,501),(795,539),(783,546),(783,600),(781,657),(788,669),(811,674),(819,684),(821,702),(799,707),(767,706),(746,703),(726,701),(724,687),(726,664),(729,620),(730,577),(731,549),(720,578),(709,598),(703,629),(694,655),(684,671),(685,680),(697,691),(700,715),(678,720),(652,716),(629,704),(619,690),(620,673),(626,665),(625,656),(635,622),(645,593),(653,570),(661,551),(663,537),(665,509),(661,499),(668,484),(662,480),(660,467),(665,431),(668,398),(670,378),(668,359),(676,337),(688,323),(697,315),(704,302),(714,289),(731,286),(731,276)],
 'entrance':[(688,240),(731,234),(764,245),(799,249),(826,278),(852,307),(855,324),(840,342),(804,363),(783,374),(781,398),(805,411),(811,431),(796,444),(775,442),(774,491),(772,524),(763,552),(757,605),(754,650),(757,665),(780,674),(801,683),(800,705),(764,707),(727,696),(701,695),(700,672),(709,620),(711,560),(703,575),(692,610),(682,639),(672,663),(673,678),(686,698),(681,710),(653,716),(616,706),(587,692),(586,671),(595,652),(594,640),(605,610),(617,578),(620,551),(628,532),(630,506),(634,489),(629,481),(631,456),(635,412),(639,381),(638,362),(648,340),(664,324),(669,311),(682,296),(693,290),(689,274)],
 'keeper':[(447,191),(475,188),(490,179),(508,170),(533,170),(560,177),(578,188),(589,188),(606,196),(617,214),(621,232),(639,233),(661,253),(685,277),(701,300),(706,317),(699,334),(679,352),(651,371),(617,387),(611,415),(605,436),(610,471),(609,531),(609,557),(606,573),(609,611),(612,641),(607,662),(618,698),(624,743),(632,785),(630,813),(633,832),(645,843),(648,879),(624,885),(593,881),(569,869),(552,866),(551,848),(548,830),(540,802),(543,784),(534,754),(529,714),(517,673),(506,630),(494,592),(486,578),(477,624),(468,660),(465,684),(469,701),(462,742),(456,776),(451,789),(455,808),(449,828),(451,854),(428,860),(412,856),(392,867),(365,870),(339,867),(321,860),(321,843),(329,829),(347,820),(365,808),(366,778),(371,757),(368,721),(372,684),(377,652),(377,631),(374,615),(380,579),(376,566),(382,541),(373,536),(377,502),(383,469),(387,440),(390,420),(391,399),(374,416),(359,431),(342,439),(322,438),(295,432),(264,422),(244,415),(233,400),(227,390),(214,386),(208,374),(213,366),(221,369),(218,359),(212,354),(207,351),(207,342),(218,334),(232,330),(247,334),(261,343),(270,356),(282,355),(305,362),(328,365),(351,351),(364,345),(383,316),(400,290),(423,276),(451,270),(464,251),(472,245),(477,223),(479,211),(461,209),(448,203)],
 'wms':[(518,190),(524,172),(537,156),(557,147),(580,147),(604,154),(624,164),(633,178),(634,196),(646,207),(651,220),(641,226),(621,215),(610,235),(597,254),(589,270),(601,286),(615,301),(623,320),(629,345),(639,366),(653,383),(664,402),(674,420),(690,443),(703,464),(708,489),(728,498),(746,509),(746,517),(732,520),(717,514),(707,522),(693,520),(678,512),(668,499),(648,492),(635,481),(625,474),(613,469),(601,467),(596,478),(598,519),(596,542),(592,551),(600,566),(594,577),(595,607),(589,621),(586,651),(587,665),(582,684),(580,714),(580,741),(579,755),(588,772),(582,800),(606,808),(626,817),(635,827),(633,844),(615,849),(591,843),(570,836),(548,835),(528,831),(525,817),(529,800),(526,773),(523,754),(523,717),(526,678),(530,648),(535,616),(537,598),(526,623),(516,655),(510,682),(500,709),(492,738),(485,759),(475,778),(472,803),(468,815),(471,829),(477,844),(476,862),(456,867),(434,865),(416,857),(408,844),(409,819),(408,805),(412,779),(414,744),(417,716),(421,685),(431,652),(437,623),(436,610),(441,575),(439,560),(443,540),(438,532),(438,503),(441,472),(443,447),(445,431),(440,413),(438,391),(432,368),(433,341),(439,316),(445,294),(456,277),(449,270),(452,258),(463,242),(480,229),(503,224),(513,225),(519,206)],
}
HOLES={'alphabet-camera':[[(806,286),(824,294),(831,309),(806,316)]], 'entrance':[[(771,284),(784,291),(787,311),(773,315)]]}
QUADS={
 'alphabet-camera':{'top':[(884,513),(1008,500),(1158,509),(1034,517)],'front':[(884,513),(1034,517),(1035,629),(884,623)],'side':[(1034,517),(1158,509),(1162,613),(1035,629)]},
 'entrance':{'top':[(837,506),(947,498),(1087,504),(978,518)],'front':[(837,506),(978,518),(978,636),(837,627)],'side':[(978,518),(1087,504),(1087,624),(978,636)]},
 'wms':{'top':[(679,516),(749,504),(935,513),(877,530)],'front':[(679,516),(877,530),(877,733),(679,717)],'side':[(877,530),(935,513),(935,715),(877,733)]},
 'keeper':{'top':[(1091,606),(1125,589),(1270,583),(1235,600)],'front':[(1091,606),(1235,600),(1235,745),(1091,751)],'side':[(1235,600),(1270,583),(1270,728),(1235,745)]},
}
# Trace the actual neighbour edge; a higher mask exposes the gift's own kraft
# side beneath its red top and falsely creates an overhang.
NEIGHBOUR=[(913,556),(1008,538),(1215,545),(1215,740),(913,740)]

def person_mask(size,branch):
 m=Image.new('L',size);d=ImageDraw.Draw(m);d.polygon(PEOPLE[branch],fill=255)
 for hole in HOLES.get(branch,[]):d.polygon(hole,fill=0)
 if branch=='keeper':
  d.polygon([(540,800),(625,805),(641,837),(650,881),(614,890),(577,881),(540,867),(531,841)],fill=255)
  d.polygon([(364,806),(449,810),(454,856),(415,865),(376,877),(323,866),(316,844),(331,823)],fill=255)
 if branch=='wms':
  d.polygon([(412,800),(467,800),(479,848),(478,869),(435,872),(405,859),(402,837)],fill=255)
  d.polygon([(529,788),(581,790),(613,807),(639,820),(639,847),(612,854),(571,844),(519,833),(516,814)],fill=255)
 m=m.filter(ImageFilter.MaxFilter(7))
 # The envelope stays opaque; only its exterior gets a short seam blend.
 return Image.fromarray(np.maximum(np.asarray(m),np.asarray(m.filter(ImageFilter.GaussianBlur(1.2)))))

def straighten(branch,ref,H):
 raw=cv2.imread(str(SOURCE/f'hf-{branch}.png'))
 raw=cv2.resize(raw,ref.size,interpolation=cv2.INTER_LANCZOS4)
 flat=cv2.warpPerspective(raw,np.array(H),ref.size,flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REPLICATE)
 return Image.fromarray(cv2.cvtColor(flat,cv2.COLOR_BGR2RGB))

def keeper_gift(image,wms):
 out=image.convert('RGBA');shadow=Image.new('RGBA',image.size)
 ImageDraw.Draw(shadow).polygon([(1089,752),(1237,747),(1273,730),(1125,733)],fill=(10,35,58,135))
 out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2)))
 # Reproject the existing front texture, label and ribbon onto this cart's plane.
 front=QUADS['wms']['front'];rect=np.float32([(0,0),(299,0),(299,299),(0,299)])
 H=cv2.getPerspectiveTransform(np.float32(front),rect)
 patch=Image.fromarray(cv2.warpPerspective(np.asarray(wms),H,(300,300))).convert('RGBA')
 gifts.warp_patch(out,patch,QUADS['keeper']['front'])
 side=ImageEnhance.Brightness(patch).enhance(.84)
 # No duplicated barcode on the side: reuse a clean red strip, then add its ribbon.
 side=side.crop((215,0,285,300)).resize((300,300))
 gifts.warp_patch(out,side,QUADS['keeper']['side'])
 gifts.warp_patch(out,gifts.ribbon('side'),QUADS['keeper']['side'])
 top=Image.new('RGBA',(300,300),'#d63630');gifts.warp_patch(out,top,QUADS['keeper']['top'])
 gifts.warp_patch(out,gifts.ribbon('top'),QUADS['keeper']['top'])
 bow,pos=gifts.bow(QUADS['keeper']);out.alpha_composite(bow,pos)
 return out.convert('RGB')

def comparison(before,after,box,path):
 images=[before.crop(box),after.crop(box)]
 w,h=images[0].size;sheet=Image.new('RGB',(w*2,h+28),'#edf1f5')
 for i,(im,label) in enumerate(zip(images,['BEFORE / v3','AFTER / v4'])):
  sheet.paste(im,(i*w,28));ImageDraw.Draw(sheet).text((i*w+8,8),label,fill='#173849')
 sheet.save(path,quality=97)

def variant_audit():
 camera=np.asarray(Image.open(ROOT/'warehouse-results-v3/outcome-alphabet-camera.webp').convert('RGB')).astype(int)
 audit=[]
 for name in ['boat','socks']:
  other=np.asarray(Image.open(ROOT/f'warehouse-results-v3/outcome-alphabet-{name}.webp').convert('RGB')).astype(int)
  delta=np.max(np.abs(other-camera),axis=2);delta[205:285,1025:1138]=0
  _,_,stats,_=cv2.connectedComponentsWithStats((delta>30).astype('uint8'))
  largest=int(stats[1:,cv2.CC_STAT_AREA].max()) if len(stats)>1 else 0
  # Outside the authored plaque only isolated WebP encoding differences remain.
  assert largest<=3 and np.count_nonzero(delta>30)<=20,name
  audit.append({'variant':name,'plaqueBounds':[1025,205,1138,285],'outsidePlaqueMeanMaxChannelDelta':float(delta.mean()),'outsidePlaquePixelsAbove30':int(np.count_nonzero(delta>30)),'largestOutsidePlaqueComponentAbove30':largest})
 return audit

def main():
 OUT.mkdir(exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
 audit=variant_audit()
 registration=json.loads((SOURCE/'registration.json').read_text());bases={};metrics=[]
 for item in registration:
  branch=item['branch'];ref=Image.open(ROOT/f'warehouse-results-v3/outcome-{branch}.webp').convert('RGB')
  base=straighten(branch,ref,item['homography']);bases[branch]=base
  base.save(REVIEW/f'{branch}-straight.png')
 wms=gifts.wrap(bases['wms'],QUADS['wms'])
 neighbour=gifts.face_mask(wms.size,[NEIGHBOUR]);wms.paste(bases['wms'],(0,0),neighbour)
 assert np.array_equal(np.asarray(wms)[np.asarray(neighbour)>0],np.asarray(bases['wms'])[np.asarray(neighbour)>0])
 for point in [(920,550),(925,550),(930,550)]:
  r,g,b=wms.getpixel(point)
  assert r>2*max(g,b),'Visible gift side must stay red up to the neighbour edge'
 for name in ['alphabet-boat','alphabet-camera','alphabet-socks','entrance','keeper','wms']:
  branch='alphabet-camera' if name.startswith('alphabet-') else name
  ref=Image.open(ROOT/f'warehouse-results-v3/outcome-{name}.webp').convert('RGB');base=bases[branch]
  result=wms.copy() if branch=='wms' else keeper_gift(base,wms) if branch=='keeper' else gifts.wrap(base,QUADS[branch])
  if name.startswith('alphabet-'):
   # v3 variants have one authored difference: this printed plaque (see receipt).
   plaque=(1042,224,1120,269);result.paste(ref.crop(plaque),plaque[:2])
  mask=person_mask(ref.size,branch);result.paste(ref,(0,0),mask)
  target=OUT/f'outcome-{name}.webp';result.save(target,lossless=True,method=6)
  decoded=Image.open(target).convert('RGB');protected=np.asarray(mask)==255
  assert np.array_equal(np.asarray(ref)[protected],np.asarray(decoded)[protected]),name
  mask.save(REVIEW/f'{name}-person-mask.png')
  overlay=Image.composite(ref,ImageEnhance.Color(ref).enhance(0),mask)
  ImageDraw.Draw(overlay).line(PEOPLE[branch]+[PEOPLE[branch][0]],fill='#ff00ff',width=2)
  overlay.save(REVIEW/f'{name}-person-envelope.jpg',quality=95)
  points=np.array(PEOPLE[branch]);bounds=(int(points[:,0].min())-8,int(points[:,1].min())-8,int(points[:,0].max())+8,int(points[:,1].max())+8)
  comparison(ref,decoded,bounds,REVIEW/f'uniform-{name}.jpg')
  geometry={'alphabet-camera':(570,200,1400,750),'entrance':(520,160,1300,740),'keeper':(150,80,1450,920),'wms':(350,100,1330,900)}[branch]
  comparison(ref,decoded,geometry,REVIEW/f'geometry-{name}.jpg')
  if name=='keeper':comparison(ref,decoded,(1030,540,1320,805),REVIEW/'keeper-contact.jpg')
  if name=='wms':comparison(ref,decoded,(840,505,1010,749),REVIEW/'wms-neighbour.jpg')
  metrics.append({'result':name,'source':str(SOURCE/f'hf-{branch}.png'),'sourceSha256':hashlib.sha256((SOURCE/f'hf-{branch}.png').read_bytes()).hexdigest(),'acceptedPeopleSource':f'public/scene-art/warehouse-results-v3/outcome-{name}.webp','acceptedPeopleSourceSha256':hashlib.sha256((ROOT/f'warehouse-results-v3/outcome-{name}.webp').read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'size':list(result.size),'protectedPersonPixels':int(protected.sum()),'protectedPersonChangedPixels':0,'lossless':True})
 deck=np.float32([(974,737),(1357,716),(1442,739),(1049,770)])
 for point in [(1091,751),(1235,745),(1270,728),(1125,734)]:
  assert cv2.pointPolygonTest(deck,point,True)>1,'Gift must contact the interior of the cart deck'
 (SOURCE/'receipt.json').write_text(json.dumps({'registration':'homography only; no dense optical flow','alphabetVariantAudit':audit,'keeperFootprintInsideDeck':True,'wmsNeighbourChangedPixels':0,'results':metrics},indent=2)+'\n')
 print('Six lossless outcomes; accepted-person pixel equality and WMS neighbour invariance passed.')

if __name__=='__main__':main()
