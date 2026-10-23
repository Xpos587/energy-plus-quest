import bpy,math,json,os
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-blockout-2026-10-21';R=ROOT/'docs/reviews/inventory-2026-10-21-geometry';D.mkdir(exist_ok=True,parents=True);R.mkdir(exist_ok=True,parents=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.unit_settings.system='METRIC';S.render.engine='BLENDER_WORKBENCH';S.render.image_settings.file_format='PNG';S.render.film_transparent=False;S.world.color=(.82,.86,.90)
S.display.shading.light='STUDIO';S.display.shading.studiolight_rotate_z=.3;S.display.shading.color_type='MATERIAL';S.display.shading.show_shadows=True;S.display.shading.show_cavity=True;S.display.shading.cavity_type='BOTH';S.display.shading.show_object_outline=True;S.display.shading.background_type='WORLD';S.display.shading.show_specular_highlight=False
C={};
for name,col in {'floor':(.69,.75,.79,1),'wall':(.82,.85,.85,1),'steel':(.15,.32,.48,1),'shelf':(.72,.43,.22,1),'carton':(.68,.60,.46,1),'pallet':(.48,.36,.24,1),'person':(.91,.48,.14,1),'skin':(.67,.56,.46,1),'forklift':(.9,.58,.16,1),'dark':(.12,.16,.20,1),'white':(.97,.98,.96,1),'X':(.87,.18,.15,1),'Y':(.15,.57,.28,1),'Z':(.17,.35,.85,1),'target':(.82,.24,.53,1),'glass':(.25,.57,.66,1)}.items():
 m=bpy.data.materials.new(name);m.diffuse_color=col;C[name]=m
cols={}
for n in ['Architecture','Racks','Props','Targets','Guides']:
 c=bpy.data.collections.new(n);S.collection.children.link(c);cols[n]=c
current='Architecture'
def place(o,name,mat):
 o.name=name;o.data.materials.append(C[mat]);
 for c in list(o.users_collection):c.objects.unlink(o)
 cols[current].objects.link(o);return o
def box(name,loc,size,mat='steel'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=place(bpy.context.object,name,mat);o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def cyl(name,loc,r,depth,mat='steel'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=depth,location=loc);return place(bpy.context.object,name,mat)
def sphere(name,loc,r,mat='skin'):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r,location=loc);return place(bpy.context.object,name,mat)
def line(name,a,b,r=.014,mat='steel'):
 v=Vector(b)-Vector(a);o=cyl(name,(Vector(a)+Vector(b))/2,r,v.length,mat);o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o
font=bpy.data.fonts.load('/usr/share/fonts/TTF/DejaVuSans.ttf')
def text(name,body,loc,size=.2,mat='dark',rot=(math.pi/2,0,0),align='CENTER'):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.font=font;cu.size=size;cu.align_x=align;cu.align_y='CENTER';cu.extrude=.001;o=bpy.data.objects.new(name,cu);cols[current].objects.link(o);o.location=loc;o.rotation_euler=rot;cu.materials.append(C[mat]);return o
# One physical room: X=0 and X=12 are opposite, parallel dock walls.
box('Room slab 12 x 7.5 m',(6,3.75,-.12),(12,7.5,.24),'floor')
box('North wall Y7.5',(6,7.55,1.8),(12,.1,3.6),'wall')
# X0 receiving wall opening: Y .7..3.7, Z0..3.0.
for y,l in [(.35,.7),(5.6,3.8)]:box('Receiving wall segment',(0,y,1.8),(.16,l,3.6),'wall')
box('Receiving lintel X0',(0,2.2,3.3),(.16,3,.6),'wall')
# Architectural cutaway: south and dispatch opaque wall surfaces removed, exact full-height wire edges retained.
box('Dispatch wall cutaway sill',(12,3.75,.10),(.16,7.5,.2),'wall')
for x in [0,12]:
 for y in [0,7.5]:line('wall vertical axis',(x,y,0),(x,y,3.6),.025)
 line('parallel wall top',(x,0,3.6),(x,7.5,3.6),.024)
for x,name in [(0,'ПРИЁМКА'),(12,'ОТГРУЗКА')]:
 for y in [.7,3.7]:box(name+' jamb',(x,y,1.5),(.2,.14,3),'steel')
 box(name+' header',(x,2.2,3),(.22,3.14,.16),'steel')
 # World X-normal sign text, consistently oriented up Z.
 o=text(name,name,(x+.13 if x==0 else x-.13,2.2,3.35),.27,'dark');o.rotation_euler=Matrix(((0,0,1),(1,0,0),(0,1,0))).to_euler()
