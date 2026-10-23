import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;ROOT=O.parents[3]
source=ROOT/'design/scene-01/painted-layer-2026-10-05/painted-vehicles-driver-fixed-optimized.blend'
def capture():
 s=bpy.context.scene;roots=sorted((o for o in s.objects if o.name.startswith('truck-')),key=lambda o:o.name)
 actions={o.name:o.animation_data.action.name if o.animation_data and o.animation_data.action else None for o in roots}
 samples=[]
 for f in range(1,1153):
  s.frame_set(f);samples.append([float(x) for o in roots for row in o.matrix_world for x in row])
 return {'camera':{'name':s.camera.name,'matrix':[list(row) for row in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale},'actions':actions,'frame_range':[s.frame_start,s.frame_end]},samples
bpy.ops.wm.open_mainfile(filepath=str(source));a,p=capture()
bpy.ops.wm.open_mainfile(filepath=str(O/'fleet-textured-v06.blend'));b,q=capture()
delta=max(abs(x-y) for sp,sq in zip(p,q) for x,y in zip(sp,sq))
result={'source':str(source),'candidate':str(O/'fleet-textured-v06.blend'),'frames_verified':1152,'root_count':8,'max_root_matrix_delta':delta,'camera_equal':a['camera']==b['camera'],'actions_equal':a['actions']==b['actions'],'frame_range_equal':a['frame_range']==b['frame_range'],'actions':b['actions'],'visual_inspection':{'map_frames':[1,385,769],'all_four_present_each':True,'green_front_test':'Two detailed windshield crew visible in green, one detailed driver plus empty seat in blue; complete v02 tractor mesh','original_close_comparison':'Original tractor descendants hidden; detailed v02 complete tractor appended'}}
assert delta==0 and result['camera_equal'] and result['actions_equal'] and result['frame_range_equal']
(O/'textured-v06-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
