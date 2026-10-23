from pathlib import Path
import xml.etree.ElementTree as ET
import json
import cairosvg,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
P=Path(__file__).resolve().parent
ROOT=P.parents[3]
old=Image.open(P.parents[1]/'fleet-road-v11-2026-10-07/backdrop-v11.png').convert('RGBA')
city=Image.open(P/'candidate-resized.png').convert('RGBA')
# Preserve the requested three short loading bays from the generated candidate.
# Three new short loading bays are intentionally preserved.
# Recover original facade pixels where image generation added generic lettering.
facade=Image.new('L',city.size);ImageDraw.Draw(facade).polygon([(259,368),(406,378),(406,415),(259,405)],fill=255);facade=facade.filter(ImageFilter.GaussianBlur(2));city=Image.composite(old,city,facade)
source=ROOT/'public/brand/gpn-snabzhenie.svg'
svg=ET.parse(source);svg.getroot().set('viewBox','0 0 207 100.04');svg.getroot().set('width','207');svg.getroot().set('height','100.04');svg.write(P/'gazprom-neft-extracted.svg',encoding='utf-8',xml_declaration=True)
cairosvg.svg2png(url=str(P/'gazprom-neft-extracted.svg'),write_to=str(P/'gazprom-neft-vector.png'),output_width=828,output_height=400)
logo=Image.open(P/'gazprom-neft-vector.png').convert('RGBA')
# One physically planar sign: four corners follow the warehouse front-face slope.
sign=Image.new('RGBA',(900,200));sign.alpha_composite(logo.resize((330,159),Image.Resampling.LANCZOS),(25,16))
ImageDraw.Draw(sign).text((440,62),'СКЛАД',font=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',91),fill='#0070ba')
quad=np.float32([[244,370],[416,380],[416,413],[244,403]])
matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[900,0],[900,200],[0,200]]),quad)
warped=cv2.warpPerspective(np.asarray(sign),matrix,city.size,flags=cv2.INTER_CUBIC)
city=Image.alpha_composite(city,Image.fromarray(warped));city.save(P/'city-brand-final.png')
city.crop((180,200,535,585)).resize((1065,1155),Image.Resampling.LANCZOS).save(P/'warehouse-enlarged.png')
(P/'city-provenance.json').write_text(json.dumps({'original_background':'fleet-road-v11-2026-10-07/backdrop-v11.png','generated_candidate':'generated-candidate.png','candidate_resized':[1920,1334],'alignment':'alignment.json; regional measured shifts below 1px, visual overlay inspected','restored_original_regions':['blank facade under generated text; СКЛАД replaced with adjacent vector label'],'brand_source':str(source),'brand_svg_viewbox':'0 0 207 100.04','sign_corners':quad.tolist(),'scope':'Concept city backdrop with exact existing brand; not deployed game'},indent=2))
