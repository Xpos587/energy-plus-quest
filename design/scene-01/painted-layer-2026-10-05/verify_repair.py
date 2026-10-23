import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent
frames=(1,133,169,769)
def snapshot():
 s=bpy.context.scene;r={};camera={'matrix':[list(x) for x in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale}
 for f in frames:
  s.frame_set(f);r[str(f)]={o.name:[list(o.location),list(o.rotation_euler)] for o in s.objects if o.name.startswith('truck-')}
 return r,camera
candidate,camera=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'controlled-motion-2026-10-04/v2b/controlled-straight-start.blend'))
source,sourcecamera=snapshot()
r={'native_root_pose_equality_all_requested_frames':candidate==source,'camera_equality':camera==sourcecamera,'frames':list(frames),'four_stills_present':all((p/'repaired-stills'/f'{f:04}.png').exists() for f in frames),'animation_rendered':False}
(p/'repaired-verification.json').write_text(json.dumps(r,indent=2));print(r)
assert candidate==source and camera==sourcecamera and r['four_stills_present']
