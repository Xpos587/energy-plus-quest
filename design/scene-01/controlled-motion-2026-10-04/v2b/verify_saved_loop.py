import bpy,json
from pathlib import Path
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
p=Path(__file__).resolve().parent;s=bpy.context.scene
roots=[s.objects[f'truck-{i}-{part}'] for i in range(1,5) for part in ('tractor','trailer')]
expected=np.load(p/'motion.npy');tracks=np.array(json.loads((p/'tracking.json').read_text())['normalized_screen_origins'])
records=[];pose_error=screen_error=0.
for frame in (1,2,1151,1152,1153):
 s.frame_set(frame);bpy.context.view_layer.update();poses=np.array([[*o.location,o.rotation_euler.z] for o in roots]);points=[]
 for o in roots:
  q=world_to_camera_view(s,s.camera,o.matrix_world.translation);points.append([q.x,1-q.y])
 pose_error=max(pose_error,float(np.abs(poses-expected[frame-1]).max()));screen_error=max(screen_error,float(np.abs(np.array(points)-tracks[frame-1]).max()))
 records.append({'frame':frame,'poses':poses.tolist(),'screen_origins':points})
a=np.array(records[0]['poses']);b=np.array(records[-1]['poses'])
pos_error=float(np.abs(a[:,:3]-b[:,:3]).max());angle_error=float(np.abs(np.angle(np.exp(1j*(a[:,3]-b[:,3])))).max())
r={'source':bpy.data.filepath,'passed':pose_error<.00002 and screen_error<1e-7 and pos_error==0 and angle_error<.00002,'saved_boundary_position_error':pos_error,'saved_boundary_angle_error_radians':angle_error,'saved_poses_vs_exported_max_error':pose_error,'saved_projection_vs_tracking_max_error':screen_error,'records':records}
(p/'saved-loop-boundary.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k!='records'});assert r['passed']
