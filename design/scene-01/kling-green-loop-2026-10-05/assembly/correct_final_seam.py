"""Bounded translation-only end-seam candidate. Source RGBA files stay untouched."""
from pathlib import Path
import json
import cv2
import numpy as np

cv2.setNumThreads(1)
p=Path(__file__).resolve().parent
out=p/'seam-correction';out.mkdir(exist_ok=True)
rgba=out/'rgba-frames';rgba.mkdir(exist_ok=True)
comps=out/'composite-frames';comps.mkdir(exist_ok=True)
first=p.parents[1]/'kling-layer-extract-2026-10-05'
source_files=sorted((p/'segment-4-layer/rgba-frames').glob('*.png'))[:120]
first_files=sorted((first/'rgba-frames').glob('*.png'))[:120]
def read(f): return cv2.imread(str(f),cv2.IMREAD_UNCHANGED)
def center(a):
    ys,xs=np.where(a[:,:,3]>127)
    return np.array([xs.mean(),ys.mean()])
centers=np.array([center(read(f)) for f in source_files])
start_centers=np.array([center(read(f)) for f in first_files[:8]])
start_velocity=np.polyfit(np.arange(8),start_centers,1)[0]
end_velocity=np.polyfit(np.arange(8),centers[-8:],1)[0]
delta=start_centers[0]-start_velocity-centers[-1]
velocity_delta=start_velocity-end_velocity
ramp_frames=36
base=cv2.imread(str(p/'segment-4-layer/empty-map-padded.png'))
hsv=cv2.cvtColor(base,cv2.COLOR_BGR2HSV)
road=((hsv[:,:,0]>=90)&(hsv[:,:,0]<=115)&(hsv[:,:,1]>45)&(hsv[:,:,2]>120)).astype(np.uint8)*255
road=cv2.morphologyEx(road,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
count,labels,stats,points=cv2.connectedComponentsWithStats(road)
label=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);road=(labels==label).astype(np.uint8)
distance=cv2.distanceTransform(road,cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
records=[];corrected_centers=[]
for index,f in enumerate(source_files):
    a=read(f);t=np.clip((index-(120-ramp_frames))/(ramp_frames-1),0,1)
    offset=(-2*t**3+3*t**2)*delta+(t**3-t**2)*(ramp_frames-1)*velocity_delta
    transform=np.array([[1,0,offset[0]],[0,1,offset[1]]],np.float32)
    working=a.astype(np.float32)
    working[:,:,:3]*=working[:,:,3:4]/255
    warped=cv2.warpAffine(working,transform,(1280,720),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    restored=np.divide(warped[:,:,:3],warped[:,:,3:4]/255,out=np.zeros_like(warped[:,:,:3]),where=warped[:,:,3:4]>1e-6)
    corrected=np.dstack((restored,warped[:,:,3])).clip(0,255).round().astype(np.uint8)
    cv2.imwrite(str(rgba/f'{index+1:04}.png'),corrected)
    alpha=corrected[:,:,3:4].astype(np.float32)/255
    composite=(corrected[:,:,:3]*alpha+base*(1-alpha)).round().astype(np.uint8)
    cv2.imwrite(str(comps/f'{index+1:04}.png'),composite)
    corrected_centers.append(center(corrected))
    body=corrected[:,:,3]>127
    records.append({'frame':index+1,'offset_pixels':offset.tolist(),'projected_body_road_clearance_pixels':float(distance[body].min())})
corrected_centers=np.array(corrected_centers)
target=read(first_files[0]);original=read(source_files[-1]);corrected=read(rgba/'0120.png')
def iou(a,b):
    aa=a[:,:,3]>127;bb=b[:,:,3]>127
    return float(np.count_nonzero(aa&bb)/np.count_nonzero(aa|bb))
join=start_centers[0]-corrected_centers[-1]
steps=np.linalg.norm(np.diff(corrected_centers,axis=0),axis=1)
original_steps=np.linalg.norm(np.diff(centers,axis=0),axis=1)
original_end=cv2.imread(str(p/'segment-4-layer/composite-frames/0120.png'))
corrected_end=cv2.imread(str(comps/'0120.png'))
next_start=cv2.imread(str(first/'composite-frames/0001.png'))
x0,y0=870,150
tiles=[image[y0:y0+210,x0:x0+210].copy() for image in (original_end,corrected_end,next_start)]
for image,label in zip(tiles,('Original end','Translated end','Next start')):
    cv2.putText(image,label,(5,19),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
cv2.imwrite(str(out/'boundary-comparison.png'),cv2.hconcat(tiles))
report={'type':'translation_only_candidate','scale':1,'rotation':0,'rig_deformed':False,'ghost_crossfade':False,'ramp_frames':ramp_frames,'end_translation_pixels':delta.tolist(),'max_translation_norm_pixels':float(max(np.linalg.norm(r['offset_pixels']) for r in records)),'source_start_velocity_pixels_per_frame':start_velocity.tolist(),'original_end_velocity_pixels_per_frame':end_velocity.tolist(),'original_join_center_displacement_pixels':float(np.linalg.norm(start_centers[0]-centers[-1])),'corrected_join_center_step_pixels':float(np.linalg.norm(join)),'corrected_join_vector_pixels':join.tolist(),'original_alpha_iou':iou(original,target),'corrected_alpha_iou':iou(corrected,target),'original_ramp_step_range_pixels':[float(original_steps[-ramp_frames:].min()),float(original_steps[-ramp_frames:].max())],'original_last8_mean_step_pixels':float(original_steps[-8:].mean()),'corrected_last8_mean_step_pixels':float(steps[-8:].mean()),'corrected_last_step_pixels':float(steps[-1]),'next_start_first7_mean_step_pixels':float(np.linalg.norm(np.diff(start_centers,axis=0),axis=1).mean()),'corrected_ramp_step_range_pixels':[float(steps[-ramp_frames:].min()),float(steps[-ramp_frames:].max())],'corrected_end_projected_body_road_clearance_pixels':records[-1]['projected_body_road_clearance_pixels'],'corrected_ramp_min_projected_body_road_clearance_pixels':min(r['projected_body_road_clearance_pixels'] for r in records[-ramp_frames:]),'clearance_method':'Largest connected blue road color region in exact empty-map-padded.png; 9px closing fills white lane/crosswalk marks; distance to region edge measured over opaque projected vehicle silhouette. This is projected body clearance, not world wheel clearance.','status':'VISUAL REVIEW PENDING; original layers preserved.','frame_corrections':records}
(out/'correction-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='frame_corrections'},indent=2))
