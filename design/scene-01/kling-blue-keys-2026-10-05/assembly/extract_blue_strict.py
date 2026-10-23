"""Bounded temporal-background blue-truck extraction; no learned model.

Run with uv run --no-project --with opencv-python-headless --with numpy python SCRIPT.
PNG RGBA layer and composited frames retain the provider's 1280x720 camera/padding.
"""
from pathlib import Path
import json
import sys
import cv2
import numpy as np

cv2.setNumThreads(1)
root = Path(__file__).resolve().parent
segment = int(sys.argv[1])
assert (root/f'segment-{segment}-receipt.json').exists(), 'Download and review first'
assert json.loads((root/f'segment-{segment}-receipt.json').read_text()).get('gate')=='motion_pass', 'Hard motion gate not passed'
config = {
 0:{'roi':(340,220,590,625),'allowed':[(375,230,450,575),(395,505,590,610)],'cab':(409,350)},
 1:{'roi':(470,180,755,625),'allowed':[(470,505,750,610),(665,180,740,610)],'cab':(530,550)},
 2:{'roi':(450,40,755,415),'allowed':[(665,60,740,415),(450,55,740,160)],'cab':(710,285)},
 3:{'roi':(340,40,610,410),'allowed':[(340,55,610,165),(375,70,450,410)],'cab':(490,120)},
}[segment]
out = root / f'segment-{segment}-strict'
out.mkdir(exist_ok=True)
source = root / f'segment-{segment}.mp4'
empty_path = root.parents[1] / 'four-truck-loop-2026-10-04/v2b-empty-map.png'
capture = cv2.VideoCapture(str(source))
fps = capture.get(cv2.CAP_PROP_FPS)
frames = []
while True:
    ok, frame = capture.read()
    if not ok:
        break
    frames.append(frame)
capture.release()
assert fps == 24 and len(frames) == 121 and frames[0].shape == (720, 1280, 3)
height, width = frames[0].shape[:2]
roi_box = config['roi']
x0, y0, x1, y1 = roi_box
stack = np.stack([frame[y0:y1, x0:x1] for frame in frames])
background = np.median(stack, axis=0).astype(np.uint8)
# Restore persistent white trailer pixels only where the clean map is road and temporal color varies strongly.
reference=np.full((720,1280,3),255,np.uint8);reference[:,121:1158]=cv2.resize(cv2.imread(str(empty_path)),(1037,720),interpolation=cv2.INTER_LANCZOS4)
ref=reference[y0:y1,x0:x1];bh=cv2.cvtColor(background,cv2.COLOR_BGR2HSV);rh=cv2.cvtColor(ref,cv2.COLOR_BGR2HSV)
variation=np.max(np.percentile(stack,95,axis=0)-np.percentile(stack,5,axis=0),axis=2)
restore=(bh[:,:,1]<30)&(bh[:,:,2]>170)&(rh[:,:,0]>=90)&(rh[:,:,0]<=115)&(rh[:,:,1]>40)&(variation>30)
background[restore]=ref[restore]
deviation = np.median(np.max(np.abs(stack.astype(np.int16)-background.astype(np.int16)), axis=3), axis=0)
threshold = np.maximum(25, deviation*3+10)
threshold[restore]=25
cv2.imwrite(str(out/'temporal-background-roi.png'), background)
allowed = np.zeros(background.shape[:2], np.uint8)
for ax0,ay0,ax1,ay1 in config['allowed']:
    cv2.rectangle(allowed, (ax0-x0,ay0-y0), (ax1-x0,ay1-y0), 255, -1)
