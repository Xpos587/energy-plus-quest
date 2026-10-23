from PIL import Image,ImageDraw
from pathlib import Path
import json,random
O=Path(__file__).parent
for d in ('guideframes','alphaframes','details'): (O/d).mkdir(exist_ok=True)
files=sorted((O/'vehicleframes').glob('[0-9][0-9][0-9][0-9].png'))
W,H=Image.open(files[0]).size
rng=random.Random(20261005)
bg=Image.new('RGB',(W,H));bg.putdata([(v,v+1,v+2) for v in [rng.choice((115,116,117,118)) for _ in range(W*H)]])
bg.save(O/'road-background.png')
contact=Image.new('RGB',(960,((H*320)//W)*3),(235,235,235))
for i,p in enumerate(files):
 im=Image.open(p).convert('RGBA');out=bg.copy();out.paste(im,mask=im.getchannel('A'));out.save(O/'guideframes'/p.name)
 im.getchannel('A').save(O/'alphaframes'/p.name)
 if i in (0,9,18,27,36,45,54,63,71):
  thumb=out.resize((320,(H*320)//W));slot=(0,9,18,27,36,45,54,63,71).index(i);contact.paste(thumb,((slot%3)*320,(slot//3)*thumb.height))
  b=im.getchannel('A').getbbox();detail=out.crop(b);detail.resize((max(960,detail.width),int(detail.height*max(960,detail.width)/detail.width))).save(O/'details'/p.name)
contact.save(O/'contact.png')
records=json.load(open(O/'transform-receipt.json'))
source=json.load(open(O/'source-geometry-inspection.json'))
receipt={'source_blend':'design/scene-01/painted-layer-2026-10-05/painted-vehicles-driver-fixed-optimized.blend','authoring':'Blender direct Python, isolated candidate; no native source mutation','geometry':'retained PILOT 3 reconstructed crew-cab curved mesh and REPAIRED 3 detailed archived chassis; no UV cube; existing mirrors/wheels retained','source_frame_interval':[85,217],'frames':len(files),'fps':12,'duration_s':6,'dimensions':[W,H],'fixed_camera':source['camera'],'ROI':source['roi_normalized'],'full_render_resolution':source['full_render'],'tractor_heading_change_deg':records[-1]['tractor_heading_deg']-records[0]['tractor_heading_deg'],'trailer_heading_change_deg':records[-1]['trailer_heading_deg']-records[0]['trailer_heading_deg'],'background':'one static seeded gray asphalt-style RGB image reused every frame','visibility':'all city objects and other cars hidden; full green vehicle isolated','passes':['RGBA source color','mapped world normal multilayer EXR','object alpha PNG'],'driver_count':'two painted faces visually confirmed in structural-still/window detail at source120; rear heading naturally hides windshield','limitations':['Structural guide, not final approved painted style.','City hidden for turn physics isolation; does not establish map collision clearance.','Archived projected texture surface detail depends on heading.','Truck fixed union crop has smaller cabin detail; details/*.png are inspection crops, not animation camera.']}
(O/'receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))
