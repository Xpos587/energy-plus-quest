"""Similarity registration with nondegenerate, scale and spatial support gates."""
import cv2,numpy as np
cv2.setNumThreads(1)

def geometry_guard(matrix,reference_dimensions,generated_dimensions,source_points=None,target_points=None):
 failures=[];matrix=np.asarray(matrix,dtype=float);finite=matrix.shape==(2,3)and np.isfinite(matrix).all()
 determinant=float(np.linalg.det(matrix[:,:2]))if finite else None
 scale=float(np.hypot(matrix[0,0],matrix[1,0]))if finite else None
 rw,rh=reference_dimensions;gw,gh=generated_dimensions;expected=float(np.sqrt(rw*rh/(gw*gh)))
 if not finite or determinant<=1e-12 or scale<=1e-6:failures.append('nondegenerate')
 ratio=scale/expected if finite else None
 if ratio is None or not .8<=ratio<=1.25:failures.append('expected_scale')
 support=[]
 for points,(width,height)in [(source_points,generated_dimensions),(target_points,reference_dimensions)]:
  if points is None:continue
  points=np.asarray(points,dtype=np.float32).reshape(-1,2)
  if len(points)<3 or not np.isfinite(points).all():coverage=0.;span=[0.,0.]
  else:coverage=float(cv2.contourArea(cv2.convexHull(points))/(width*height));span=(np.ptp(points,axis=0)/[width,height]).tolist()
  support.append({'hullFraction':coverage,'spanFraction':span})
  if coverage<.005 or min(span)<.1:failures.append('spatial_coverage')
 return {'accepted':not failures,'failures':sorted(set(failures)),'determinant':determinant,'scale':scale,'expectedScale':expected,'scaleRatio':ratio,'support':support,'policy':'positive determinant; scale/expected in[0.8,1.25]; inlier hull>=0.5% and span>=10% on both axes in both images'}

def register(reference,generated,reference_pixels_per_source_pixel=1.0):
 a=cv2.cvtColor(reference,cv2.COLOR_BGR2GRAY);b=cv2.cvtColor(generated,cv2.COLOR_BGR2GRAY)
 sift=cv2.SIFT_create(nfeatures=6000);ka,da=sift.detectAndCompute(a,None);kb,db=sift.detectAndCompute(b,None)
 if da is None or db is None:return None,{'matches':0,'accepted':False,'reason':'featureless image'}
 matches=cv2.BFMatcher().knnMatch(db,da,k=2);good=[pair[0]for pair in matches if len(pair)==2 and pair[0].distance<.72*pair[1].distance]
 if len(good)<8:return None,{'matches':len(good),'accepted':False,'reason':'too few correspondences'}
 src=np.float32([kb[m.queryIdx].pt for m in good]);dst=np.float32([ka[m.trainIdx].pt for m in good]);affine,inliers=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2.*reference_pixels_per_source_pixel,maxIters=8000,confidence=.999)
 if affine is None or inliers is None:return None,{'matches':len(good),'accepted':False,'reason':'similarity not found'}
 goodidx=inliers.ravel().astype(bool)
 guard=geometry_guard(affine,(reference.shape[1],reference.shape[0]),(generated.shape[1],generated.shape[0]),src[goodidx],dst[goodidx])
 if not np.isfinite(affine).all():return None,{'matches':len(good),'accepted':False,'geometryGuard':guard,'reason':'nonfinite similarity matrix'}
 if not goodidx.any():return affine,{'matches':len(good),'accepted':False,'geometryGuard':guard,'reason':'no inliers'}
 mapped=cv2.transform(src[None],affine)[0];errors=np.linalg.norm(mapped-dst,axis=1);scale=float(np.hypot(affine[0,0],affine[1,0]));rotation=float(np.degrees(np.arctan2(affine[1,0],affine[0,0])))
 metric={'matches':len(good),'inliers':int(goodidx.sum()),'inlierFraction':float(goodidx.mean()),'referencePixelsPerSourcePixel':reference_pixels_per_source_pixel,'meanResidualReferencePx':float(errors[goodidx].mean()),'p95ResidualReferencePx':float(np.percentile(errors[goodidx],95)),'meanResidualSourcePx':float(errors[goodidx].mean()/reference_pixels_per_source_pixel),'p95ResidualSourcePx':float(np.percentile(errors[goodidx],95)/reference_pixels_per_source_pixel),'scale':scale,'rotationDegrees':rotation,'affineGeneratedToReference':affine.tolist(),'geometryGuard':guard}
 metric['accepted']=guard['accepted']and metric['inliers']>=12 and metric['inlierFraction']>=.45 and metric['p95ResidualSourcePx']<=1.8 and abs(rotation)<=.6
 return affine,metric