empty = cv2.imread(str(empty_path))
scale = min(width/empty.shape[1], height/empty.shape[0])
scaled = cv2.resize(empty, (round(empty.shape[1]*scale), round(empty.shape[0]*scale)), interpolation=cv2.INTER_LANCZOS4)
base = np.full((height,width,3),255,np.uint8)
left,top = (width-scaled.shape[1])//2,(height-scaled.shape[0])//2
base[top:top+scaled.shape[0],left:left+scaled.shape[1]] = scaled
cv2.imwrite(str(out/'empty-map-padded.png'),base)
rgba_dir=out/'rgba-frames'; comp_dir=out/'composite-frames'
rgba_dir.mkdir(exist_ok=True); comp_dir.mkdir(exist_ok=True)
cab_rows=json.loads((root/f'segment-{segment}-layer/cab-tracking.json').read_text())['rows']
previous=np.array((config['cab'][0]-x0,config['cab'][1]-y0),np.float32)
records=[]; sampled={round(t*24):t for t in (0,.5,1.75,2.5,3.5,4.75)}
panels=[]
for index,frame in enumerate(frames):
    crop=frame[y0:y1,x0:x1]
    delta=np.max(np.abs(crop.astype(np.int16)-background.astype(np.int16)),axis=2)
    motion=((delta>threshold)&(allowed>0)).astype(np.uint8)*255
    hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
    green=((hsv[:,:,0]>=95)&(hsv[:,:,0]<=125)&(hsv[:,:,1]>=100)&((hsv[:,:,1]>=170)|(hsv[:,:,2]<240))&(hsv[:,:,2]>=35)&(motion>0)).astype(np.uint8)*255
    cab_center=np.array(cab_rows[index]['cab_px'])-[x0,y0]
    yy,xx=np.indices(green.shape)
    seed=((green>0)&((xx-cab_center[0])**2+(yy-cab_center[1])**2<26**2)).astype(np.uint8)*255
    if not np.any(seed):raise RuntimeError(f'No observed blue cab seed in frame {index+1}')
    connected=cv2.morphologyEx(motion,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    count,components,stats,centroids=cv2.connectedComponentsWithStats(connected)
    selected_labels=np.unique(components[seed>0]); selected_labels=selected_labels[selected_labels>0]
    candidate=np.isin(components,selected_labels).astype(np.uint8)*255
    # White trailer and blue cab define compact supports independently of dark road variation.
    white=((hsv[:,:,1]<20)&(hsv[:,:,2]>150)&(motion>0)).astype(np.uint8)*255
    white=cv2.morphologyEx(white,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    white_raw=white.copy()
    white=cv2.morphologyEx(white,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    wc,wl,ws,wcent=cv2.connectedComponentsWithStats(white)
    trailers=[j for j in range(1,wc) if 250<ws[j,cv2.CC_STAT_AREA]<3200 and np.linalg.norm(wcent[j]-cab_center)<115]
    if not trailers:
        raise RuntimeError(f'No intact white trailer in frame {index+1}')
    trailer=max(trailers,key=lambda j:ws[j,cv2.CC_STAT_AREA]/(np.linalg.norm(wcent[j]-cab_center)+25))
    axis=wcent[trailer]-cab_center;axis=axis/max(np.linalg.norm(axis),1e-6)
    fragments=[j for j in range(1,wc) if ws[j,cv2.CC_STAT_AREA]>60 and np.linalg.norm(wcent[j]-cab_center)<125 and np.dot(wcent[j]-cab_center,axis)>0 and abs(((wcent[j,0]-cab_center[0])*axis[1]-(wcent[j,1]-cab_center[1])*axis[0]))<18]
    trailer_mask=np.isin(wl,fragments).astype(np.uint8)*255
    # Recover narrow neutral front-roof fragments erased by the opening.
    rc,rl,rs,rcent=cv2.connectedComponentsWithStats(white_raw)
    front=[j for j in range(1,rc) if 25<rs[j,cv2.CC_STAT_AREA]<900 and np.linalg.norm(rcent[j]-cab_center)<65 and np.dot(rcent[j]-cab_center,axis)>0 and abs((rcent[j,0]-cab_center[0])*axis[1]-(rcent[j,1]-cab_center[1])*axis[0])<18 and max(rs[j,cv2.CC_STAT_WIDTH],rs[j,cv2.CC_STAT_HEIGHT])<65]
    trailer_mask[np.isin(rl,front)]=255
    cab_support=np.zeros_like(seed); trailer_support=np.zeros_like(seed)
    cv2.fillConvexPoly(cab_support,cv2.convexHull(cv2.findNonZero(seed)),255)
    cv2.fillConvexPoly(trailer_support,cv2.convexHull(cv2.findNonZero(trailer_mask)),255)
    cab_core=cab_support.copy()
    cab_support=cv2.dilate(cab_support,np.ones((9,9),np.uint8))
    trailer_core=trailer_support.copy()
    trailer_support=cv2.dilate(trailer_support,np.ones((7,7),np.uint8),anchor=(3,5))
    trailer_colors=(hsv[:,:,1]<20)|(hsv[:,:,2]<105)
    support=((cab_support>0)|((trailer_support>0)&trailer_colors)).astype(np.uint8)*255
    selected_labels=np.unique(components[(seed>0)|(trailer_mask>0)]);selected_labels=selected_labels[selected_labels>0];candidate=np.isin(components,selected_labels).astype(np.uint8)*255
    body=cv2.bitwise_and(candidate,support)
    body[cab_core>0]=255
    body[trailer_mask>0]=255
    white_support=cv2.dilate(trailer_core,np.ones((19,13),np.uint8),anchor=(6,8))
    body[(white_support>0)&(hsv[:,:,1]<20)&(hsv[:,:,2]>130)]=255
    contours,_=cv2.findContours(body,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(body,contours,-1,255,cv2.FILLED)
    body[(cab_support==0)&(hsv[:,:,1]>=20)&(hsv[:,:,2]>=105)]=0
    body[(cab_support==0)&(hsv[:,:,0]>=35)&(hsv[:,:,0]<=85)&(hsv[:,:,1]>60)]=0
    nc2,lab2,stat2,c2=cv2.connectedComponentsWithStats(body); keep=np.unique(lab2[(seed>0)|(trailer_mask>0)]);keep=keep[keep>0];body=np.isin(lab2,keep).astype(np.uint8)*255
    edge=cv2.GaussianBlur(body,(3,3),.6).astype(np.float32)/255
    broad=cv2.dilate(body,np.ones((11,11),np.uint8),anchor=(7,10))>0
    # Estimate neutral shadow opacity from relative background darkening; use black RGB.
    darkening=np.mean(background.astype(np.float32)-crop.astype(np.float32),axis=2)
    intensity=np.maximum(np.mean(background.astype(np.float32),axis=2),30)
    shadow=np.clip((darkening-3)/intensity,0,.45)*(broad&(body==0)&(allowed>0))
    shadow=cv2.GaussianBlur(shadow.astype(np.float32),(5,5),1)
    alpha=edge+(1-edge)*shadow
    rgb=np.zeros_like(crop,dtype=np.float32)
    rgb=np.divide(crop.astype(np.float32)*edge[:,:,None],alpha[:,:,None],out=rgb,where=alpha[:,:,None]>1e-6)
    alpha_full=np.zeros((height,width),np.float32); alpha_full[y0:y1,x0:x1]=alpha
    rgb_full=np.zeros_like(frame); rgb_full[y0:y1,x0:x1]=np.clip(rgb,0,255).round().astype(np.uint8)
    layer=np.dstack((rgb_full,(alpha_full*255).round().astype(np.uint8)))
    cv2.imwrite(str(rgba_dir/f'{index+1:04}.png'),layer)
    composite=np.clip(rgb_full.astype(np.float32)*alpha_full[:,:,None]+base.astype(np.float32)*(1-alpha_full[:,:,None]),0,255).round().astype(np.uint8)
    cv2.imwrite(str(comp_dir/f'{index+1:04}.png'),composite)
    ys,xs=np.where(body>0)
    record={'frame':index+1,'time':index/fps,'cab_center':[float(cab_center[0]+x0),float(cab_center[1]+y0)],'opaque_mask_pixels':int((body>0).sum()),'alpha_bbox':[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+x0+1),int(ys.max()+y0+1)],'motion_components':count-1}
    records.append(record)
    if index in sampled:
        checker=np.indices((height,width)).sum(axis=0)//16%2
        checkbase=np.where(checker[:,:,None],225,245).astype(np.float32)
        isolated=np.clip(rgb_full.astype(np.float32)*alpha_full[:,:,None]+checkbase*(1-alpha_full[:,:,None]),0,255).astype(np.uint8)
        triptych=np.concatenate((frame,isolated,composite),axis=1)
        cv2.putText(triptych,f'{sampled[index]}s: source | RGBA layer on checker | empty-map composite',(12,27),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,0,0),2,cv2.LINE_AA)
        cv2.imwrite(str(out/f'check-{index+1:04}.png'),triptych)
        panels.append(cv2.resize(triptych,(1920,360),interpolation=cv2.INTER_AREA))
        # Native detail evidence keeps every truck pixel inspectable.
        detail=np.concatenate((crop,isolated[y0:y1,x0:x1],composite[y0:y1,x0:x1]),axis=1)
        cv2.imwrite(str(out/f'detail-{index+1:04}.png'),detail)
cv2.imwrite(str(out/'before-after-contact.jpg'),np.concatenate(panels,axis=0))
report={'source':str(source),'empty_map':str(empty_path),'fps':fps,'frames':len(frames),'duration_seconds':len(frames)/fps,'provider_dimensions':[width,height],'empty_map_native_dimensions':[empty.shape[1],empty.shape[0]],'map_scale':scale,'map_padded_bounds':[left,top,left+scaled.shape[1],top+scaled.shape[0]],'roi_box':roi_box,'method':'Per-channel temporal median; per-pixel MAD threshold; connected moving blue cab seeded rig clipped to separate cab/trailer convex supports expanded 4px/3px; trailer excludes saturated blue asphalt; 1px feather and 7px neutral black soft-shadow region. No learned model.','static_other_trucks_included':False,'visual_acceptance':'PENDING: inspect all six native detail strips before judging mask quality.','frames_metrics':records}
(out/'extraction-report.json').write_text(json.dumps(report,indent=2))
print('EXTRACTED',len(frames),'RGBA frames; six sampled source/layer/composite comparisons',flush=True)
