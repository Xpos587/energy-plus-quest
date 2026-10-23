import importlib.util,tempfile,unittest
from pathlib import Path
from PIL import Image
s=importlib.util.spec_from_file_location('reconcile',Path(__file__).with_name('reconcile.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ReconcileTests(unittest.TestCase):
 def test_equal_alpha_does_not_hide_changed_rgb(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);Image.new('RGBA',(4,4),(255,0,0,255)).save(p/'a.png');Image.new('RGBA',(4,4),(0,0,255,255)).save(p/'b.png');self.assertFalse(m.same_pixels(p/'a.png',p/'b.png'))
 def test_alpha_difference_is_not_treated_as_duplicate(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);Image.new('RGBA',(4,4),(255,0,0,255)).save(p/'a.png');Image.new('RGBA',(4,4),(255,0,0,0)).save(p/'b.png');self.assertFalse(m.same_pixels(p/'a.png',p/'b.png'));self.assertTrue(m.same_pixels(p/'a.png',p/'a.png'))
if __name__=='__main__':unittest.main()
