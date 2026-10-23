import bpy, math, json, pathlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
SRC=P.parents[1]/'truck-native-quality-2026-10-05/image-to-3d/green-tractor-detailed.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
crew=bpy.data.collections.new('CREW'); bpy.context.scene.collection.children.link(crew)
def mat(name,col,rough=.65):
 m=bpy.data.materials.new('CREW_'+name);m.diffuse_color=(*col,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*col,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=rough;return m
skin=mat('warm_skin',(.64,.37,.23));skinLight=mat('skin_highlight',(.76,.47,.30));lips=mat('muted_lips',(.40,.18,.12));blue=mat('workshirt_blue',(.035,.19,.48));lapel=mat('collar_blue',(.055,.26,.58));seam=mat('shirt_seam',(.025,.10,.22));hair=mat('dark_chestnut',(.075,.044,.025));hair2=mat('light_brown',(.16,.10,.055));white=mat('eyes_ivory',(.88,.86,.78));iris=mat('iris_grey',(.13,.20,.23));black=mat('pupil',(.018,.025,.03));pants=mat('navy_trousers',(.035,.055,.105));rubber=mat('wheel_rubber',(.025,.031,.034));metal=mat('wheel_spokes',(.18,.21,.23));seat=mat('seat_charcoal',(.055,.08,.11))
grey=mat('older_grey_temples',(.24,.25,.24))
def place(o,name,m):
 o.name='CREW_'+name
 for c in list(o.users_collection):c.objects.unlink(o)
 crew.objects.link(o);o.data.materials.append(m)
 if o.type=='MESH':
  for f in o.data.polygons:f.use_smooth=True
 return o
def uv(name,loc,scale,m,segments=32):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=20,location=loc);o=place(bpy.context.object,name,m);o.scale=scale;return o
def tube(name,a,b,r,m,r2=None):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(a+b)/2);o=place(bpy.context.object,name,m);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def mesh(name,verts,faces,m):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('CREW_'+name,me);crew.objects.link(o);me.materials.append(m)
 for f in me.polygons:f.use_smooth=True
 return o
