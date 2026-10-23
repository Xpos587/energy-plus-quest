import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
SOURCE=P.parent/'fleet-v16-cab-repair-2026-10-08/fleet-v16-cab-repair.blend'
receipt=json.loads((P/'wheel-build-receipt.json').read_text());hidden=set(receipt['hidden_original_wheel_objects'])
def actions():
 out={}
 for a in bpy.data.actions:
  out[a.name]=[(fc.data_path,fc.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for layer in a.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
 return out
def objects():
 return {o.name:([list(row) for row in o.matrix_local],o.parent.name if o.parent else None,o.hide_render,[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None,len(o.data.vertices) if o.type=='MESH' else None) for o in bpy.data.objects}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.scene.frame_set(144);bpy.context.view_layer.update();old=objects();oldactions=actions()
bpy.ops.wm.open_mainfile(filepath=str(P/'wheels-base.blend'));s=bpy.context.scene;s.frame_set(144);bpy.context.view_layer.update();new=objects();newactions=actions();errors=[]
for name,value in old.items():
 expected=list(value)
 if name in hidden:expected[2]=True
 if tuple(expected)!=new.get(name):errors.append(name)
assert not errors,errors
for name,value in oldactions.items():assert value==newactions[name],name
expected_materials={'V14 clean blue charcoal rubber','V14 soft warm alloy','V14 satin charcoal trim'}
for w in receipt['wheels']:
 mats=bpy.data.objects[w['tyre']].data.materials
 assert len(mats)==3 and all(m is not None for m in mats),w['tag']
 assert {m.name for m in mats}==expected_materials,w['tag']
guard_gap={}
for name in receipt['shortened_side_guards']:
 ob=bpy.data.objects[name];root=bpy.data.objects[f'truck-{name.split()[0]}-trailer'];tr=root.matrix_world.inverted()@ob.matrix_world
 gap=min((tr@v.co).x for v in ob.data.vertices)-(-4.48+.358)
 assert gap>.115,(name,gap)
 guard_gap[name]=gap
data=[];old_previous={};traveled={w['tag']:0 for w in receipt['wheels']};max_roll_error=0;ground_min=1e9;ground_max=-1e9;clearance={i:1e9 for i in range(1,5)};max_angles={i:(0,0) for i in range(1,5)}
for f in range(1,193):
 s.frame_set(f);bpy.context.view_layer.update()
 for w in receipt['wheels']:
  i,part,axle,side=w['tag'].split();i=int(i);axle=int(axle);side=int(side);steer=bpy.data.objects[w['steering']];spin=bpy.data.objects[w['rotation']];root=bpy.data.objects[f'truck-{i}-{part}'];m=spin.matrix_world;center=steer.matrix_world.translation.copy();scale=root.matrix_world.to_scale().x;r=w['radius_local']
  angle=steer.rotation_euler.z
  if part=='trailer' or axle>0:assert abs(angle)<1e-9
  elif abs(angle)>max_angles[i][0]:max_angles[i]=(abs(angle),f)
  if w['tag'] in old_previous:
   move=center-old_previous[w['tag']];heading=steer.matrix_world.to_3x3()@Vector((1,0,0));traveled[w['tag']]+=move.length*(1 if move.dot(heading)>=0 else -1)
  old_previous[w['tag']]=center
  max_roll_error=max(max_roll_error,abs(spin.rotation_euler.y-traveled[w['tag']]/(r*scale)))
  # Exact circular tangent and the 64-segment crown's actually rotated contact vertices.
  assert abs(center.z-r*scale)<1e-5,(w['tag'],f,center.z-r*scale)
  crown=[m@Vector((r*math.cos(k*math.tau/64),y,r*math.sin(k*math.tau/64))) for k in range(64) for y in (-.077,.077)]
  bottom=min(p.z for p in crown);ground_min=min(ground_min,bottom);ground_max=max(ground_max,bottom)
  if part=='tractor' and axle==0:
   if i in (1,4):
    g=bpy.data.objects[f'WORN {i} isolated cab suspension'];inv=Matrix.Translation(Vector((.8,0,.9)))@g.matrix_world.inverted();opening=.469
   else:inv=root.matrix_world.inverted();opening=.392
   # Full steering/roll profile, evaluated in the moving opening's coordinates.
   for k in range(64):
    a=k*math.tau/64
    for y,rad in ((-.1275,.282),(-.108,.345),(-.077,r),(.077,r),(.108,.345),(.1275,.282)):
     p=inv@m@Vector((rad*math.cos(a),y,rad*math.sin(a)))
     if .74<abs(p.y)<1.00 and p.z>.355:
      clearance[i]=min(clearance[i],opening-math.hypot(p.x-.8,p.z-.355))
assert max_roll_error<.0002,max_roll_error
assert ground_min>-.00001 and ground_max<.0006,(ground_min,ground_max)
assert min(clearance.values())>0,clearance
report={'source_objects_compared':len(old),'source_object_transforms_parents_mesh_vertex_counts_material_slots_unchanged':True,'only_original_visibility_changes':len(hidden),'all_source_animation_keys_handles_interpolation_unchanged':True,'wheel_count':len(receipt['wheels']),'consolidated_wheel_meshes':len([o for o in bpy.data.objects if o.name.startswith('WHEEL tyre ')]),'frames_checked':192,'front_steering_maximum':{i:{'degrees':math.degrees(v[0]),'frame':v[1]} for i,v in max_angles.items()},'maximum_distance_radius_roll_residual_radians':max_roll_error,'analytic_tyre_road_tangency':'Z=0 for all wheels at all frames','actual_polygon_crown_lowest_world_z_range':[ground_min,ground_max],'conservative_steered_tyre_clearance_in_cab_opening_local':clearance,'trailer_axles_steering_zero':True,'contact_layer':'48 tight alpha .28 radial contact patches; excluded from broad SUN shadow by render lane','boundary':'tyre profile vs conservative opening envelope, not full collision simulation; visual close/map gate required'}
report['persistent_saved_wheel_materials']=sorted(expected_materials)
report['shortened_guard_first_tyre_local_clearance']=guard_gap
(P/'wheel-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
