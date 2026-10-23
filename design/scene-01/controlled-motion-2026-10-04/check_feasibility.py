"""Read-only certification that phase-only straight start is unavailable."""
import bpy,json,math
import numpy as np
from pathlib import Path
p=Path('/home/michael/Github/energy-plus-quest/design/scene-01/controlled-motion-2026-10-04')
s=bpy.context.scene
a=np.load(p/'source-motion.npy')
report={'source':bpy.data.filepath,'duration_seconds':s.frame_end/s.render.fps,'fps':s.render.fps,'frames':s.frame_end,'required_start_articulation_degrees':3,'allowed_operation':'Independent cyclic phase shifts of existing native animation only','trucks':[],'camera_preserved':True,'geometry_modified':False,'render_started':False}
for i in range(4):
 info=[]
 for part in ('tractor','trailer'):
  o=s.objects[f'truck-{i+1}-{part}'];ad=o.animation_data;curves=[]
  for layer in ad.action.layers:
   for strip in layer.strips:
    bag=strip.channelbag(ad.action_slot)
    if bag:curves.extend(bag.fcurves)
  yaw=next(c for c in curves if c.data_path=='rotation_euler' and c.array_index==2)
  info.append({'part':part,'yaw_key_count':len(yaw.keyframe_points),'interpolations':sorted(set(k.interpolation for k in yaw.keyframe_points)),'first_key_frame':yaw.keyframe_points[0].co.x,'last_key_frame':yaw.keyframe_points[-1].co.x,'modifiers':[m.type for m in yaw.modifiers]})
 delta=(a[:,i*2,3]-a[:,i*2+1,3]+np.pi)%(2*np.pi)-np.pi
 # All signed wrapped values stay positive and well below pi. Linear yaw curves
 # with matching integer keys therefore cannot attain a lower subframe angle.
 assert all(x['interpolations']==['LINEAR'] and x['yaw_key_count']==1153 and not x['modifiers'] for x in info)
 assert (delta>0).all() and (delta<np.pi/2).all()
 angles=np.rad2deg(delta)
 report['trucks'].append({'truck':i+1,'minimum_articulation_degrees':float(angles.min()),'minimum_source_frame':int(angles.argmin()+1),'eligible_integer_frames':int((angles[:-1]<3).sum()),'initial_articulation_degrees':float(angles[0]),'yaw_curves':info})
report['continuous_interval_proof']='Both yaw channels have matching frame1..1153 linear keys, no modifiers. Signed cab-minus-trailer yaw stays positive and below90deg. Its linear interpolation has its minimum at an endpoint; subframes cannot improve these minima.'
report['feasible']=all(t['minimum_articulation_degrees']<3 for t in report['trucks'])
report['limitation']='A straight initial pose requires changing the articulation trajectory or routes, beyond allowed phase-only edits. No candidate or preview presented as satisfying this constraint.'
(p/'phase-feasibility.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
