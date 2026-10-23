import importlib.util,unittest,json
from unittest.mock import patch
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('registration',Path(__file__).with_name('registration.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RegistrationTests(unittest.TestCase):
 def test_collapsed_affine_rejected_despite_zero_residual(self):
  points=np.array([[0,0],[100,0],[0,100],[100,100]],float)
  result=m.geometry_guard(np.array([[0,0,90],[0,0,199]],float),(710,354),(1777,885),points,points)
  self.assertFalse(result['accepted']);self.assertIn('nondegenerate',result['failures'])
 def test_expected_resize_with_distributed_inliers_is_valid(self):
  points=np.array([[10,10],[90,10],[10,90],[90,90]],float)
  result=m.geometry_guard(np.array([[.5,0,0],[0,.5,0]],float),(100,100),(200,200),points*2,points)
  self.assertTrue(result['accepted'])
 def test_local_repeating_cluster_is_insufficient_global_evidence(self):
  points=np.array([[10,10],[11,10],[10,11],[11,11]],float)
  result=m.geometry_guard(np.array([[.5,0,0],[0,.5,0]],float),(100,100),(200,200),points*2,points)
  self.assertFalse(result['accepted']);self.assertIn('spatial_coverage',result['failures'])
 def test_wrong_scale_and_nonfinite_transform_are_rejected(self):
  points=np.array([[10,10],[90,10],[10,90],[90,90]],float)
  for matrix in [np.array([[.01,0,0],[0,.01,0]]),np.array([[np.nan,0,0],[0,1,0]])]:
   self.assertFalse(m.geometry_guard(matrix,(100,100),(200,200),points,points)['accepted'])
 def test_nonfinite_ransac_cannot_write_nan_into_job_json(self):
  image=np.random.default_rng(7).integers(0,256,(160,160,3),dtype=np.uint8)
  def invalid(src,dst,**kwargs):return np.full((2,3),np.nan),np.ones((len(src),1),dtype=np.uint8)
  with patch.object(m.cv2,'estimateAffinePartial2D',side_effect=invalid):matrix,metric=m.register(image,image)
  self.assertIsNone(matrix);self.assertFalse(metric['accepted']);json.dumps(metric,allow_nan=False)
if __name__=='__main__':unittest.main()
