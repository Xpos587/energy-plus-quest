from pathlib import Path
import cairosvg,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
city=Image.open(P/'city-detail.png').convert('RGBA')
svg=P.parents[1]/'fleet-v19-city-occlusion-2026-10-08/city/gazprom-neft-extracted.svg'
cairosvg.svg2png(url=str(svg),write_to=str(P/'logo-exact.png'),output_width=330,output_height=160)
logo=Image.open(P/'logo-exact.png').convert('RGBA')
sign=Image.new('RGBA',(900,210),(0,0,0,0));sign.alpha_composite(logo,(30,25))
ImageDraw.Draw(sign).text((465,65),'СКЛАД',font=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',80),fill='#0070ba')
quad=np.float32([[451,640],[861,670],[861,741],[451,711]])
m=cv2.getPerspectiveTransform(np.float32([[0,0],[900,0],[900,210],[0,210]]),quad)
rgba=np.asarray(sign,dtype=np.float32)/255
rgba[:,:,:3]*=rgba[:,:,3:4]
warped=cv2.warpPerspective(rgba,m,city.size,flags=cv2.INTER_LINEAR)
alpha=warped[:,:,3:4]
warped[:,:,:3]=np.divide(warped[:,:,:3],alpha,out=np.zeros_like(warped[:,:,:3]),where=alpha>1e-6)
city=Image.alpha_composite(city,Image.fromarray(np.rint(np.clip(warped,0,1)*255).astype(np.uint8)))
city.save(P/'city-final.png');city.crop((340,360,1080,1140)).save(P/'warehouse-final-crop.png')
