import copy,unittest
from freshness import assembly_is_current
class FreshnessTests(unittest.TestCase):
 def fixture(self):
  attempt={'candidate':'one.png','attempt':1,'affineGeneratedToReference':[[1,0,0],[0,1,0]]};tile={'id':'p2-one','status':'accepted','attempts':[attempt]};job={'rois':[tile],'protection':{'revision':1},'roiRevision':1};receipt={'tiles':[{'id':tile['id'],'accepted':True,'registration':copy.deepcopy(attempt)}],'protection':copy.deepcopy(job['protection']),'roiRevision':1};return job,receipt
 def test_matching_input_is_current(self):
  j,r=self.fixture();self.assertTrue(assembly_is_current(j,r,2))
 def test_appended_resolved_roi_makes_old_master_stale(self):
  j,r=self.fixture();t=copy.deepcopy(j['rois'][0]);t['id']='p2-repair';j['rois'].append(t);self.assertFalse(assembly_is_current(j,r,2))
 def test_new_native_attempt_makes_old_master_stale(self):
  j,r=self.fixture();j['rois'][0]['attempts'].append({'candidate':'two.png','attempt':2});self.assertFalse(assembly_is_current(j,r,2))
 def test_protection_and_roi_revisions_invalidate_old_master(self):
  for field in ['protection','roiRevision']:
   j,r=self.fixture();j[field]={'revision':2} if field=='protection' else 2;self.assertFalse(assembly_is_current(j,r,2))
if __name__=='__main__':unittest.main()
