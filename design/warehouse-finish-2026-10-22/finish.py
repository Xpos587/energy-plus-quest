import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-finish-2026-10-22';R=ROOT/'docs/reviews/inventory-2026-10-22-finish'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'design/warehouse-blockout-2026-10-21/warehouse-blockout-v4.blend'))
S=bpy.context.scene
original={o.name:{'matrix':[list(row) for row in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices]} for o in bpy.data.objects if o.type=='MESH'}
camdata={o.name:{'matrix':[list(row) for row in o.matrix_world],'scale':o.data.ortho_scale} for o in bpy.data.objects if o.type=='CAMERA'}
new=bpy.data.collections.new('Illustration finishing');S.collection.children.link(new)
def mat(name,col,rough=.45,metal=0,em=0):
 m=bpy.data.materials.new('Finish '+name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*col,1);n.inputs['Roughness'].default_value=rough;n.inputs['Metallic'].default_value=metal
 if em:n.inputs['Emission Color'].default_value=(*col,1);n.inputs['Emission Strength'].default_value=em
 return m
M={k:mat(k,c) for k,c in {'blue':(.025,.24,.64),'orange':(1,.23,.025),'ivory':(.85,.82,.69),'floor':(.42,.64,.78),'dark':(.035,.065,.11),'skin':(.82,.49,.29),'hair':(.15,.12,.10),'white':(.94,.96,.94),'carton':(.64,.36,.13),'tape':(.82,.62,.34),'wood':(.52,.30,.12),'lightblue':(.34,.75,1),'pale':(.62,.83,.95),'green':(.22,.49,.12),'grey':(.30,.36,.42)}.items()}
M['window']=mat('window',(.37,.72,.94),em=.25);M['screen']=mat('screen',(.025,.55,.84),em=.4);M['stripe']=mat('stripe',(.92,.94,.89));M['lamp']=mat('lamp',(1,.82,.34),em=1)
def apply(o,m):o.data.materials.clear();o.data.materials.append(M[m])
def bevel(o,r=.025):
 if o.type=='MESH':b=o.modifiers.new('Small illustrated edge','BEVEL');b.width=r;b.segments=3;b.affect='EDGES';o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL')
def put(o,name,m):
 o.name='Finish '+name
 for c in list(o.users_collection):c.objects.unlink(o)
 new.objects.link(o);apply(o,m);return o
def box(n,p,d,m,r=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=put(bpy.context.object,n,m);o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if r:bevel(o,r)
 return o
def ell(n,p,d,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1,location=p);o=put(bpy.context.object,n,m);o.scale=d
 for f in o.data.polygons:f.use_smooth=True
 return o
def rod(n,a,b,r,m):
 v=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=v.length,location=(Vector(a)+Vector(b))/2);o=put(bpy.context.object,n,m);o.rotation_euler=v.to_track_quat('Z','Y').to_euler();bevel(o,.008);return o
# Existing geometry receives material and tiny edge treatment; no vertex or object-coordinate edits.
for o in list(bpy.data.objects):
 if o.type not in {'MESH','FONT'}:continue
 n=o.name
 if n.startswith(('Target ','World axis','Parallel Y direction')):o.hide_render=True;continue
 if n.startswith('1m grid'):o.hide_render=True;continue
 if n.startswith('Keeper 1.76m'):o.hide_render=True;continue
 key='blue'
 if 'wall' in n.lower() or 'lintel' in n:key='ivory'
 if 'slab' in n or 'yard' in n:key='floor'
 if 'beam' in n:key='orange'
 if 'deck' in n:key='wood'
 if 'carton' in n:key='carton'
 if 'pallet' in n.lower() or 'cargo bed' in n:key='wood'
 if 'plaque' in n:key='white' if o.type=='MESH' else 'blue'
 if o.type=='FONT':key='blue'
 if 'wheel' in n or 'chassis' in n or 'bumper' in n or 'mast' in n or 'fork' in n.lower():key='dark'
 if n=='Forklift body':key='orange'
 if 'Truck cargo' in n and 'wire' not in n:key='white'
 if 'Drone' in n:key='blue' if ('body' in n or 'guard' in n or 'arm' in n) else 'dark'
 if 'WMS desk' in n:key='wood' if n=='WMS desk' else 'blue'
 if 'terminal' in n:key='dark'
 if 'bollard' in n:key='orange'
 apply(o,key)
 if o.type=='MESH' and not ('wire' in n or 'axis' in n):bevel(o,.015 if 'Rack' in n else .025)
# Truck normal enclosed body with rear aperture. Restore immutable existing skin objects.
for o in bpy.data.objects:
 if o.name.startswith(('Truck cargo roof','Truck cargo side')):o.hide_render=False
 if o.name.startswith('Truck cargo wire'):o.hide_render=True
