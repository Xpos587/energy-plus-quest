import cv2,numpy as np

def roof_polygon(crop,cab,previous,q):
 lines=cv2.HoughLinesP(cv2.Canny(crop,60,160),1,np.pi/180,round(20*q),minLineLength=round(30*q),maxLineGap=round(7*q))
 if lines is None:return None
 items=[]
 for x0,y0,x1,y1 in lines.reshape(-1,4):
  p=np.array([x0,y0],float);z=np.array([x1,y1],float);length=np.linalg.norm(z-p);mid=(p+z)/2
  if 30*q<=length<=125*q and np.linalg.norm(mid-previous)<22*q and 18*q<np.linalg.norm(mid-cab)<130*q:items.append((p,z,(z-p)/length,length,mid))
 pairs=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   v=a[2];normal=np.array([-v[1],v[0]])
   if abs(np.dot(v,b[2]))<.985:continue
   width=abs(np.dot(b[4]-a[4],normal));middle=(a[4]+b[4])/2
   if not 12*q<=width<=34*q:continue
   ap=sorted([np.dot(a[0],v),np.dot(a[1],v)]);bp=sorted([np.dot(b[0],v),np.dot(b[1],v)]);lo=max(ap[0],bp[0]);hi=min(ap[1],bp[1])
   if hi-lo<30*q:continue
   # Use measured edge extent; reject long street/curb boundaries.
   lo=min(ap[0],bp[0]);hi=max(ap[1],bp[1]);n0=np.dot(a[4],normal);n1=np.dot(b[4],normal)
   if hi-lo>115*q:continue
   poly=np.array([v*lo+normal*n0,v*hi+normal*n0,v*hi+normal*n1,v*lo+normal*n1])
   mask=np.zeros(crop.shape[:2],np.uint8);cv2.fillConvexPoly(mask,poly.round().astype(np.int32),255);h=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV);fraction=np.mean(((h[:,:,1]<100)&(h[:,:,2]>130))[mask>0])
   if fraction<.65:continue
   score=np.linalg.norm(middle-previous)+.2*np.linalg.norm(middle-cab)-.07*(a[3]+b[3])
   pairs.append((score,poly,middle))
 if not pairs:return None
 _,poly,center=min(pairs,key=lambda x:x[0]);return poly.round().astype(np.int32),center
