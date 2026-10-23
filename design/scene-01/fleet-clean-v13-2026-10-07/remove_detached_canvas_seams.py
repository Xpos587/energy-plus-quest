import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v13-clean.blend'));removed=[]
for o in list(bpy.data.objects):
 if any(o.name.startswith(f'V08 {i} softly folded canvas seam') or o.name.startswith(f'V08 {i} subdued canvas wear') for i in (1,4)):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v13-clean.blend'))
r=json.loads((P/'change-receipt.json').read_text());r['removed_detached_canvas_overlays']=removed;(P/'change-receipt.json').write_text(json.dumps(r,indent=2))
