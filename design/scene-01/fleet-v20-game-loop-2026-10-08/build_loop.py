import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;N=2304;fps=24
source=P.parent/'fleet-behavior-v16-2026-10-07/fleet-v16.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
names=[f'truck-{i}-{p}' for i in range(1,5) for p in ('tractor','trailer')]
rates={1:.75,2:.5,3:1.,4:.5};poses={n:[] for n in names}
for f in range(N+1):
 for i,rate in rates.items():
  sf=1+(f*rate)%1152;s.frame_set(int(sf),subframe=sf%1)
  for part in ('tractor','trailer'):
   o=bpy.data.objects[f'truck-{i}-{part}'];poses[o.name].append((tuple(o.location),tuple(o.rotation_euler)))
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-v19-city-occlusion-2026-10-08/occlusion/city-occlusion.blend'));s=bpy.context.scene;s.frame_start=1;s.frame_end=N;s.render.fps=fps
for name in names:
 o=bpy.data.objects[name];o.animation_data_clear();last=None
 for f,(loc,rot) in enumerate(poses[name],1):
  rot=list(rot)
  if last is not None:rot[2]=last+math.atan2(math.sin(rot[2]-last),math.cos(rot[2]-last))
  last=rot[2];o.location=loc;o.rotation_euler=rot;o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f)
# Accepted cab amplitudes; harmonics use integer cycles to close at48s.
for i in (1,4):
 o=bpy.data.objects[f'WORN {i} isolated cab suspension'];o.animation_data_clear();phase=0 if i==1 else 1.15;cycles=211 if i==1 else 250
 for f in range(N+1):
  w=2*math.pi*cycles*f/N+phase;w2=2*math.pi*round(cycles*1.71)*f/N+1.71*phase;w3=2*math.pi*round(cycles*1.43)*f/N+1.43*phase
  z=.07*(.78*math.sin(w)+.22*math.sin(w2+.6));rx=math.radians(1.3)*(.8*math.sin(w+.45)+.2*math.sin(w3+1.1))*(1 if i==1 else -1);ry=math.radians(.25)*math.sin(w+.9)
  o.location=(.8,0,.9+z);o.rotation_euler=(rx,ry,0);o.keyframe_insert('location',frame=f+1);o.keyframe_insert('rotation_euler',frame=f+1)
roots={(i,p):bpy.data.objects[f'truck-{i}-{p}']for i in range(1,5)for p in ('tractor','trailer')};paths={k:[]for k in roots};stacks={i:[]for i in (1,4)}
for f in range(N+1):
 s.frame_set(f+1);bpy.context.view_layer.update()
 for k,o in roots.items():paths[k].append(o.matrix_world.copy())
 for i in stacks:
  o=bpy.data.objects[f'{i} exhaust stack'];vs=[o.matrix_world@Vector(v)for v in o.bound_box];stacks[i].append(Vector((sum(v.x for v in vs)/8,sum(v.y for v in vs)/8,max(v.z for v in vs)+.018)))
# Wheel local placements preserve compact v19 rear axles. Centered periodic curvature.
wheelrows=[]
for steer in [o for o in s.objects if o.name.startswith('WHEEL steering ')]:
 _,_,si,part,axle,side=steer.name.split();i=int(si);side=int(side);axle=int(axle);spin=bpy.data.objects[steer.name.replace('steering','rotation')];steer.animation_data_clear();spin.animation_data_clear();ms=paths[i,part];scale=ms[0].to_scale().x;R=.358;centers=[m@steer.location for m in ms];angles=[0.];deltas=[]
 for f in range(N+1):
  j=f%N;a=(j-1)%N;b=(j+1)%N;ma=paths[i,'tractor'][a];mb=paths[i,'tractor'][b];aa=math.atan2(ma[1][0],ma[0][0]);ab=math.atan2(mb[1][0],mb[0][0]);dyaw=math.atan2(math.sin(ab-aa),math.cos(ab-aa));ds=((mb@Vector((-1.775,0,R)))-(ma@Vector((-1.775,0,R)))).length/scale;k=dyaw/ds if ds>1e-8 else 0
  delta=math.atan2(2.575*k,1-steer.location.y*k) if part=='tractor' and axle==0 else 0;deltas.append(delta)
  if f:angles.append(angles[-1]+(centers[f]-centers[f-1]).length/(R*scale))
 # Close visual wheel phase via less-than-half-turn correction spread over entire48s.
 factor=round(angles[-1]/(2*math.pi))*2*math.pi/angles[-1]
 for f in range(N+1):
  steer.rotation_euler.z=deltas[f];spin.rotation_euler.y=angles[f]*factor;steer.keyframe_insert('rotation_euler',index=2,frame=f+1);spin.keyframe_insert('rotation_euler',index=1,frame=f+1)
 wheelrows.append({'name':steer.name,'rolling_speed_correction_percent':(factor-1)*100,'max_steer_degrees':max(abs(math.degrees(x))for x in deltas)})
# Continuous periodic smoke: same12 parcels,2frame spacing,24frame lifespan, wrapped historicalstack positions.
for i in (1,4):
 for slot in range(13):
  o=bpy.data.objects[f'V16 smoke truck {i} exhaust puff {slot}'];o.animation_data_clear();o.hide_render=slot==12
  if slot==12:continue
  nt=o.data.materials[0].node_tree;nt.animation_data_clear();density=[n for n in nt.nodes if n.type=='MATH' and n.operation=='MULTIPLY'][-1];noise=next(n for n in nt.nodes if n.type=='TEX_NOISE')
  for f in range(N+1):
   age=(f+1-slot*2)%24;birth=(f-age)%N;u=age/24;o.location=stacks[i][birth]+Vector((0,0,5*math.sqrt(u)));r=(.28+u)*(.93+.12*math.sin(slot*1.7));o.scale=(r*1.45,r,r*1.45);travel=stacks[i][(birth+1)%N]-stacks[i][birth];o.rotation_euler[2]=math.atan2(travel.y,travel.x)
   density.inputs[1].default_value=2.8*(1-u)**1.15;noise.inputs['W'].default_value=3*math.sin(2*math.pi*f/N);noise.inputs['W'].keyframe_insert('default_value',frame=f+1);density.inputs[1].keyframe_insert('default_value',frame=f+1)
   for channel in ('location','rotation_euler','scale'):o.keyframe_insert(channel,frame=f+1)
for action in bpy.data.actions:
 for layer in action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);bpy.context.view_layer.update();first={o.name:o.matrix_world.copy()for o in s.objects if not o.hide_render};s.frame_set(N+1);bpy.context.view_layer.update();errors={name:max(abs(x-y)for ra,rb in zip(mat,bpy.data.objects[name].matrix_world)for x,y in zip(ra,rb))for name,mat in first.items()};maximum=max(errors.values());assert maximum<.0002,(maximum,sorted(errors.items(),key=lambda p:-p[1])[:10])
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'v20-game-loop.blend'))
(P/'loop-contract.json').write_text(json.dumps({'frames':N,'fps':fps,'seconds':N/fps,'laps':rates,'visible_object_boundary_max_matrix_error':maximum,'wheels':wheelrows,'smoke':'12parcels24frame lifetime; periodic historicalstack births and noise','cab':'integer-cycle harmonics; accepted amplitudes preserved','root_source':str(source)},indent=2));print('LOOP_SAVED',maximum,flush=True)
