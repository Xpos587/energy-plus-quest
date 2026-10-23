import importlib.util,tempfile,unittest,json
from pathlib import Path
from PIL import Image
spec=importlib.util.spec_from_file_location('flowers_pipeline',Path(__file__).with_name('pipeline.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PipelineTests(unittest.TestCase):
 def test_resume_does_not_reset_accepted_tiles_or_frozen_source(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);s=p/'input.png';Image.new('RGB',(90,60),'blue').save(s)
   job=m.prepare_job(p/'job',s,'F0001','owner-receipt')
   self.assertEqual(len(job['tiles']),9);job['tiles'][0]['status']='accepted';m.save_job(p/'job',job)
   Image.new('RGB',(90,60),'red').save(s);resumed=m.prepare_job(p/'job',s,'F0001','owner-receipt')
   self.assertEqual(resumed['tiles'][0]['status'],'accepted');self.assertEqual(Image.open(p/'job/source.png').getpixel((0,0)),(0,0,255))
 def test_partial_tiles_cannot_be_promoted_to_master(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);s=p/'input.png';Image.new('RGB',(90,60),'blue').save(s);m.prepare_job(p/'job',s,'F0001','owner-receipt')
   with self.assertRaisesRegex(ValueError,'accepted'):m.assemble(p/'job',1)
 def test_featureless_candidate_is_rejected_and_receipt_kept(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);s=p/'input.png';Image.new('RGB',(90,60),'blue').save(s);m.prepare_job(p/'job',s,'F0001','owner-receipt')
   receipt=m.record(p/'job','p1-00',s)
   self.assertFalse(receipt['accepted']);j=m.load_job(p/'job');self.assertEqual(j['tiles'][0]['status'],'rejected');self.assertEqual(len(j['tiles'][0]['attempts']),1)
 def test_alpha_is_frozen_without_flattening(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);s=p/'input.png';Image.new('RGBA',(90,60),(10,20,30,0)).save(s);m.prepare_job(p/'job',s,'F0001','receipt')
   self.assertEqual(Image.open(p/'job/source.png').mode,'RGBA');self.assertEqual(Image.open(p/'job/source-alpha.png').getpixel((0,0)),0)
 def test_retention_requires_rejected_attempt_and_discloses_reason(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);s=p/'input.png';Image.new('RGB',(90,60),'blue').save(s);m.prepare_job(p/'job',s,'F0001','receipt')
   with self.assertRaises(ValueError):m.retain(p/'job','p1-00','not registered','owner')
   m.record(p/'job','p1-00',s);m.retain(p/'job','p1-00','featureless protected area','owner')
   tile=m.load_job(p/'job')['tiles'][0];self.assertEqual(tile['status'],'retained');self.assertEqual(tile['retention']['reason'],'featureless protected area')
 def test_saved_master_preserves_alpha_and_retained_core_against_overlap(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);s=p/'input.png';Image.new('RGBA',(90,60),(0,0,255,80)).save(s);job=m.prepare_job(p/'job',s,'FTEST','receipt');job['exportLongestEdge']=90
   self.assertEqual(m.master_size(job),(90,60))
   Image.new('L',(90,60),0).save(p/'mask.png');m.set_protection(p/'job',p/'mask.png','owner-approved fixture');job['protection']=m.load_job(p/'job')['protection']
   for tile in job['tiles']:
    box=tile['box'];Image.new('RGB',(box[2]-box[0],box[3]-box[1]),'red').save(p/'job'/f"{tile['id']}-fixture.png");tile['status']='accepted';tile['attempts']=[{'candidate':f"{tile['id']}-fixture.png",'affineGeneratedToReference':[[1,0,0],[0,1,0]],'geometryGuard':{'accepted':True},'accepted':True}]
   job['tiles'][4]['status']='retained';job['tiles'][4]['retention']={'reason':'unit fixture rejected tile','ownerReceipt':'fixture'};m.save_job(p/'job',job)
   receipt=m.assemble(p/'job',1);im=Image.open(p/'job/pass1-master.png');self.assertEqual(im.mode,'RGBA');self.assertEqual(im.getpixel((45,30)),(0,0,255,80));self.assertFalse(receipt['fullNativeReconstruction']);self.assertEqual(receipt['retainedPriorTiles'],['p1-11'])
 def test_append_roi_preserves_accepted_work(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);s=p/'input.png';Image.new('RGB',(90,60),'blue').save(s);m.prepare_job(p/'job',s,'FTEST','receipt');Image.new('RGB',(90,60),'blue').save(p/'job/pass1-master.png');f=p/'rois.json';f.write_text(json.dumps([{'id':'p2-first','sourceBox':[10,10,20,20]}]));m.set_rois(p/'job',f);j=m.load_job(p/'job');j['rois'][0]['status']='accepted';j['rois'][0]['attempts']=[{'accepted':True,'fixture':True}];m.save_job(p/'job',j);f.write_text(json.dumps([{'id':'p2-repair','sourceBox':[20,20,30,30]}]));m.set_rois(p/'job',f,append=True);j=m.load_job(p/'job');self.assertEqual(len(j['rois']),2);self.assertEqual(j['rois'][0]['status'],'accepted');self.assertEqual(j['rois'][0]['attempts'],[{'accepted':True,'fixture':True}])
 def test_visual_rejection_overrides_numeric_acceptance_without_erasing_it(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);s=p/'input.png';Image.new('RGB',(90,60),'blue').save(s);m.prepare_job(p/'job',s,'FTEST','receipt');j=m.load_job(p/'job');j['tiles'][0]['status']='accepted';j['tiles'][0]['attempts']=[{'accepted':True,'fixture':'numeric acceptance'}];m.save_job(p/'job',j);m.visual_reject(p/'job','p1-00','visible double edge','owner-review');j=m.load_job(p/'job');self.assertEqual(j['tiles'][0]['status'],'rejected');self.assertTrue(j['tiles'][0]['attempts'][0]['accepted']);m.retain(p/'job','p1-00','preserve original edge after visual rejection','owner-review');self.assertEqual(m.load_job(p/'job')['tiles'][0]['status'],'retained')
 def test_roi_feathers_only_interior_boundaries_not_canvas_edges(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);s=p/'input.png';Image.new('RGB',(90,60),'blue').save(s);job=m.prepare_job(p/'job',s,'FTEST','receipt');job['exportLongestEdge']=90;m.save_job(p/'job',job)
   Image.new('L',(90,60),0).save(p/'mask.png');m.set_protection(p/'job',p/'mask.png','owner');Image.new('RGB',(90,60),'blue').save(p/'job/pass1-master.png')
   (p/'job/pass1-assembly.json').write_text(json.dumps({'retainedPriorTiles':[]}))
   f=p/'rois.json';f.write_text(json.dumps([{'id':'p2-edge','sourceBox':[0,0,45,30]}]));m.set_rois(p/'job',f);job=m.load_job(p/'job');tile=job['rois'][0];tile['status']='accepted';Image.new('RGB',(45,30),'red').save(p/'job/native.png');tile['attempts']=[{'candidate':'native.png','affineGeneratedToReference':[[1,0,0],[0,1,0]],'geometryGuard':{'accepted':True},'accepted':True}];m.save_job(p/'job',job);m.assemble(p/'job',2)
   with Image.open(p/'job/pass2-master.png')as im:
    edge=im.getpixel((0,0));self.assertGreaterEqual(edge[0],240);self.assertLessEqual(edge[2],10);self.assertEqual(im.getpixel((44,29)),(0,0,255));self.assertEqual(im.getpixel((60,40)),(0,0,255))
if __name__=='__main__':unittest.main()