# Docked truck outside X0: bed flush with indoor floor, yard 1.1m lower.
box('Exterior yard z -1.1',(-3.0,2.2,-1.18),(6,4.2,.16),'floor')
box('Truck chassis',(-3.15,2.2,-.42),(5.3,2.35,.32),'dark');box('Truck cargo bed z0',(-2.5,2.2,-.08),(4.8,2.35,.16),'pallet')
box('Truck cargo roof',(-2.5,2.2,2.65),(4.8,2.4,.12),'white')
for y in [1.0,3.4]:box('Truck cargo side',(-2.5,y,1.28),(4.8,.10,2.6),'white')
box('Truck front cargo bulkhead',(-4.9,2.2,1.3),(.12,2.4,2.6),'white');box('Truck cab',(-5.55,2.2,.1),(1.1,2.2,1.6),'steel')
for x in [-4.8,-1.1]:
 for y in [1.05,3.35]:
  o=cyl('Truck wheel',(x,y,-.67),.43,.22,'dark');o.rotation_euler=(math.pi/2,0,0)
for y in [.57,3.83]:box('Dock bumper',(0,y,-.25),(.28,.22,.5),'dark');cyl('Dock bollard',(.45,y,.44),.09,.88,'person')
# Three identical shallow carton shelves, not pallet or forklift-access racks.
current='Racks';labels=['А-Б','В-К','Л-М','Н-У','Ф-Э','Ю-Я'];rackmeta=[]
for n,cx in enumerate([2.4,5.4,8.4]):
 x0,x1=cx-.9,cx+.9;y0,y1=3.5,4.7
 for x in [x0,cx,x1]:
  for y in [y0,y1]:box(f'Rack{n+1} upright',(x,y,1.35),(.055,.055,2.7))
 for z in [.15,1.0,1.85,2.7]:
  box(f'Rack{n+1} deck',(cx,4.1,z),(1.8,1.2,.06),'shelf')
  for y in [y0,y1]:box(f'Rack{n+1} beam',(cx,y,z),(1.8,.065,.09),'steel')
 for bay in range(2):
  bx=x0+.45+bay*.9
  for z in [.42,1.28,2.12]:
   for yy in [3.85,4.35]:box(f'Rack{n+1} bay{bay+1} carton',(bx,yy,z),(.68,.43,.48),'carton')
  plate=box(labels[n*2+bay]+' plaque',(bx,3.445,2.32),(.78,.035,.34),'white');text('Plaque '+labels[n*2+bay],labels[n*2+bay],(bx,3.421,2.32),.21)
 rackmeta.append({'id':n+1,'center':[cx,4.1,1.35],'bounds':[[x0,3.5,0],[x1,4.7,2.7]],'bay_width':.9,'labels':labels[n*2:n*2+2],'storage':'cartons/totes; no rack pallets'})
# Human, pallet, forklift and WMS scale silhouettes.
current='Props'
def human(name,x,y):
 for dx in [-.13,.13]:box(name+' leg',(x+dx,y,.44),(.17,.22,.88),'dark')
 box(name+' torso',(x,y,1.20),(.48,.28,.6),'person');sphere(name+' head',(x,y,1.64),.12);return [x,y,1.76]
keeper=human('Keeper 1.76m',1.0,5.1)
box('Receiving EUR pallet',(1.0,.85,.075),(1.2,.8,.15),'pallet');box('Floor staged cartons',(1.0,.85,.48),(.95,.7,.66),'carton')
# Forklift travels only in front cross aisle; long axis X.
fx,fy=6.8,1.7
box('Forklift body',(fx,fy,.58),(1.65,1.1,.85),'forklift');box('Forklift overhead guard',(fx,fy,2.03),(1.4,1.1,.12),'steel')
for dx in [-.6,.6]:
 for dy in [-.48,.48]:
  box('Forklift guard post',(fx+dx,fy+dy,1.4),(.05,.05,1.2),'steel');o=cyl('Forklift wheel',(fx+dx,fy+dy,.3),.3,.2,'dark');o.rotation_euler=(math.pi/2,0,0)
