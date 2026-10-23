from pathlib import Path
import json
import subprocess
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

P = Path(__file__).resolve().parents[1]
R = Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('Review', '/usr/share/fonts/TTF/DejaVuSans.ttf'))
C = canvas.Canvas(str(R/'energy-plus-map-3d-v02.pdf'), pagesize=(842,595))
C.setTitle('Энергия+ · Первая сцена · 3D-проба v02')
def title(text, meta='v02'):
    C.setFillColorRGB(.08,.17,.24)
    C.setFont('Review',19)
    C.drawString(30,558,text)
    C.setFont('Review',10)
    C.setFillColorRGB(.36,.45,.50)
    C.drawRightString(810,559,meta)
def label(text,x,y):
    C.setFont('Review',10)
    C.setFillColorRGB(.24,.35,.43)
    C.drawString(x,y,text)
def image(path,box,trim=False,crop=None):
    im=Image.open(path).convert('RGBA')
    if crop: im=im.crop(crop)
    if trim: im=im.crop(im.getchannel('A').getbbox())
    bg=Image.new('RGBA',im.size,'white'); bg.alpha_composite(im)
    x,y,w,h=box; k=min(w/im.width,h/im.height); iw,ih=im.width*k,im.height*k
    C.drawImage(ImageReader(bg.convert('RGB')),x+(w-iw)/2,y+(h-ih)/2,iw,ih)
title('Первая сцена · зелёная фура')
label('Эталон · текущая игра',30,520)
image(P.parents[2]/'public/scene-art/carrier-results-2026-10-02/crew-wide-v6.webp',(30,300,390,200))
label('Референс для 3D',30,270)
image(P/'image-to-3d/green-tractor-reference.png',(30,38,390,220),True)
label('3D-проба · 900 × 900',445,520)
image(P/'image-to-3d/detail-three-quarter.png',(445,58,365,442),True)
C.showPage()
title('Кабина · до / после','v01 → v02 · 900 × 900')
label('v01',30,515); label('v02',440,515)
image(P/'image-to-3d/finished-front.png',(30,215,370,280),True)
image(P/'image-to-3d/detail-front.png',(440,215,370,280),True)
image(P/'image-to-3d/finished-front.png',(30,55,370,125),crop=(285,565,625,675))
image(P/'image-to-3d/detail-front.png',(440,55,370,125),crop=(285,565,625,675))
C.showPage()
M=P/'image-to-3d/motion'; video=M/'green-tractor-turn-detailed.mp4'
if video.exists():
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate:format=duration','-of','json',str(video)]))
    stream=info['streams'][0]; a,b=map(int,stream['r_frame_rate'].split('/'))
    title('Поворот · проба движения','v02 · %.1f с · %g fps'%(float(info['format']['duration']),a/b))
    for filename,x,caption in [('entry-detailed.png',30,'Вход'),('apex-detailed.png',292,'Поворот'),('exit-detailed.png',554,'Выход')]:
        label(caption,x,507); image(M/filename,(x,190,245,285))
    label('%d × %d · один тягач и полуприцеп'%(stream['width'],stream['height']),30,100)
    C.showPage()
C.save()
print('PDF v02 written')