box('truck windshield',(-6.108,2.2,.40),(.015,1.65,.68),'lightblue')
box('truck side window',(-5.55,1.087,.48),(.72,.018,.52),'lightblue')
box('truck front bumper',(-6.14,2.2,-.42),(.12,2.1,.15),'grey')
for y in [1.4,3.0]:box('truck headlight',(-6.208,y,-.12),(.025,.30,.18),'lamp')
for x in [-4.8,-1.1]:
 for y in [.92,3.48]:rod('wheel hub',(x,y-.025,-.67),(x,y+.025,-.67),.20,'grey')
# Floor soft light tiles exactly on existing floor plane.
for x in range(13):rod('floor tile joint',(x,.03,.007),(x,7.47,.007),.005,'pale')
for y in range(8):rod('floor tile joint',(.03,y,.007),(11.97,y,.007),.005,'pale')
# Large bright panels inset onto unchanged north wall plane; blue frames and crossbars.
for x in [1.25,3.65,6.05,8.45,10.85]:
 box('window frame',(x,7.483,2.10),(1.95,.045,2.12),'blue')
 box('window glass',(x,7.451,2.10),(1.80,.018,1.97),'window')
 box('window sky top',(x,7.438,2.65),(1.76,.012,.80),'lightblue')
 box('window horizon',(x,7.428,1.55),(1.76,.012,.36),'pale')
 for dx in [-.50,.08,.53]:ell('distant foliage',(x+dx,7.415,1.39),(.30,.012,.24),'green')
 box('window mullion',(x,7.402,2.10),(.045,.040,1.98),'blue')
 box('window transom',(x,7.401,2.17),(1.81,.040,.045),'blue')
 box('window sill',(x,7.39,1.06),(2.05,.18,.07),'ivory')
# Architectural column and lighting details do not relocate wall.
for x in [0,2.45,4.85,7.25,9.65,12]:box('north wall trim',(x,7.43,1.8),(.07,.06,3.6),'blue')
for x in [1.25,6.05,10.85]:
 rod('lamp neck',(x,7.4,3.35),(x,7.1,3.35),.035,'blue');ell('wall lamp',(x,7.04,3.28),(.14,.14,.09),'blue');ell('lamp warm underside',(x,7.04,3.22),(.10,.10,.025),'lamp')
# Carton tape seams, top folds, tiny address labels; some original cartons become white wrapped packs.
random.seed(7)
for i,o in enumerate([o for o in bpy.data.objects if 'carton' in o.name.lower() and o.name in original]):
 x,y,z=o.location;w,d,h=o.dimensions
 wrapped=(i%7==4)
 if wrapped:apply(o,'white')
 box('package top tape',(x,y,z+h/2+.004),(.07,d*.96,.008),'pale' if wrapped else 'tape',.002)
 box('package front tape',(x,y-d/2-.004,z),(.07,.008,h*.97),'pale' if wrapped else 'tape',.002)
 box('package label',(x+w*.24,y-d/2-.010,z-h*.20),(w*.19,.008,h*.22),'white',.002)
 for off in [-.035,0,.035]:box('label barcode',(x+w*.24+off,y-d/2-.016,z-h*.20),(.008,.004,h*.14),'grey',0)
# Rack bolt heads and side diagonal braces remain inside exact original envelope.
for cx in [2.4,5.4,8.4]:
 for x in [cx-.865,cx+.865]:
  for z in [.22,1.07,1.92,2.58]:ell('rack bolt',(x,3.495,z),(.014,.008,.014),'white')
  rod('rack end diagonal',(x,3.57,.22),(x,4.63,1.77),.012,'blue');rod('rack end diagonal',(x,4.63,.22),(x,3.57,1.77),.012,'blue')
# One fully modeled keeper. Faces oriented south so visible to canonical camera.
def person(n,x,y,z=0,seated=False):
 if not seated:
  for dx in [-.12,.12]:
   box(n+' boot',(x+dx,y-.06,z+.08),(.18,.33,.16),'dark',.045);rod(n+' trouser',(x+dx,y,z+.17),(x+dx,y,z+.90),.085,'blue')
  torsoz=z+1.20;headz=z+1.61
 else:
  torsoz=z+1.17;headz=z+1.57
  for dx in [-.12,.12]:
   rod(n+' seated thigh',(x+dx,y,z+.92),(x+dx,y-.28,z+.86),.085,'blue');rod(n+' seated shin',(x+dx,y-.28,z+.86),(x+dx,y-.30,z+.55),.075,'blue');box(n+' boot',(x+dx,y-.36,z+.51),(.17,.27,.13),'dark')
 ell(n+' jacket',(x,y,torsoz),(.25,.16,.32),'blue');box(n+' vest',(x,y-.135,torsoz),(.36,.07,.49),'orange',.025)
 box(n+' reflective band',(x,y-.177,torsoz-.10),(.38,.012,.045),'white',.001)
 rod(n+' neck',(x,y,headz-.19),(x,y,headz-.09),.065,'skin');ell(n+' head',(x,y,headz),(.125,.11,.15),'skin');ell(n+' hair',(x,y+.014,headz+.08),(.128,.11,.075),'hair')
 ell(n+' nose',(x,y-.11,headz-.01),(.029,.034,.035),'skin')
 for dx in [-.045,.045]:ell(n+' eye',(x+dx,y-.106,headz+.035),(.012,.009,.012),'dark')
 for dx in [-.29,.29]:
  a=(x+dx*.78,y,torsoz+.16);b=(x+dx,y-.04,torsoz-.12);c=(x+dx,y-.20,torsoz-.20);rod(n+' sleeve',a,b,.078,'blue');rod(n+' forearm',b,c,.060,'blue');ell(n+' hand',c,(.065,.055,.065),'skin')
 if not seated:box(n+' scanner',(x+.29,y-.25,torsoz-.15),(.08,.10,.13),'dark')
