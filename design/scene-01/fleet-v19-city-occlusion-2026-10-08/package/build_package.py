from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,subprocess
P=Path(__file__).resolve().parent;BASE=P.parent;SCENE=BASE.parent
bg=Image.open(BASE/'city/city-brand-final.png').convert('RGBA')
old=Image.open(SCENE/'fleet-road-v11-2026-10-07/backdrop-v11.png').convert('RGBA')
mask=np.asarray(Image.open(SCENE/'fleet-lookdev-v10-2026-10-07/road-receiver-mask.png').convert('L'),dtype=np.float32)/255
shadowdir=SCENE/'fleet-v16-wheels-style-2026-10-08/turn-shadow'
def compose(f,background=bg,before=False):
 alpha=Image.open(shadowdir/f'{f:04}.png').getchannel('A').filter(ImageFilter.GaussianBlur(1.3)).resize(bg.size,Image.Resampling.LANCZOS)
 alpha=np.rint(np.asarray(alpha,dtype=np.float32)*mask*.48).astype(np.uint8)
 shadow=Image.new('RGBA',bg.size,(83,91,96,0));shadow.putalpha(Image.fromarray(alpha))
 folder='before' if before else 'passage'
 vehicle=Image.open(BASE/'occlusion'/folder/f'{f:04}.png').convert('RGBA')
 return Image.alpha_composite(Image.alpha_composite(background,shadow),vehicle).convert('RGB')
output=P/'v19-city-occlusion-2s.mp4'
proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1334','-r','24','-i','-','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
for f in range(129,177):
 im=compose(f);proc.stdin.write(im.tobytes())
 if f in (129,134,150,154,158,176):im.save(P/f'full-map-{f:04}.png')
proc.stdin.close();assert proc.wait()==0
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames,r_frame_rate,duration','-of','json',str(output)]))
assert probe['streams'][0]['nb_read_frames']=='48' and probe['streams'][0]['duration']=='2.000000'
assert subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-']).returncode==0
font='/usr/share/fonts/TTF/DejaVuSans.ttf';bold='/usr/share/fonts/TTF/DejaVuSans-Bold.ttf'
def page(title,subtitle):
 im=Image.new('RGB',(1600,1100),'#f6f5f0');d=ImageDraw.Draw(im)
 d.text((60,36),title,font=ImageFont.truetype(bold,42),fill='#193446');d.text((60,94),subtitle,font=ImageFont.truetype(font,23),fill='#536472');return im
pages=[]
p=page('V19 / Город и грузовики','08.10.2026 · Визуальная проверка сцены')
warehouse=Image.open(BASE/'city/warehouse-enlarged.png').convert('RGB');warehouse.thumbnail((910,880));p.paste(warehouse,(60,165));d=ImageDraw.Draw(p)
for y,t in [(205,'Склад'),(275,'Логотип «Газпром нефть»'),(312,'из исходного SVG'),(380,'Три двери — три места'),(490,'Колёса прицепов'),(560,'Шаг осей: 0,87 → 0,77'),(597,'Форма и материалы сохранены'),(720,'Следующие страницы'),(790,'Перекрытие машин зданиями'),(827,'и полный кадр карты')]:
 d.text((1000,y),t,font=ImageFont.truetype(bold if y in (205,490,720) else font,25),fill='#193446')
d.text((60,1060),'Проверочный рендер. Изменения не опубликованы в игре.',font=ImageFont.truetype(font,19),fill='#536472');pages.append(p)
p=page('Машины проходят за зданиями','Тот же кадр 134 · те же маршруты · исправлена видимость за крышами')
box=(995,160,1555,390);a=compose(134,old,True).crop(box);b=compose(134).crop(box)
for im,y,label in [(a,165,'ДО'),(b,615,'ПОСЛЕ')]:
 im=im.resize((1008,414),Image.Resampling.LANCZOS);p.paste(im,(430,y));ImageDraw.Draw(p).text((70,y+28),label,font=ImageFont.truetype(bold,29),fill='#193446')
pages.append(p)
p=page('Полная карта','Кадр 154 · компактные оси, склад с логотипом и машины за зданиями')
im=compose(154);im.thumbnail((1400,900));p.paste(im,((1600-im.width)//2,155));pages.append(p)
for n,p in enumerate(pages,1):p.save(P/f'page-{n:02}.png')
pages[0].save(P/'v19-city-occlusion-review.pdf',save_all=True,append_images=pages[1:],resolution=144)
(P/'package-validation.json').write_text(json.dumps({'video':probe,'decode_exit':0,'pdf_pages':3,'frames':[129,176],'city':'../city/city-brand-final.png','vehicle_alpha':'../occlusion/passage','shadow_source':str(shadowdir),'shadow_note':'Original matching frame mesh shadows reuse pre-compact axle source; small axle-position difference possible. Road receiver mask excludes roofs.','scope':'Visual proof only, not deployed game'},indent=2))
print(output);print(P/'v19-city-occlusion-review.pdf')
