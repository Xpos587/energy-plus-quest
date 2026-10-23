"""Coherent grounded wheels, path-derived front steering and distance-derived rolling."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
SOURCE=P.parent/'fleet-v16-cab-repair-2026-10-08/fleet-v16-cab-repair.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(1)
R=.358;TRACTOR_X=(.8,-1.35,-2.20);TRAILER_X=(-4.48,-5.35,-6.22);TRACK=.805;REAR=-1.775;BASE=.8-REAR
roots={(i,p):bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')}
paths={k:[] for k in roots};yaw={i:[] for i in range(1,5)}
for f in range(1,193):
 s.frame_set(f);bpy.context.view_layer.update()
 for key,root in roots.items():paths[key].append(root.matrix_world.copy())
 for i in yaw:
  m=roots[i,'tractor'].matrix_world;angle=math.atan2(m[1][0],m[0][0])
  if yaw[i]:angle=yaw[i][-1]+math.atan2(math.sin(angle-yaw[i][-1]),math.cos(angle-yaw[i][-1]))
  yaw[i].append(angle)
steering={};curvature={}
for i in range(1,5):
 ms=paths[i,'tractor'];centers=[m@Vector((REAR,0,R)) for m in ms];scale=ms[0].to_scale().x;curvature[i]=[]
 for f in range(192):
  a=max(0,f-1);b=min(191,f+1);ds=(centers[b]-centers[a]).length/scale
  k=(yaw[i][b]-yaw[i][a])/ds if ds>1e-7 else 0;curvature[i].append(k)
 for side in (-1,1):steering[i,side]=[math.atan2(BASE*k,1-side*TRACK*k) for k in curvature[i]]
s.frame_set(1);bpy.context.view_layer.update()
hidden=[]
for (i,part),root in roots.items():
 for o in root.children_recursive:
  if o.hide_render:continue
  name=o.name
  old=(part=='tractor' and name.startswith(f'V14 {i} ') and any(t in name for t in ('tire carcass','alloy rim ring','recessed wheel bowl','central hub','rim vent')))
  old=old or (part=='trailer' and name.startswith(f'{i} ') and any(t in name for t in ('seated tire','hub center','recessed hub','rim recess')))
  if old:o.hide_render=True;hidden.append(name)
guards=[]
for i in range(1,5):
 root=roots[i,'trailer']
 for suffix in ('','.001'):
  ob=bpy.data.objects[f'{i} trailer side guard{suffix}'];ob.data=ob.data.copy();tr=root.matrix_world.inverted()@ob.matrix_world;inv=tr.inverted()
  for vertex in ob.data.vertices:
   p=tr@vertex.co;p.x=max(p.x,-4.0);vertex.co=inv@p
  ob.data.update();guards.append(ob.name)
rubber=bpy.data.materials['V14 clean blue charcoal rubber'];metal=bpy.data.materials['V14 soft warm alloy'];trim=bpy.data.materials['V14 satin charcoal trim']
col=bpy.data.collections.new('WHEELS path-derived running gear');s.collection.children.link(col)
def empty(name,parent,loc):
 o=bpy.data.objects.new(name,None);col.objects.link(o);o.parent=parent;o.location=loc;return o
def mesh_obj(name,verts,faces,parent,mat,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);o.parent=parent;me.materials.append(mat)
 for face in me.polygons:face.use_smooth=smooth
 return o
def lathe(name,profile,parent,mat):
 vs=[];fs=[];n=64
 for y,r in profile:
  for k in range(n):a=2*math.pi*k/n;vs.append((r*math.cos(a),y,r*math.sin(a)))
 for j in range(len(profile)):
  q=(j+1)%len(profile)
  for k in range(n):kn=(k+1)%n;fs.append((j*n+k,j*n+kn,q*n+kn,q*n+k))
 return mesh_obj(name,vs,fs,parent,mat,True)
def cylinder(name,parent,loc,r,depth,mat,axis='Y',vertices=32):
 vs=[];fs=[]
 for z in (-depth/2,depth/2):
  for k in range(vertices):a=2*math.pi*k/vertices;vs.append((r*math.cos(a),r*math.sin(a),z))
 fs=[tuple(range(vertices-1,-1,-1)),tuple(vertices+k for k in range(vertices))]
 for k in range(vertices):q=(k+1)%vertices;fs.append((k,q,vertices+q,vertices+k))
 o=mesh_obj(name,vs,fs,parent,mat);o.location=loc
 if axis=='Y':o.rotation_euler.x=math.pi/2
 for face in o.data.polygons:face.use_smooth=len(face.vertices)==4
 b=o.modifiers.new('Manufactured edge','BEVEL');b.width=.005;b.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
contact=bpy.data.materials.new('WHEEL tight ambient contact');contact.use_nodes=True;n=contact.node_tree.nodes;n.clear();l=contact.node_tree.links
uv=n.new('ShaderNodeTexCoord');distance=n.new('ShaderNodeVectorMath');distance.operation='DISTANCE';distance.inputs[1].default_value=(.5,.5,0);l.new(uv.outputs['UV'],distance.inputs[0])
ramp=n.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=.05;ramp.inputs['From Max'].default_value=.5;ramp.inputs['To Min'].default_value=.28;ramp.inputs['To Max'].default_value=0;l.new(distance.outputs['Value'],ramp.inputs[0])
trans=n.new('ShaderNodeBsdfTransparent');dark=n.new('ShaderNodeEmission');dark.inputs[0].default_value=(.025,.03,.035,1);mix=n.new('ShaderNodeMixShader');out=n.new('ShaderNodeOutputMaterial');l.new(ramp.outputs[0],mix.inputs[0]);l.new(trans.outputs[0],mix.inputs[1]);l.new(dark.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
contact.surface_render_method='DITHERED'
wheels=[];control_report=[]
for (i,part),root in roots.items():
 xs=TRACTOR_X if part=='tractor' else TRAILER_X
 for axle,x in enumerate(xs):
  # Grounded axle and suspension supports attach wheels to the preserved underframe.
  cylinder(f'WHEEL axle {i} {part} {axle}',root,(x,0,R),.058,1.51,trim)
  mount_top=.70 if part=='tractor' else 1.05
  if part=='trailer':cylinder(f'WHEEL trailer crossmember {i} {axle}',root,(x,0,1.05),.045,1.86,trim)
  for side in (-1,1):cylinder(f'WHEEL suspension mount {i} {part} {axle} {side}',root,(x,side*.36,(R+mount_top)/2),.045,mount_top-R,trim,'Z')
  for side in (-1,1):
   tag=f'{i} {part} {axle} {side}';steer=empty(f'WHEEL steering {tag}',root,(x,side*TRACK,R));spin=empty(f'WHEEL rotation {tag}',steer,(0,0,0))
   tire=lathe(f'WHEEL tyre {tag}',[(-.110,.235),(-.1275,.282),(-.125,.320),(-.108,.345),(-.077,R),(.077,R),(.108,.345),(.125,.320),(.1275,.282),(.110,.235)],spin,rubber)
   tire['rolling_radius']=R;steer['steered_front_axle']=part=='tractor' and axle==0
   # Eight dark ventilation recesses, machined lip and ordinary valve stem make rotation legible.
   for face_side in (-1,1):
    y=face_side*.136
    cylinder(f'WHEEL rim face {tag} {face_side}',spin,(0,y,0),.231,.023,metal)
    cylinder(f'WHEEL rim inset {tag} {face_side}',spin,(0,y+face_side*.013,0),.178,.010,trim)
    cylinder(f'WHEEL hub {tag} {face_side}',spin,(0,y+face_side*.028,0),.085,.042,metal)
    for k in range(8):
     a=2*math.pi*k/8
     cylinder(f'WHEEL vent {tag} {face_side} {k}',spin,(.195*math.cos(a),y+face_side*.014,.195*math.sin(a)),.019,.011,trim,vertices=16)
    cylinder(f'WHEEL valve {tag} {face_side}',spin,(.217,y+face_side*.022,.025),.009,.020,trim,vertices=12)
   # Real ten-lug hub pattern gives a second feature frequency alongside eight vent recesses.
   bolts=[];bolt_faces=[]
   for face_side in (-1,1):
    for k in range(10):
     angle=2*math.pi*k/10;cx=.064*math.cos(angle);cz=.064*math.sin(angle);start=len(bolts)
     for y in (face_side*.185,face_side*.195):
      for j in range(6):a=2*math.pi*j/6;bolts.append((cx+.008*math.cos(a),y,cz+.008*math.sin(a)))
     bolt_faces.append(tuple(start+j for j in range(6)));bolt_faces.append(tuple(start+6+j for j in range(6)))
     for j in range(6):nj=(j+1)%6;bolt_faces.append((start+j,start+nj,start+6+nj,start+6+j))
   mesh_obj(f'WHEEL ten lug heads {tag}',bolts,bolt_faces,spin,trim)
   # Fine staggered crown grooves are geometry on the actual rolling tyre, not cartoon markers.
   vs=[];fs=[]
   for k in range(32):
    a=2*math.pi*k/32
    for band in (-1,1):
     index=len(vs)
     for da,y in ((-.012,band*.071),(.012,band*.071),(.04,0),(.018,0)):
      vs.append((R*math.cos(a+da),y,R*math.sin(a+da)))
     fs.append(tuple(range(index,index+4)))
   mesh_obj(f'WHEEL tread grooves {tag}',vs,fs,spin,trim)
   patch=mesh_obj(f'WHEEL contact {tag}',[(-.19,-.145,-R+.0006),(.19,-.145,-R+.0006),(.19,.145,-R+.0006),(-.19,.145,-R+.0006)],[(0,1,2,3)],steer,contact)
   uvdata=patch.data.uv_layers.new(name='UVMap')
   for loop,v in zip(uvdata.data,((0,0),(1,0),(1,1),(0,1))):loop.uv=v
   ms=paths[i,part];centers=[m@Vector((x,side*TRACK,R)) for m in ms];angles=[];angle=0;total=0;scale=ms[0].to_scale().x
   for f in range(192):
    delta=steering[i,side][f] if part=='tractor' and axle==0 else 0
    if f:
     movement=centers[f]-centers[f-1];heading=ms[f].to_3x3()@Vector((math.cos(delta),math.sin(delta),0));signed=movement.length*(1 if movement.dot(heading)>=0 else -1);total+=signed;angle+=signed/(R*scale)
    steer.rotation_euler.z=delta;steer.keyframe_insert('rotation_euler',index=2,frame=f+1);spin.rotation_euler.y=angle;spin.keyframe_insert('rotation_euler',index=1,frame=f+1);angles.append(angle)
   wheels.append({'tag':tag,'steering':steer.name,'rotation':spin.name,'tyre':tire.name,'radius_local':R,'radius_world':R*scale,'center_local':[x,side*TRACK,R],'total_signed_world_distance':total,'total_rotation_radians':angle,'max_steering_degrees':max(abs(math.degrees(v)) for v in (steering[i,side] if part=='tractor' and axle==0 else [0]))})
# Bake manufactured parts into one mesh per wheel; no per-bolt draw calls/modifiers remain.
s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for info in wheels:
 target=bpy.data.objects[info['tyre']];spin=bpy.data.objects[info['rotation']];inv=spin.matrix_world.inverted();parts=[o for o in spin.children if o.type=='MESH'];vs=[];fs=[];slots=[];faceinfo=[]
 for ob in parts:
  ev=ob.evaluated_get(deps);me=ev.to_mesh();off=len(vs);tr=inv@ob.matrix_world;vs.extend(tr@v.co for v in me.vertices)
  mapping=[]
  for mat in me.materials:
   mat=bpy.data.materials[mat.name]
   if mat not in slots:slots.append(mat)
   mapping.append(slots.index(mat))
  for face in me.polygons:fs.append(tuple(off+j for j in face.vertices));faceinfo.append((mapping[face.material_index],face.use_smooth))
  ev.to_mesh_clear()
 mesh=bpy.data.meshes.new(f'Consolidated rolling wheel {info["tag"]}');mesh.from_pydata(vs,[],fs);mesh.update()
 for mat in slots:mesh.materials.append(mat)
 for face,(slot,smooth) in zip(mesh.polygons,faceinfo):face.material_index=slot;face.use_smooth=smooth
 target.data=mesh
 for ob in parts:
  if ob!=target:bpy.data.objects.remove(ob,do_unlink=True)
for a in bpy.data.actions:
 if not a.name.startswith('WHEEL'):continue
 for layer in a.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(144);bpy.ops.wm.save_as_mainfile(filepath=str(P/'wheels-base.blend'))
receipt={'source':str(SOURCE),'hidden_original_wheel_objects':hidden,'wheel_count':len(wheels),'wheels':wheels,'steering_method':'front tractor pairs only, Ackermann delta=atan2(L*k,1-y*k), k from sampled root yaw versus rear-bogie-center path distance in root units; L=2.575','roll_method':'each actual wheel-center signed world path distance divided by local radius times root scale','road_plane_world_z':0,'contact_material':'tight radial ambient footprint, maximum alpha .28, local half extents .19 x .145, parented to steering pivot at ground+.0006; exclude WHEEL contact objects from broad SUN shadow casters','preserved':'original route roots, hitches, trailer bodies, detailed cab, accepted cab shake, smoke, crew, camera'}
receipt['shortened_side_guards']=guards
(P/'wheel-build-receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps({'wheel_count':len(wheels),'max_steering_degrees':max(w['max_steering_degrees'] for w in wheels),'hidden_parts':len(hidden)}),flush=True)