person('keeper',9.8,2.3)
# Driver within original forklift guard, legs tucked inside original machine footprint.
box('forklift seat',(6.95,1.7,.99),(.43,.55,.12),'dark');box('forklift backrest',(7.12,1.7,1.20),(.11,.55,.47),'dark');person('driver',6.78,1.7,-.02,True)
rod('steering column',(6.40,1.7,.85),(6.37,1.7,1.26),.035,'dark')
bpy.ops.mesh.primitive_torus_add(major_radius=.15,minor_radius=.021,location=(6.37,1.7,1.26));put(bpy.context.object,'steering wheel','dark')
ell('forklift beacon',(7.18,1.7,2.15),(.09,.09,.10),'orange')
# WMS screen, pedestal stand, keyboard, unobtrusive UI lines.
box('monitor stand',(9.5,1.02,.86),(.08,.09,.19),'dark');box('monitor foot',(9.5,1.0,.83),(.34,.23,.025),'dark');box('monitor screen',(9.5,.974,1.1),(.52,.012,.34),'screen')
for z in [1.01,1.08,1.15]:box('WMS screen row',(9.53,.964,z),(.31,.005,.016),'pale',0)
box('keyboard',(9.5,.73,.835),(.48,.18,.018),'dark');ell('mouse',(9.89,.73,.844),(.045,.07,.018),'dark')
# Pallet slats and receiving stack details.
for y in [.53,.69,.85,1.01,1.17]:box('pallet slat',(1,y,.153),(1.18,.12,.025),'wood',.007)
# Drone orange accents and visible front lens preserve four existing rotors.
ell('drone orange crown',(9.5,5.8,2.88),(.16,.14,.065),'orange');ell('drone lens',(9.5,5.628,2.60),(.055,.018,.055),'screen')
# Render setup, soft illustrative physically lit surfaces.
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True;S.cycles.seed=0;S.render.threads_mode='FIXED';S.render.threads=8
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.58,.75,.90,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for name,p,power,size,col in [('key',(2,-4,13),1800,8,(1,.87,.71)),('fill',(10,1,10),1300,7,(.69,.84,1)),('window',(4,6,10),1200,6,(1,1,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(name,d);new.objects.link(o);o.location=p;o.rotation_euler=(Vector((5,3,0))-o.location).to_track_quat('-Z','Y').to_euler()
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.render.film_transparent=False
S.camera=bpy.data.objects['FullSourceOverscan'];S.render.resolution_x=1440;S.render.resolution_y=1000;S.render.resolution_percentage=100
# Exact original-coordinate audit, no file hashes or sizes.
errors=[]
for n,v in original.items():
 o=bpy.data.objects[n]
 if [list(row) for row in o.matrix_world]!=v['matrix'] or [list(x.co) for x in o.data.vertices]!=v['vertices']:errors.append(n)
for n,v in camdata.items():
 o=bpy.data.objects[n]
 if [list(row) for row in o.matrix_world]!=v['matrix'] or o.data.ortho_scale!=v['scale']:errors.append(n)
assert not errors,errors
receipt={'original_mesh_objects_checked':len(original),'mesh_coordinate_or_transform_changes':errors,'original_cameras_checked':len(camdata),'source':'design/warehouse-blockout-2026-10-21/warehouse-blockout-v4.blend','render':[1440,1000],'seed':0,'engine':'CYCLES','samples':32,'geometry_policy':'Original mesh vertices/object transforms/cameras unchanged. Keeper source silhouettes hidden, additive person at same position, original truck skin revealed. Additive surface detail only.','source_contract':json.loads((ROOT/'design/warehouse-blockout-2026-10-21/manifest-v4.json').read_text())['runtime_source_contract']}
(R/'geometry-preservation-v1.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'warehouse-finish-v1.blend'));S.render.filepath=str(R/'source-v1-clean.png');bpy.ops.render.render(write_still=True)
print('FINISH V1 COMPLETE')