box('Forklift mast',(fx-.95,fy,1.2),(.16,.9,2.4),'steel')
for dy in [-.32,.32]:box('Forklift fork',(fx-1.6,fy+dy,.14),(1.2,.1,.1),'dark')
box('WMS desk',(10.6,.9,.77),(1.2,.65,.10),'shelf')
for dx in [-.5,.5]:box('WMS desk leg',(10.6+dx,.9,.38),(.06,.5,.76),'steel')
box('WMS terminal',(10.6,1.02,1.1),(.6,.08,.42),'glass');human('WMS operator 1.76m',11.0,1.7)
# Targets: ordinary scene landmarks, proof markers separate collection.
current='Targets';targets={'receiving':[.25,2.2,1.4],'keeper':[1.0,5.1,1.5],'wms':[10.6,.9,1.1],'alphabet':[5.4,3.43,2.32]}
for i,(name,p) in enumerate(targets.items(),1):sphere('Target '+name,p,.10,'target')
# Same physical world axes and grid in both views; optional proof overlay collection.
current='Guides'
for x in range(13):line('1m grid X',(x,0,.013),(x,7.5,.013),.006,'white')
for y in range(8):line('1m grid Y',(0,y,.013),(12,y,.013),.006,'white')
for a,b,col in [((0,0,.04),(12,0,.04),'X'),((0,0,.04),(0,7.5,.04),'Y'),((0,0,0),(0,0,3.6),'Z')]:line('World axis '+col,a,b,.035,col)
for x in [0,12]:line('Parallel Y direction guide',(x,0,3.65),(x,7.5,3.65),.035,'Y')
# Camera compositions of one scene; portrait is an honest tighter viewport, never room deformation.
current='Architecture';cams={}
def camera(name,look,offset,scale,res):
 data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);S.collection.objects.link(o);o.location=Vector(look)+Vector(offset);o.rotation_euler=(Vector(look)-o.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;cams[name]={'object':o,'resolution':res,'look_at':look};return o
camera('Desktop',(3.8,3.4,.8),(17,-23,22),19.5,(1440,900))
camera('Portrait',(3.3,2.8,1),(17,-23,22),13.2,(780,1180))
camera('Topdown',(4,3.3,0),(0,0,30),20,(1600,1000))
S.render.resolution_percentage=100;S.camera=cams['Desktop']['object'];bpy.ops.wm.save_as_mainfile(filepath=str(D/'warehouse-blockout-v1.blend'))
manifest={'units':'m','seed':0,'engine':'BLENDER_WORKBENCH','room':{'bounds':[[0,0,0],[12,7.5,3.6]],'receiving_plane':'X=0','dispatch_plane':'X=12','parallel_normals':[[1,0,0],[1,0,0]],'cutaway':'roof and south wall omitted; dispatch surface cut at z .2 with full-height wire edges, true wall plane X12 unchanged'},'rack_runs':rackmeta,'pedestrian_service_gaps_m':[1.2,1.2],'front_cross_aisle_m':3.5,'operational_limit':'3.5m is modeled clear cross-aisle, not certified turning clearance; forklift excluded from 1.2m gaps','human_height_m':1.76,'floor_pallet':[1.2,.8,.15],'forklift_body':[1.65,1.1,.85],'forklift_total_length_m':2.8,'gate_opening_m':[3,3],'dock':{'indoor_and_cargo_bed_z':0,'exterior_yard_z':-1.1,'truck_long_axis':'X; perpendicular to X0; no forklift route into yard'},'targets':targets,'cameras':{},'art_status':'geometry blockout only; no AI or production edits'}
for name,c in cams.items():
 S.camera=c['object'];S.render.resolution_x,S.render.resolution_y=c['resolution'];
 coords={k:list(world_to_camera_view(S,S.camera,Vector(p))) for k,p in targets.items()}
 manifest['cameras'][name]={'type':'ORTHO','location':list(S.camera.location),'rotation_euler':list(S.camera.rotation_euler),'look_at':c['look_at'],'ortho_scale':S.camera.data.ortho_scale,'resolution':c['resolution'],'safe_margin':.05,'target_projection_uvz':coords,'same_scene':True,'portrait_policy':'viewport/pan; all four targets need not be in one view' if name=='Portrait' else None}
 for guide in [False,True]:
  cols['Guides'].hide_render=not guide;S.render.filepath=str(R/(name.lower()+('-guides' if guide else '-clean')+'.png'));bpy.ops.render.render(write_still=True)
cols['Guides'].hide_render=False;S.camera=cams['Desktop']['object'];S.render.resolution_x,S.render.resolution_y=cams['Desktop']['resolution'];bpy.ops.wm.save_as_mainfile(filepath=str(D/'warehouse-blockout-v1.blend'));(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('BLOCKOUT COMPLETE')
