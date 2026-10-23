import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-clean-v13-2026-10-07/fleet-v13-clean.blend'))
s=bpy.context.scene;s.frame_set(1)
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')]
def pose():return {o.name:[list(r) for r in o.matrix_world] for o in roots}
base={}
for f in (1,385,769,1152):s.frame_set(f);base[f]=pose()
s.frame_set(1)
# Shared broad illumination: surface normals and ground shadows use this same sun vector.
light=Vector((-40,35,70)).normalized()
def shade(m,color=None):
 m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
 if color is not None:
  n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);out=n.new('ShaderNodeOutputMaterial');l.new(e.outputs[0],out.inputs[0])
 for e in list(n):
  if e.type!='EMISSION':continue
  src=e.inputs[0].links[0].from_socket if e.inputs[0].is_linked else None;c=e.inputs[0].default_value[:]
  geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=light;l.new(geo.outputs['Normal'],dot.inputs[0])
  ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements[0].position=0;r.elements[0].color=(.49,.62,.76,1);r.elements[1].position=.86;r.elements[1].color=(1.12,1.08,.97,1);r.elements.new(.28).color=(.72,.80,.86,1);r.interpolation='EASE';l.new(dot.outputs['Value'],ramp.inputs[0])
  mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=c
  if src:l.new(src,mix.inputs[1])
  l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],e.inputs[0])
 return m
fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
mats={m for o in fleet if o.type=='MESH' for m in o.data.materials if m}
for m in mats:
 if 'windshield' in m.name.lower() or 'exhaust' in m.name.lower():continue
 shade(m)
pal={1:(.66,.115,.075),2:(.065,.34,.75),3:(.255,.59,.10),4:(.97,.65,.075)}
def mat(name,col):return shade(bpy.data.materials.new('V14 '+name),col)
trim=mat('satin charcoal trim',(.105,.16,.19));metal=mat('soft warm alloy',(.50,.56,.56));glass=mat('cool glazing',(.15,.38,.49));lamp=mat('warm round headlight',(.94,.91,.65));amber=mat('amber indicators',(.96,.36,.035))
def mesh(name,verts,faces,root,material,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 if len(faces)>1:
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new('V14 '+name,me);s.collection.objects.link(o);o.parent=root;me.materials.append(material)
 if bevel:
  b=o.modifiers.new('Manufactured edge radius','BEVEL');b.width=bevel;b.segments=3
  no=o.modifiers.new('Weighted broad face normals','WEIGHTED_NORMAL');no.keep_sharp=True
 return o

def box(name,loc,dim,root,material,bevel=.035):
 x,y,z=loc;a,b,c=[v/2 for v in dim];v=[(x+dx*a,y+dy*b,z+dz*c) for dx,dy,dz in ((-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1))]
 return mesh(name,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],root,material,bevel)
