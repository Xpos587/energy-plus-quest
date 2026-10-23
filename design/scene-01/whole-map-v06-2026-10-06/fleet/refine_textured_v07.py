"""Cab proportion refinement only; preserves rear hitch zone and all rig poses."""
import bpy,json,time
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;s=bpy.context.scene;records=[]
def bounds(vs):return [[min(v[a] for v in vs),max(v[a] for v in vs)] for a in range(3)]
for i in range(1,5):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];before=[v.co.copy() for v in o.data.vertices];cab=[v for v in before if v.x<-.30 and v.z>-.15];changed_wheels=0;rear_delta=0;contact_delta=0
 for v,old in zip(o.data.vertices,before):
  co=old.copy()
  if old.x<-.30:
   # Front wheel region translates rigidly with its axle: do not stretch circular tyres.
   frontwheel=(-.75<old.x<-.40 and abs(old.y)>.30 and old.z<-.18)
   if frontwheel:co.x+=(-.575+.30)*.25;changed_wheels+=1
   else:co.x=-.30+(old.x+.30)*1.25
   if old.z>-.15:co.z=-.15+(old.z+.15)*1.25;co.y*=1.06
  v.co=co
  if old.x>=0:rear_delta=max(rear_delta,(co-old).length)
  if old.z<-.50:contact_delta=max(contact_delta,abs(co.z-old.z))
 o.data.update();after=[v.co.copy() for v in o.data.vertices];cab_after=[after[j] for j,p in enumerate(before) if p.x<-.30 and p.z>-.15]
 assert rear_delta==0 and contact_delta==0
 records.append({'truck':i,'cab_bounds_before_model_space':bounds(cab),'cab_bounds_after_model_space':bounds(cab_after),'cab_factors':[1.25,1.06,1.25],'cab_pivot_x':-.30,'height_pivot_z':-.15,'rear_zone_x_ge_0_max_delta':rear_delta,'ground_contact_z_max_delta':contact_delta,'front_wheel_vertices_rigid_x_translation':changed_wheels,'front_axle_x_shift_model':(-.575+.30)*.25,'front_axle_x_shift_local_world':.15125})
# Blue reefer: remove curtain buckles (existing flat trailer remains smooth white).
# No actual reefer refrigeration unit exists in this frozen scene.
removed=[]
for o in bpy.data.objects['truck-2-trailer'].children:
 if 'curtain buckle' in o.name:o.hide_render=True;removed.append(o.name)
roots=[o for o in s.objects if o.name.startswith('truck-')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');crypto.matte_id=', '.join(o.name for o in fleet if o.type in ('MESH','FONT') and not o.hide_render)
s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
receipt={'parent':'fleet-textured-v06.blend','candidate':'fleet-textured-v07.blend','records':records,'blue_curtain_buckles_hidden':len(removed),'limitations':['Cab upper body length/height expanded25%; width6%; old lower roofs retained.','Front axle moves forward.15125 local units with rigid tyre-region translation; contact heights and rear hitch geometry remain exact.','No existing reefer unit asset in scene: blue only loses inappropriate curtain buckles; original trailer dimensions and actions unchanged.','Perceptual size remains a visual judgement; geometry factors are measured.']}
(O/'textured-v07-receipt.json').write_text(json.dumps(receipt,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'fleet-textured-v07.blend'))
normal_times={}
for f in (1,385,769):
 s.frame_set(f);s.render.filepath=str(O/f'textured-v07-vehicles-{f:04}.png');t=time.perf_counter();bpy.ops.render.render(write_still=True);normal_times[str(f)]=time.perf_counter()-t
# Separate fast scene candidate, not a mutation of normal city source.
for o in s.objects:
 if o.type in ('MESH','FONT','CURVE') and o not in fleet:o.hide_render=True
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'fleet-textured-v07-fast.blend'))
fast_times={}
for f in (1,385):
 s.frame_set(f);s.render.filepath=str(O/f'textured-v07-fast-{f:04}.png');t=time.perf_counter();bpy.ops.render.render(write_still=True);fast_times[str(f)]=time.perf_counter()-t
(O/'textured-v07-timing.json').write_text(json.dumps({'normal_seconds':normal_times,'fast_seconds':fast_times,'resolution':[1920,1334],'fast_scene':'city meshes hidden; lights and camera preserved; existing Cryptomatte output unchanged','note':'Same Blender process sequential measured wall time, no full-loop estimate'},indent=2))
# Native desktop-angle close pilot, isolated from city only for QA.
s.frame_set(769);root=bpy.data.objects['truck-3-tractor'];cam=s.camera;center=root.matrix_world@Vector((0,0,1.7));view=cam.matrix_world.to_quaternion()@Vector((0,0,1));cam.location=center+view*35;cam.data.ortho_scale=6;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.filepath=str(O/'textured-v07-green-desktop-close.png');bpy.ops.render.render(write_still=True)
print('V07 PILOT + FAST TIMING COMPLETE')