def curve(name,pts,r,m):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for b,p in zip(s.bezier_points,pts):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new('CREW_'+name,c);crew.objects.link(o);c.materials.append(m);return o
# head front is negative X; successive rings sculpt adult chin, jaw, cheek and cranium.
def head(role,Y,hairmat):
 C=Vector((-.775,Y,.145));rings=[(-.086,.025,.028),(-.075,.039,.043),(-.048,.050,.051),(-.020,.056,.056),(.008,.057,.060),(.033,.055,.061),(.058,.050,.052),(.078,.034,.037),(.086,.008,.010)]
 verts=[];N=48
 for z,w,d in rings:
  for j in range(N):
   t=j*2*math.pi/N;sy=math.sin(t);cx=math.cos(t)
   # cheeks flatten the frontal plane, jaw narrows toward chin
   front=d*(.93 if z<-.05 else 1)
   verts.append(tuple(C+Vector((-front*cx,w*sy,z))))
 faces=[]
 for k in range(len(rings)-1):
  for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 faces += [tuple(range(N-1,-1,-1)),tuple((len(rings)-1)*N+j for j in range(N))]
 o=mesh(role+'_sculpted_head',verts,faces,skinLight);mod=o.modifiers.new('soft_face','SUBSURF');mod.levels=1
 for s in [-1,1]:
  uv(role+'_ear_'+str(s),C+Vector((.001,s*.057,-.009)),(.013,.010,.023),skin)
  uv(role+'_ear_inner_'+str(s),C+Vector((-.009,s*.061,-.011)),(.004,.004,.013),lips)
  # eye sockets remain small and adult-proportioned
  uv(role+'_eye_'+str(s),C+Vector((-.0525,s*.024,.015)),(.005,.010,.0035),white)
  uv(role+'_iris_'+str(s),C+Vector((-.0575,s*.024,.0148)),(.0007,.0031,.0030),iris)
  uv(role+'_pupil_'+str(s),C+Vector((-.0581,s*.024,.0148)),(.0004,.0014,.0017),black)
  curve(role+'_brow_'+str(s),[C+Vector((-.056,s*.014,.027)),C+Vector((-.055,s*.025,.029)),C+Vector((-.049,s*.036,.025))],.0017,hairmat)
  curve(role+'_upper_lid_'+str(s),[C+Vector((-.055,s*.015,.017)),C+Vector((-.058,s*.024,.018)),C+Vector((-.051,s*.034,.017))],.00065,skin)
 # bridge and tip form volumetric recognisable nose, no texture cards
 uv(role+'_nose_bridge',C+Vector((-.059,0,.001)),(.008,.0055,.019),skinLight)
 uv(role+'_nose_tip',C+Vector((-.067,0,-.012)),(.005,.006,.0045),skinLight)
 for s in [-1,1]:uv(role+'_nostril_'+str(s),C+Vector((-.067,s*.0045,-.015)),(.0015,.0016,.0008),lips)
 curve(role+'_upper_lip',[C+Vector((-.050,-.017,-.035)),C+Vector((-.055,-.006,-.034)),C+Vector((-.0555,0,-.035)),C+Vector((-.055,.007,-.034)),C+Vector((-.050,.017,-.035))],.0007,lips)
 curve(role+'_lower_lip',[C+Vector((-.050,-.013,-.037)),C+Vector((-.054,0,-.038)),C+Vector((-.050,.013,-.037))],.0006,skin)
 # hair cap follows head rings, waved swept forelock, sideburns
 hv=[]
 for k in range(5):
  phi=.03+(math.pi*.48)*k/4
  for j in range(N):
   t=j*2*math.pi/N;z=.034+.063*math.cos(phi);x=-.064*math.sin(phi)*math.cos(t);y=.062*math.sin(phi)*math.sin(t)
   # hairline is higher on front, leaves forehead
   if k==4:
    z=(.058 if role=='passenger' else .043) if math.cos(t)>0 else .010
    if role=='passenger' and math.cos(t)>0:x*=.86
   hv.append(tuple(C+Vector((x,y,z))))
 hf=[]
 for k in range(4):
  for j in range(N):hf.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 cap=mesh(role+'_hair_cap',hv,hf,hairmat)
 if role=='passenger':
  cap.data.materials.append(grey)
  for f in cap.data.polygons:
   p=sum((cap.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
   if abs(p.y-Y)>.045 and p.z<C.z+.055:f.material_index=1
 if role=='driver':uv(role+'_swept_forelock',C+Vector((-.036,-.012,.066)),(.020,.031,.011),hairmat)
 for s in [-1,1]:
  uv(role+'_sideburn_'+str(s),C+Vector((.002,s*.052,.022)),(.018,.003,.019),grey if role=='passenger' else hairmat)
 for j in range(4):curve(role+'_hair_flow_'+str(j),[C+Vector((-.031,-.030+j*.015,.070)),C+Vector((-.008,-.035+j*.015,.083)),C+Vector((.025,-.026+j*.015,.070))],.0012,hairmat)
 return C
for role,Y,hm in [('driver',-.20,hair2),('passenger',.20,hair)]:
 head(role,Y,hm)
 tube(role+'_neck',(-.70,Y,.008),(-.755,Y,.073),.023,skinLight)
 # shirt tapered from seated waist to broad adult shoulders
 uv(role+'_shirt_torso',(-.65,Y,-.080),(.070,.103,.125),blue)
 uv(role+'_shoulder_L',(-.66,Y-.079,-.025),(.047,.040,.043),blue)
 uv(role+'_shoulder_R',(-.66,Y+.079,-.025),(.047,.040,.043),blue)
 uv(role+'_hips',(-.53,Y,-.235),(.077,.077,.057),pants)
 for s in [-1,1]:
  tube(role+'_seated_thigh_'+str(s),(-.54,Y+s*.045,-.242),(-.73,Y+s*.049,-.273),.039,pants,r2=.031)
  uv(role+'_knee_'+str(s),(-.73,Y+s*.049,-.278),(.034,.034,.037),pants)
  tube(role+'_calf_'+str(s),(-.73,Y+s*.049,-.285),(-.71,Y+s*.049,-.425),.026,pants,r2=.020)
  uv(role+'_shoe_'+str(s),(-.753,Y+s*.049,-.443),(.058,.029,.024),rubber)
 # front shirt placket, two pockets, folded collar
 curve(role+'_placket',[(-.720,Y,-.18),(-.725,Y,-.07),(-.711,Y,.018)],.002,seam)
 for s in [-1,1]:
  mesh(role+'_collar_'+str(s),[(-.725,Y+s*.005,.040),(-.714,Y+s*.052,.013),(-.739,Y+s*.027,-.025)],[(0,1,2)],lapel)
  curve(role+'_pocket_'+str(s),[(-.711,Y+s*.026,-.048),(-.715,Y+s*.067,-.047),(-.709,Y+s*.066,-.090),(-.718,Y+s*.029,-.090)],.0015,lapel)
 # seated support pads/backrests
 uv(role+'_seat_base',(-.51,Y,-.290),(.10,.096,.031),seat)
 uv(role+'_seat_back',(-.525,Y,-.074),(.029,.094,.185),seat)
 if role=='driver':
  for s in [-1,1]:
   shoulder=(-.68,Y+s*.085,-.010);elbow=(-.711,Y+s*.096,-.095);hand=(-.774,Y+s*.062,.015)
   tube(role+'_upper_arm_'+str(s),shoulder,elbow,.033,blue,r2=.026)
   tube(role+'_forearm_'+str(s),elbow,hand,.025,blue,r2=.017)
   uv(role+'_hand_'+str(s),hand,(.018,.017,.022),skinLight)
   for f in range(3):curve(role+'_grip_finger_'+str(s)+'_'+str(f),[(-.793,Y+s*.060+(f-1)*.008,.025),(-.793,Y+s*.063+(f-1)*.008,.013),(-.781,Y+s*.063+(f-1)*.008,.007)],.0034,skin)
 else:
  for s in [-1,1]:
   a=(-.67,Y+s*.083,-.01);b=(-.665,Y+s*.12,-.13);h=(-.722,Y+s*.053,-.211)
   tube(role+'_upper_arm_'+str(s),a,b,.032,blue,r2=.026);tube(role+'_forearm_'+str(s),b,h,.026,blue,r2=.019);uv(role+'_relaxed_hand_'+str(s),h,(.028,.020,.016),skinLight)
# one steering wheel, tilted normal towards -X. Hands on upper-left and upper-right rim.
center=Vector((-.79,-.20,-.035));normal=Vector((-1,0,.32)).normalized();u=Vector((0,1,0));v=normal.cross(u).normalized();pts=[center+.077*(math.cos(t)*u+math.sin(t)*v) for t in [i*2*math.pi/64 for i in range(65)]]
curve('steering_wheel_rim',pts,.007,rubber)
for angle in [math.pi/6,5*math.pi/6,3*math.pi/2]:tube('steering_wheel_spoke_'+str(angle),center,center+.070*(math.cos(angle)*u+math.sin(angle)*v),.005,metal)
uv('steering_wheel_hub',center,(.013,.019,.019),rubber);tube('steering_column',center,(-.71,-.20,-.13),.010,metal)
# Ground truth asset remains a crew-only compatible-coordinate scene.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1000;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.film_transparent=True
s.world=bpy.data.worlds.new('CREW_studio_world');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.58,.65,.75,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
for name,loc,power,size in [('key',(-2,-1,3),250,3),('fill',(-2,2,1),140,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='PREVIEW_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((-.7,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='PREVIEW_camera';s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.72
s.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'crew.blend'))
def render(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
render('crew-front',(-2.8,0,.25),(-.68,0,-.105),1.03)
render('crew-three-quarter',(-2.0,1.0,.45),(-.67,0,-.105),1.03)
# Read-only cab source copied through library load; remove only front windshield faces in preview copy.
with bpy.data.libraries.load(str(SRC),link=False) as (a,b):b.objects=['Mesh_0']
cab=b.objects[0];s.collection.objects.link(cab);cab.name='PREVIEW_actual_cab'
import bmesh
bm=bmesh.new();bm.from_mesh(cab.data);remove=[]
for f in bm.faces:
 p=f.calc_center_median();n=f.normal
 if n.x<-.3 and abs(p.x-(.187338*p.z-.913884))<.024 and abs(p.y)<.39 and .017<p.z<.254:remove.append(f)
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(cab.data);bm.free()
render('cab-front',(-3,0,.32),(-.80,0,.12),.91)
render('cab-three-quarter',(-2.3,1.3,.60),(-.77,0,.09),1.0)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'crew-cab-preview.blend'))
(P/'receipt.json').write_text(json.dumps({'source':str(SRC),'crew_asset':'crew.blend','objects':len(crew.objects),'volumetric_humans':True,'head_centers':{'driver':[-.775,-.20,.145],'passenger':[-.775,.20,.145]},'hips':{'driver':[-.53,-.20,-.235],'passenger':[-.53,.20,-.235]},'wheel_center':list(center),'wheel_radius':.077,'wheel_normal':list(normal),'windshield_faces_removed_in_preview':len(remove),'render_engine':'CYCLES','samples':24,'resolution':[1000,720],'limitations':['stylized geometric faces do not replicate approved face identity exactly','cab preview front windshield removed only in new copy','roof can occlude crew at steep aerial angles']},indent=2))
