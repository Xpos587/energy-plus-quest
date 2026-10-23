from pathlib import Path
import json,cv2,numpy as np
cv2.setNumThreads(1)
r=Path(__file__).parent;p=r.parent/'kling-green-loop-2026-10-05/assembly/candidate-22.75s';idx=285
row=json.loads((p/'green-tracking.json').read_text())['rows'][idx];cx,cy=row['cab_px'];im=cv2.imread(str(p/'composite-frames'/f'{idx+1:04}.png'));x0,y0=round(cx-25),round(cy-25);crop=im[y0:y0+50,x0:x0+50];hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
green=((hsv[:,:,0]>35)&(hsv[:,:,0]<85)&(hsv[:,:,1]>45)&(hsv[:,:,2]>30)).astype(np.uint8)*255
n,l,s,c=cv2.connectedComponentsWithStats(green);keep=[j for j in range(1,n) if s[j,4]>15];hull=np.zeros_like(green);cv2.fillConvexPoly(hull,cv2.convexHull(cv2.findNonZero(np.isin(l,keep).astype(np.uint8))),255)
glass=((hsv[:,:,0]>85)&(hsv[:,:,0]<125)&(hsv[:,:,1]>15)&(hsv[:,:,2]>30)&(hull>0)).astype(np.uint8)*255
n,l,s,c=cv2.connectedComponentsWithStats(glass);j=max(range(1,n),key=lambda j:s[j,4]);pts=cv2.findNonZero((l==j).astype(np.uint8));rect=cv2.minAreaRect(pts);box=cv2.boxPoints(rect)+[x0,y0]
def order(a):
 out=np.zeros((4,2),np.float32);sm=a.sum(1);df=np.diff(a,axis=1).ravel();out[0]=a[np.argmin(sm)];out[2]=a[np.argmax(sm)];out[1]=a[np.argmin(df)];out[3]=a[np.argmax(df)];return out
box=order(box);template=cv2.imread(str(r/'green-detail-reference.png'));th,tw=template.shape[:2]
# Explicit windshield interior quad; body, mirrors and roadside are excluded.
q=np.array([[444,229],[788,238],[791,371],[432,369]],np.float32);q[:,0]*=tw/1255;q[:,1]*=th/1246
scale=3;large=cv2.resize(im,(1280*scale,720*scale),interpolation=cv2.INTER_LANCZOS4);M=cv2.getPerspectiveTransform(q,box*scale);warped=cv2.warpPerspective(template,M,(large.shape[1],large.shape[0]));mask=np.zeros(large.shape[:2],np.uint8);cv2.fillConvexPoly(mask,np.round(box*scale).astype(np.int32),255);mask=cv2.GaussianBlur(mask,(3,3),.5).astype(np.float32)/255
out=np.clip(warped*mask[:,:,None]+large*(1-mask[:,:,None]),0,255).round().astype(np.uint8);cv2.imwrite(str(r/'green-window-pilot-3840.png'),out)
check=im.copy();cv2.polylines(check,[box.astype(np.int32)],True,(0,0,255),1);cv2.imwrite(str(r/'window-source-detection.png'),check[y0:y0+50,x0:x0+50]);cv2.imwrite(str(r/'window-pilot-detail.png'),out[(y0-5)*scale:(y0+50)*scale,(x0-5)*scale:(x0+50)*scale]);(r/'window-pilot-receipt.json').write_text(json.dumps({'frame':idx,'cab_anchor':[cx,cy],'source_glass_quad':box.tolist(),'template_quad':q.tolist(),'output_dimensions':[3840,2160],'change':'AI-generated windshield interior only; 0.5px feather; rest is ordinary Lanczos upsample, not new source detail','driver_count':'two on template, one steering wheel; animated placement not yet verified'},indent=2));print(box.tolist())
