"""Bounded temporal-background green-truck extraction; no learned model.

Run with uv run --no-project --with opencv-python-headless --with numpy python SCRIPT.
PNG RGBA layer and composited frames retain the provider's 1280x720 camera/padding.
"""
from pathlib import Path
import json
import cv2
import numpy as np

cv2.setNumThreads(1)
out = Path(__file__).resolve().parent
source = out.parent / 'kling-bounded-2026-10-05/green-only.mp4'
empty_path = out.parent / 'four-truck-loop-2026-10-04/v2b-empty-map.png'
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
roi_box = (690, 65, 1005, 320)
x0, y0, x1, y1 = roi_box
stack = np.stack([frame[y0:y1, x0:x1] for frame in frames])
background = np.median(stack, axis=0).astype(np.uint8)
deviation = np.median(np.max(np.abs(stack.astype(np.int16)-background.astype(np.int16)), axis=3), axis=0)
threshold = np.maximum(11, deviation*3+6)
cv2.imwrite(str(out/'temporal-background-roi.png'), background)
allowed = np.zeros(background.shape[:2], np.uint8)
cv2.rectangle(allowed, (930-x0,65-y0), (1004-x0,319-y0), 255, -1)
cv2.rectangle(allowed, (690-x0,65-y0), (1004-x0,175-y0), 255, -1)
empty = cv2.imread(str(empty_path))
scale = min(width/empty.shape[1], height/empty.shape[0])
scaled = cv2.resize(empty, (round(empty.shape[1]*scale), round(empty.shape[0]*scale)), interpolation=cv2.INTER_LANCZOS4)
base = np.full((height,width,3),255,np.uint8)
left,top = (width-scaled.shape[1])//2,(height-scaled.shape[0])//2
base[top:top+scaled.shape[0],left:left+scaled.shape[1]] = scaled
cv2.imwrite(str(out/'empty-map-padded.png'),base)
rgba_dir=out/'rgba-frames'; comp_dir=out/'composite-frames'
rgba_dir.mkdir(exist_ok=True); comp_dir.mkdir(exist_ok=True)
previous=np.array((977-x0,210-y0),np.float32)
records=[]; sampled={round(t*24):t for t in (0,.5,1.75,2.5,3.5,4.75)}
panels=[]
for index,frame in enumerate(frames):
    crop=frame[y0:y1,x0:x1]
    delta=np.max(np.abs(crop.astype(np.int16)-background.astype(np.int16)),axis=2)
    motion=((delta>threshold)&(allowed>0)).astype(np.uint8)*255
    hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
    green=((hsv[:,:,0]>=35)&(hsv[:,:,0]<=90)&(hsv[:,:,1]>=65)&(hsv[:,:,2]>=35)&(motion>0)).astype(np.uint8)*255
    count,labels,stats,centroids=cv2.connectedComponentsWithStats(green)
    candidates=[j for j in range(1,count) if stats[j,cv2.CC_STAT_AREA]>=8]
    if not candidates:
        raise RuntimeError(f'No moving green cab in frame {index+1}')
    cab=min(candidates,key=lambda j:np.linalg.norm(centroids[j]-previous)-min(stats[j,cv2.CC_STAT_AREA],250)*.015)
    cab_center=centroids[cab]; previous=cab_center
    seed=(labels==cab).astype(np.uint8)*255
    connected=cv2.morphologyEx(motion,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    count,components,stats,centroids=cv2.connectedComponentsWithStats(connected)
    selected_labels=np.unique(components[seed>0]); selected_labels=selected_labels[selected_labels>0]
    candidate=np.isin(components,selected_labels).astype(np.uint8)*255
    # White trailer and green cab define compact supports independently of dark road variation.
    white=((hsv[:,:,1]<70)&(hsv[:,:,2]>150)&(motion>0)).astype(np.uint8)*255
    white=cv2.morphologyEx(white,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    wc,wl,ws,wcent=cv2.connectedComponentsWithStats(white)
    trailers=[j for j in range(1,wc) if 250<ws[j,cv2.CC_STAT_AREA]<3200 and np.linalg.norm(wcent[j]-cab_center)<115]
    if not trailers:
        raise RuntimeError(f'No intact white trailer in frame {index+1}')
    trailer=max(trailers,key=lambda j:ws[j,cv2.CC_STAT_AREA]/(np.linalg.norm(wcent[j]-cab_center)+25))
    trailer_mask=(wl==trailer).astype(np.uint8)*255
    cab_support=np.zeros_like(seed); trailer_support=np.zeros_like(seed)
    cv2.fillConvexPoly(cab_support,cv2.convexHull(cv2.findNonZero(seed)),255)
    cv2.fillConvexPoly(trailer_support,cv2.convexHull(cv2.findNonZero(trailer_mask)),255)
    cab_support=cv2.dilate(cab_support,np.ones((9,9),np.uint8))
    trailer_support=cv2.dilate(trailer_support,np.ones((7,7),np.uint8))
    trailer_colors=(hsv[:,:,1]<85)|(hsv[:,:,2]<105)
    support=((cab_support>0)|((trailer_support>0)&trailer_colors)).astype(np.uint8)*255
    body=cv2.bitwise_and(candidate,support)
    contours,_=cv2.findContours(body,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(body,contours,-1,255,cv2.FILLED)
    edge=cv2.GaussianBlur(body,(3,3),.6).astype(np.float32)/255
    broad=cv2.dilate(body,np.ones((15,15),np.uint8))>0
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
report={'source':str(source),'empty_map':str(empty_path),'fps':fps,'frames':len(frames),'duration_seconds':len(frames)/fps,'provider_dimensions':[width,height],'empty_map_native_dimensions':[empty.shape[1],empty.shape[0]],'map_scale':scale,'map_padded_bounds':[left,top,left+scaled.shape[1],top+scaled.shape[0]],'roi_box':roi_box,'method':'Per-channel temporal median; per-pixel MAD threshold; connected moving green cab seeded rig clipped to separate cab/trailer convex supports expanded 4px/3px; trailer excludes saturated blue asphalt; 1px feather and 7px neutral black soft-shadow region. No learned model.','static_other_trucks_included':False,'visual_acceptance':'PENDING: inspect all six native detail strips before judging mask quality.','frames_metrics':records}
(out/'extraction-report.json').write_text(json.dumps(report,indent=2))
print('EXTRACTED',len(frames),'RGBA frames; six sampled source/layer/composite comparisons',flush=True)
