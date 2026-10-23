import importlib.util,tempfile,unittest,json
from pathlib import Path
from PIL import Image
spec=importlib.util.spec_from_file_location('flowers_promote',Path(__file__).with_name('promote.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PromoteTests(unittest.TestCase):
 def fixture(self,p,decision='accepted_for_runtime',retained=False):
  (p/'public').mkdir();(p/'job').mkdir();(p/'docs/reviews').mkdir(parents=True);Image.new('RGB',(90,6),'blue').save(p/'public/source.png');Image.new('RGB',(8192,546),'red').save(p/'job/pass2-master.png')
  def tile(id):return {'id':id,'status':'accepted','attempts':[{'candidate':id+'.png','attempt':1,'affineGeneratedToReference':[[1,0,0],[0,1,0]]}]}
  p1=[tile('p1-'+str(n))for n in range(9)];p2=[tile('p2-'+str(n))for n in range(4)]
  if retained:p2[0].update(status='retained',retention={'reason':'actual rejected fixture','ownerReceipt':'fixture'})
  job={'sourceDimensions':[90,6],'status':'master_ready_for_visual_review','tiles':p1,'rois':p2,'protection':{'status':'owner_approved'}}
  def receipt(tiles):return {'acceptedNativeTiles':sum(t['status']=='accepted'for t in tiles),'retainedPriorTiles':[t['id']for t in tiles if t['status']=='retained'],'inheritedPass1Retentions':[],'protection':job['protection'],'tiles':[{'id':t['id'],'accepted':t['status']=='accepted','registration':t['attempts'][-1],'retention':t.get('retention')}for t in tiles]}
  (p/'job/job.json').write_text(json.dumps(job));(p/'job/pass1-assembly.json').write_text(json.dumps(receipt(p1)));(p/'job/pass2-assembly.json').write_text(json.dumps(receipt(p2)));review={'decision':decision,'passes':2};(p/'docs/reviews/review.json').write_text(json.dumps(review));return{'id':'FTEST','source':'public/source.png','outputRoot':'job','freezeStatus':'owner_frozen'}
 def test_appended_roi_blocks_stale_master_promotion(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);asset=self.fixture(p);j=json.loads((p/'job/job.json').read_text());j['rois'].append({'id':'p2-repair','status':'accepted','attempts':[{'candidate':'repair.png','attempt':1}]});(p/'job/job.json').write_text(json.dumps(j))
   with self.assertRaisesRegex(ValueError,'stale'):m.promote(p,asset,'docs/reviews/review.json')
 def test_three_roi_master_requires_explicit_protocol_exception(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);asset=self.fixture(p);j=json.loads((p/'job/job.json').read_text());j['rois']=j['rois'][:3];(p/'job/job.json').write_text(json.dumps(j));r=json.loads((p/'job/pass2-assembly.json').read_text());r['tiles']=r['tiles'][:3];r['acceptedNativeTiles']=3;(p/'job/pass2-assembly.json').write_text(json.dumps(r))
   with self.assertRaisesRegex(ValueError,'4'):m.promote(p,asset,'docs/reviews/review.json')

 def test_unreviewed_or_semantically_held_master_never_activates(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);asset=self.fixture(p,decision='pending')
   with self.assertRaises(ValueError):m.promote(p,asset,'docs/reviews/review.json')
   self.assertFalse((p/'src/media/flowers-masters.json').exists())
 def test_promotion_is_reversible_alias_original_untouched(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);asset=self.fixture(p);r=m.promote(p,asset,'docs/reviews/review.json');self.assertEqual(Image.open(p/'public/source.png').size,(90,6));self.assertEqual(r['passes'],2);self.assertTrue((p/r['master']).exists());self.assertEqual(json.loads((p/'src/media/flowers-masters.json').read_text())['public/source.png']['master'],r['master'])
 def test_retained_regions_require_explicit_review_acceptance(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);asset=self.fixture(p,retained=True)
   with self.assertRaisesRegex(ValueError,'retained'):m.promote(p,asset,'docs/reviews/review.json')
if __name__=='__main__':unittest.main()
