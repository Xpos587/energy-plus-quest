import bpy,json,pathlib,math
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'crew.blend'))
objs=[o for o in bpy.data.objects if o.name.startswith('CREW_')]
heads=[o for o in objs if o.name.endswith('sculpted_head')]
assert len(heads)==2
assert len([o for o in objs if o.name=='CREW_steering_wheel_rim'])==1
checks={}
for o in heads:
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 margin=min(p.x-(.187338*p.z-.913884) for p in pts)
 assert margin>0
 checks[o.name]={'front_glass_clearance_min':margin,'head_mesh_bbox_center':[(min(p[k] for p in pts)+max(p[k] for p in pts))/2 for k in range(3)]}
for r in ['driver','passenger']:
 for part in ['hips','seated_thigh_-1','seated_thigh_1','calf_-1','calf_1','seat_base','seat_back']:
  assert 'CREW_'+r+'_'+part in bpy.data.objects
C=Vector((-.79,-.20,-.035));n=Vector((-1,0,.32)).normalized()
for s in [-1,1]:
 hand=bpy.data.objects['CREW_driver_hand_'+str(s)].location
 d=hand-C;plane=abs(d.dot(n));rad=(d-n*d.dot(n)).length
 dist=math.sqrt(plane**2+(rad-.077)**2)
 assert dist<.020
 checks['hand_'+str(s)]={'center_to_rim_distance':dist,'hand_ellipsoid_radii':[.018,.017,.022]}
assert all(o.name.startswith('CREW_') for o in bpy.data.collections['CREW'].objects)
(P/'validation.json').write_text(json.dumps({'passed':True,'crew_objects':len(objs),'two_heads':len(heads),'one_wheel':True,'seated_body_parts':True,'checks':checks},indent=2))
print('CREW VALIDATION PASSED',len(objs))
