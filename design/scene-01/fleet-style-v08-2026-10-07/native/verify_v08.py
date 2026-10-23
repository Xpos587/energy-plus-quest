import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent
src=O.parents[1]/'whole-map-v06-2026-10-06/fleet/fleet-textured-v07.blend'
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;roots=sorted((o for o in s.objects if o.name.startswith('truck-')),key=lambda o:o.name);samples=[]
 for f in range(1,1153):
  s.frame_set(f);samples.append([float(x) for o in roots for r in o.matrix_world for x in r])
 return {'poses':samples,'camera':{'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'ortho':s.camera.data.ortho_scale},'actions':{o.name:o.animation_data.action.name if o.animation_data and o.animation_data.action else None for o in roots},'range':[s.frame_start,s.frame_end],'cab_vertices':{i:[list(v.co) for v in bpy.data.objects[f'V02 DETAILED {i} complete tractor'].data.vertices] for i in range(1,5)}}
a=capture(src);b=capture(O/'fleet-illustrated-v08.blend');delta=max(abs(x-y) for p,q in zip(a['poses'],b['poses']) for x,y in zip(p,q));contact={};rear={}
for i in range(1,5):
 contact[i]=max(abs(p[j]-q[j]) for p,q in zip(a['cab_vertices'][i],b['cab_vertices'][i]) if p[2]<-.15 for j in range(3));rear[i]=max(abs(p[j]-q[j]) for p,q in zip(a['cab_vertices'][i],b['cab_vertices'][i]) if p[0]>=0 for j in range(3))
r={'frames_verified':1152,'roots':len(b['actions']),'max_root_matrix_delta':delta,'camera_equal':a['camera']==b['camera'],'actions_equal':a['actions']==b['actions'],'range_equal':a['range']==b['range'],'cab_contact_tyre_region_max_vertex_delta':contact,'cab_rear_hitch_region_max_vertex_delta':rear,'source':str(src),'candidate':str(O/'fleet-illustrated-v08.blend')};assert delta==0 and r['camera_equal'] and r['actions_equal'] and r['range_equal'] and max(contact.values())==0 and max(rear.values())==0;(O/'v08-final-verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
