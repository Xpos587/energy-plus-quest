"""Check final encoded pose to first, excluding the unencoded boundary key."""
import json
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent;m=np.load(p/'motion.npy');rendered=m[:-1]
position_steps=np.diff(rendered[:,:,:3],axis=0)
angle_steps=np.angle(np.exp(1j*np.diff(rendered[:,:,3],axis=0)))
seam_position=rendered[0,:,:3]-rendered[-1,:,:3]
seam_angles=np.angle(np.exp(1j*(rendered[0,:,3]-rendered[-1,:,3])))
max_steps=np.linalg.norm(position_steps,axis=2).max(axis=0)
seam_steps=np.linalg.norm(seam_position,axis=1)
assert (seam_steps<=max_steps*1.001).all()
assert (np.abs(seam_angles)<=np.abs(angle_steps).max(axis=0)*1.001+1e-9).all()
rows=[]
for k in range(8):
 rows.append({'object':f'truck-{k//2+1}-'+('tractor' if k%2==0 else 'trailer'),'seam_displacement':seam_position[k].tolist(),'seam_step_distance':float(seam_steps[k]),'maximum_nonseam_step_distance':float(max_steps[k]),'seam_speed_scene_units_per_second':float(seam_steps[k]*24),'previous_speed':float(np.linalg.norm(position_steps[-1,k])*24),'next_speed':float(np.linalg.norm(position_steps[0,k])*24),'seam_angular_step_degrees':float(np.rad2deg(seam_angles[k])),'angular_step_before_degrees':float(np.rad2deg(angle_steps[-1,k])),'angular_step_after_degrees':float(np.rad2deg(angle_steps[0,k])),'velocity_vector_change_into_seam':float(np.linalg.norm(seam_position[k]-position_steps[-1,k])*24),'velocity_vector_change_out_of_seam':float(np.linalg.norm(position_steps[0,k]-seam_position[k])*24)})
screen=np.array(json.loads((p/'tracking.json').read_text())['normalized_screen_origins'])
screen_seam=np.linalg.norm(screen[0]-screen[-2],axis=1)
screen_max=np.linalg.norm(np.diff(screen[:-1],axis=0),axis=2).max(axis=0)
assert (screen_seam<=screen_max*1.002).all()
r={'passed':True,'fps':24,'rendered_pose_count':len(rendered),'comparison':'Encoded last frame1152 to encoded first frame1. Native frame1153 is not encoded. All seam displacement and yaw steps are within regular-cycle maxima.','maximum_seam_velocity_vector_change':max(max(x['velocity_vector_change_into_seam'],x['velocity_vector_change_out_of_seam']) for x in rows),'objects':rows,'screen_seam_step_norm':screen_seam.tolist(),'maximum_regular_screen_step_norm':screen_max.tolist()}
(p/'loop-seam-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
