import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
H=-1.45
roots=[bpy.data.objects[f'truck-{i}-{part}'] for i in range(1,5) for part in ['tractor','trailer']]
hide={o.name:o.hide_render for o in s.objects};camera={'name':s.camera.name,'location':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'ortho_scale':s.camera.data.ortho_scale}
rows=[];original={};bounds={};angles={i:[] for i in range(1,5)}
for i in range(1,5):
 r=bpy.data.objects[f'truck-{i}-tractor'];o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];m=r.matrix_world.inverted()@o.matrix_world
 pts=[m@v.co for v in o.data.vertices];cab=[p for p in pts if p.z>=1.01];bounds[i]={'cab_rear_x':min(p.x for p in cab),'cab_halfwidth':max(abs(p.y) for p in cab)}
for f in range(1,1153):
 s.frame_set(f)
 for i in range(1,5):
  r=bpy.data.objects[f'truck-{i}-tractor'];t=bpy.data.objects[f'truck-{i}-trailer'];a=math.atan2(math.sin(t.rotation_euler.z-r.rotation_euler.z),math.cos(t.rotation_euler.z-r.rotation_euler.z));angles[i].append((abs(a),f,a))
  original[f,i]={'tractor':list(r.location),'tractor_rotation':list(r.rotation_euler),'trailer_rotation':list(t.rotation_euler),'newlocation':list(r.matrix_world@Vector((H,0,0))),'oldpin_local':list(r.matrix_world.inverted()@t.matrix_world.translation)}
for i in range(1,5):
 t=bpy.data.objects[f'truck-{i}-trailer']
 for f in range(1,1153):
  t.location=original[f,i]['newlocation'];t.keyframe_insert(data_path='location',frame=f)
# Original visible decorative exhaust is attached beside the actual imported cab rear.
for i in [1,4]:
 r=bpy.data.objects[f'truck-{i}-tractor']
 for o in r.children_recursive:
  if not o.hide_render and 'exhaust' in o.name:
   # Mesh coordinate displacement preserves animated local translations of smoke.
   delta=o.matrix_world.to_3x3().inverted()@(r.matrix_world.to_3x3()@Vector((.90,0,0)))
   if o.data.users>1:o.data=o.data.copy()
   for v in o.data.vertices:v.co+=delta
# validate unchanged source orientation/trajectory and pin alignment on every frame
errors=[]
for f in range(1,1153):
 s.frame_set(f)
 for i in range(1,5):
  r=bpy.data.objects[f'truck-{i}-tractor'];t=bpy.data.objects[f'truck-{i}-trailer'];ori=original[f,i];a=math.atan2(math.sin(t.rotation_euler.z-r.rotation_euler.z),math.cos(t.rotation_euler.z-r.rotation_euler.z))
  pin=(r.matrix_world@Vector((H,0,0))-t.matrix_world.translation).length
  assert pin<1e-5,(f,i,pin)
  assert (Vector(r.location)-Vector(ori['tractor'])).length<1e-5
  assert (Vector(t.rotation_euler)-Vector(ori['trailer_rotation'])).length<1e-5
  # Separating plane between entire visible cab body and frontmost trailer body corner.
  front=H+.7*math.cos(a)+1.029*abs(math.sin(a));clear=bounds[i]['cab_rear_x']-front
  assert clear>0,(i,f,clear)
  rows.append({'frame':f,'truck':i,'pin_error_world':pin,'articulation_deg':math.degrees(a),'cab_separating_clearance_local':clear})
for o in s.objects:assert o.hide_render==hide[o.name]
s.frame_set(1);s.render.use_compositing=False;s.render.film_transparent=True
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v11-coupling.blend'))
receipt={'source':'../fleet-lookdev-v10-2026-10-07/fleet-v10-age.blend','hitch_local_before':[-2.3,0,0],'hitch_local_after':[H,0,0],'trailer_kingpin_local':[0,0,0],'straight_gap_before':bounds[1]['cab_rear_x']-(-2.3+.7),'straight_gap_after':bounds[1]['cab_rear_x']-(H+.7),'camera':camera,'validation':{'frames':1152,'truck_frames':len(rows),'max_pin_error_world':max(r['pin_error_world'] for r in rows),'min_cab_separating_clearance_local':min(r['cab_separating_clearance_local'] for r in rows),'max_turns':{i:{'frame':max(a)[1],'angle_deg':math.degrees(max(a)[0])} for i,a in angles.items()}},'preservation':'all source hide_render flags, tractor root locations/rotations, trailer headings, camera, materials, source geometry except exhaust translation; source crew faces/materials untouched','exhaust_relocation':'visible stack and smoke on trucks 1 and 4 moved +0.90 tractor local X beside actual imported cab rear; required to avoid new trailer collision','bounds':bounds}
(P/'coupling-receipt.json').write_text(json.dumps(receipt,indent=2));(P/'all-frames-validation.json').write_text(json.dumps(rows))
print(json.dumps(receipt),flush=True)
# isolated QA comes AFTER master save; master retains original camera/scene flags.
for o in s.objects:
 if o.type not in ('CAMERA','LIGHT') and not any(o==r or o in r.children_recursive for r in roots):o.hide_render=True
for f in [1,385,769]:
 s.frame_set(f);s.render.filepath=str(P/f'vehicles-{f:04}.png');bpy.ops.render.render(write_still=True)
c=s.camera;c.animation_data_clear();c.data.type='ORTHO';s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100
for i in range(1,5):
 s.frame_set(1);r=bpy.data.objects[f'truck-{i}-tractor'];t=bpy.data.objects[f'truck-{i}-trailer'];keep={r,t,*r.children_recursive,*t.children_recursive}
 for o in s.objects:
  if o.type not in ('CAMERA','LIGHT'):o.hide_render=hide[o.name] or o not in keep
 for label,local,scale,targetlocal in [('front',(9,-12,7),9,(-1.4,0,1.2)),('side',(-2,-17,3.0),13,(-3,0,1.2))]:
  c.data.ortho_scale=scale;target=r.matrix_world@Vector(targetlocal);c.location=r.matrix_world@Vector(local);c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/f'{label}-{i}.png');bpy.ops.render.render(write_still=True)
 f=max(angles[i])[1];s.frame_set(f);c.data.ortho_scale=12;target=r.matrix_world@Vector((-2,0,1.2));c.location=r.matrix_world@Vector((5,-11,10));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/f'maxturn-{i}-{f:04}.png');bpy.ops.render.render(write_still=True)