def line(name,a,b,r,root,material):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length);o=bpy.context.object;o.name='V14 '+name;o.parent=root;o.location=(Vector(a)+Vector(b))/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);return o
receipts=[]
for i in range(1,5):
 paint=mat(f'{i} painted body',pal[i]);canvas=mat(f'{i} canvas pigment',tuple(v*.93 for v in pal[i]));root=bpy.data.objects[f'truck-{i}-tractor'];trailer=bpy.data.objects[f'truck-{i}-trailer']
 for o in trailer.children_recursive:
  if o.type=='MESH':
   for j,m in enumerate(o.data.materials):
    if m and ('woven pale canvas' in m.name or 'clean porcelain cargo' in m.name):o.data.materials[j]=canvas if i in (1,4) else paint
 # Cab's masked color texture remains, with stronger coherent surface shading.
 cabmat=bpy.data.materials[f'V09 {i} painted cab front roof near side']
 for n in cabmat.node_tree.nodes:
  if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and not n.inputs[1].is_linked:n.inputs[1].default_value=(*pal[i],1)
 if i in (1,4):
  o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];o.data=o.data.copy();transform=root.matrix_world.inverted()@o.matrix_world;inverse=transform.inverted()
  bm=bmesh.new();bm.from_mesh(o.data);remove=[]
  crew=[f for f in bm.faces if f.material_index==1];uv=bm.loops.layers.uv.active
  crew_before=[tuple(l[uv].uv) for f in crew for l in f.loops]
  for f in bm.faces:
   if f.material_index==1:continue
   pts=[transform@v.co for v in f.verts];cen=sum(pts,Vector())/len(pts)
   # Original wheels/chassis survive; modern body/grille/windows above are actually removed.
   if f.material_index in (2,3,4) or (cen.x>-.60 and cen.z>1.19) or (cen.x>.045 and (cen.z>.94 or cen.x>1.40 or (cen.x>1.23 and cen.z>.67))):remove.append(f)
  bmesh.ops.delete(bm,geom=remove,context='FACES')
  # Keep the exact character UV mapping on a planar, new cab window.
  for v in {v for f in crew for v in f.verts}:
   p=transform@v.co;p.x=1.715;p.z=1.37+(p.z-1.405)*(.86 if i==1 else .69);p.y*=1 if i==1 else .95;v.co=inverse@p
  crew_after=[tuple(l[uv].uv) for f in crew for l in f.loops];assert crew_before==crew_after
  bm.to_mesh(o.data);bm.free();o.data.update()
  for ob in root.children_recursive:
   if ob.name.startswith(f'V09 CLEAN {i}'):ob.hide_render=True
  h=2.13 if i==1 else 1.99;w=.95 if i==1 else .90;back=.08 if i==1 else .30
  # Old forward-control cab shell, low roof, exposed bumper. Window cut-out remains open.
  box(f'{i} older flat front lower panel',(1.61,0,1.085),(.21,2*w,.57),root,paint,.045)
  box(f'{i} lower nose',(1.59,0,.67),(.26,2*w,.29),root,paint,.04)
  box(f'{i} rear cab bulkhead',(back,0,1.46),(.14,2*w,h-.77),root,paint,.045)
  box(f'{i} low rounded rain roof',((back+1.60)/2,0,h),((1.60-back)+.18,2*w+.08,.13),root,paint,.055 if i==1 else .022)
  # Side cheeks with a circular wheel opening and inset door window.
  for sign in (-1,1):
   # Profile clockwise with lower circular opening cut into its outline.
   profile=[(back,.68),(back,h-.06),(1.62,h-.06),(1.72,1.32),(1.72,.68),(1.38,.68)]
   profile +=[(.85+.52*math.cos(a),.44+.52*math.sin(a)) for a in [math.pi*k/18 for k in range(3,17)]]
   profile +=[(.31,.68)]
   vs=[(x,sign*w,z)for x,z in profile];mesh(f'{i} formed side cab {sign}',vs,[tuple(range(len(vs)))],root,paint,.014)
   # Small side glazing and rubber surround; old triangular quarter-light.
   window=[(.51,h-.19),(1.45,h-.19),(1.58,1.47),(.51,1.47)]
   mesh(f'{i} side rubber window {sign}',[(x,sign*(w+.006),z) for x,z in window],[(0,1,2,3)],root,trim)
   inset=[(.56,h-.23),(1.41,h-.23),(1.52,1.51),(.56,1.51)]
   mesh(f'{i} side blue glass {sign}',[(x,sign*(w+.013),z) for x,z in inset],[(0,1,2,3)],root,glass)
   line(f'{i} side glass divider {sign}',(1.22,sign*(w+.02),1.50),(1.22,sign*(w+.02),h-.22),.014,root,trim)
   box(f'{i} door handle {sign}',(.53,sign*(w+.025),1.28),(.19,.035,.035),root,metal,.01)
   line(f'{i} door rear seam {sign}',(.37,sign*(w+.017),.99),(.37,sign*(w+.017),h-.17),.007,root,trim)
   box(f'{i} entry step {sign}',(.27,sign*.96,.56),(.36,.19,.10),root,metal,.025)
   # Arc over retained original front wheel.
   for k in range(16):
    a=math.pi*k/16;b=math.pi*(k+1)/16
    line(f'{i} rolled wheel arch {sign} {k}',(.85+.54*math.cos(a),sign*(w+.016),.44+.54*math.sin(a)),(.85+.54*math.cos(b),sign*(w+.016),.44+.54*math.sin(b)),.028,root,paint)
   line(f'{i} narrow mirror arm {sign}',(1.47,sign*.87,1.85),(1.56,sign*1.045,1.86),.018,root,metal)
   box(f'{i} compact older mirror {sign}',(1.57,sign*1.057,1.76),(.095,.10,.28),root,trim,.025)
  # Windshield border follows the retained crew plane, never crossing a face.
  top=1.37+((2.063 if i==1 else 2.206)-1.405)*(.86 if i==1 else .69)
  box(f'{i} windshield top gasket',(1.731,0,top+.025),(.035,1.76 if i==1 else 1.67,.055),root,trim,.012)
  box(f'{i} windshield bottom gasket',(1.737,0,1.365),(.035,1.76 if i==1 else 1.67,.045),root,trim,.01)
  for sy in (-1,1):box(f'{i} windshield pillar {sy}',(1.731,sy*(.85 if i==1 else .81),(1.37+top)/2),(.06,.055,top-1.33),root,paint,.013)
  line(f'{i} split screen mullion',(1.738,0,1.385),(1.738,0,top-.015),.017,root,trim)
  for sy in (-1,1):line(f'{i} wiper {sy}',(1.745,sy*.39,1.39),(1.745,sy*.58,1.53),.011,root,trim)
  box(f'{i} separate steel bumper',(1.80,0,.44),(.20,2*w+.10,.18),root,metal,.035)
  box(f'{i} compact grille',(1.731,0,.98),(.04,.94 if i==1 else .72,.29),root,trim,.03)
  for z in (.89,.98,1.07):box(f'{i} horizontal grille bar',(1.758,0,z),(.023,.88 if i==1 else .65,.023),root,metal,.007)
  for sy in (-1,1):
   y=sy*(.73 if i==1 else .69)
   line(f'{i} round lamp bezel {sy}',(1.728,y,.84),(1.790,y,.84),.14 if i==1 else .125,root,metal)
   line(f'{i} round headlamp lens {sy}',(1.792,y,.84),(1.800,y,.84),.108 if i==1 else .097,root,lamp)
   box(f'{i} amber signal {sy}',(1.750,sy*.79,1.14),(.045,.14,.075),root,amber,.02)
  # Continuous cloth shell: broad folds are actual shape, no applied stripes or rectangles.
  for ob in trailer.children_recursive:
   if any(k in ob.name for k in ('long semitrailer','rear doors','trailer roof rail','softly folded','subdued canvas')):ob.hide_render=True
  verts=[];faces=[];N=90;M=36
  # Cross-section from near bottom up the side, across gently arched top, down far side.
  section=[]
  for k in range(9):section.append((-.915,1.07+(3.08-1.07)*k/8))
  for k in range(1,21):
   y=-.915+1.83*k/20;section.append((y,3.08+.18*(1-(y/.915)**2)))
  for k in range(1,9):section.append((.915,3.08-(3.08-1.07)*k/8))
  M=len(section)
  for a in range(N+1):
   x=-6.8+7.5*a/N;wave=math.sin((x+.2)*2*math.pi/.72)
   for y,z in section:
    if abs(y)>.91:
     envelope=math.sin(math.pi*(z-1.07)/(3.08-1.07));y+=math.copysign(.047*wave*envelope,y);z+=.018*math.sin(x*5)*envelope
    else:z+=.012*math.sin(x*4)*(1-(y/.915)**2)
    verts.append((x,y,z))
  for a in range(N):
   for b in range(M-1):q=a*M+b;faces.append((q,q+M,q+M+1,q+1))
  faces.extend([tuple(range(M-1,-1,-1)),tuple(N*M+b for b in range(M))])
  cloth=mesh(f'{i} continuous arched canvas',verts,faces,trailer,canvas)
  for p in cloth.data.polygons:p.use_smooth=True
  receipts.append({'truck':i,'removed_modern_cab_faces':len(remove),'crew_uv_loops_unchanged':len(crew_before),'roof_height':h,'canvas_vertices':len(verts)})
# Matching real light direction for any residual diffuse portions.
for o in bpy.data.objects:
 if o.type=='LIGHT' and o.data.type=='SUN':o.rotation_euler=(-light).to_track_quat('-Z','Y').to_euler();o.data.energy=1.2;o.data.angle=.12
for f in base:s.frame_set(f);assert pose()==base[f],f
s.frame_set(1);s.render.film_transparent=True;s.render.use_compositing=False
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
(P/'build-receipt.json').write_text(json.dumps({'source':'../fleet-clean-v13-2026-10-07/fleet-v13-clean.blend','geometry':receipts,'animated_roots_exact_at_frames':list(base),'illumination_vector':list(light),'scale_camera_routes_unchanged':True},indent=2))
