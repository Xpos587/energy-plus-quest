import bpy,math,bmesh,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-native-v14-2026-10-07/fleet-v14-native.blend'));s=bpy.context.scene;s.frame_set(1)
light=Vector((-40,35,70)).normalized()
def material(name,color):
 m=bpy.data.materials.new('V15 '+name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;g=n.new('ShaderNodeNewGeometry');d=n.new('ShaderNodeVectorMath');d.operation='DOT_PRODUCT';d.inputs[1].default_value=light;l.new(g.outputs['Normal'],d.inputs[0]);r=n.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=-1;r.inputs['To Min'].default_value=.72;r.inputs['To Max'].default_value=1.12;l.new(d.outputs['Value'],r.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=(*color,1);l.new(r.outputs[0],mix.inputs[2]);e=n.new('ShaderNodeEmission');l.new(mix.outputs[0],e.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(e.outputs[0],out.inputs[0]);return m
cream=material('warm light alloy',(.69,.73,.66));steel=material('blue slate mechanics',(.22,.31,.36));vent=material('vent cavities',(.10,.18,.22))
colors={1:(.70,.15,.095),2:(.05,.32,.73),3:(.28,.64,.11),4:(.99,.68,.105)}
def objmesh(name,vs,fs,parent,mat,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('V15 '+name,me);s.collection.objects.link(o);o.parent=parent;me.materials.append(mat)
 if len(fs)>1:
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 if bevel:
  b=o.modifiers.new('Integral rounded edge','BEVEL');b.width=bevel;b.segments=3;o.modifiers.new('Broad face normals','WEIGHTED_NORMAL')
 return o
def box(name,loc,dim,parent,mat,r=.025):
 x,y,z=loc;a,b,c=[q/2 for q in dim];v=[(x+dx*a,y+dy*b,z+dz*c)for dx,dy,dz in ((-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1))];return objmesh(name,v,[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)],parent,mat,r)
def rod(name,a,b,r,parent,mat):
 a=Vector(a);b=Vector(b);d=b-a;v=[];axis=d.normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.1:u=axis.cross(Vector((0,1,0)))
 u.normalize();w=axis.cross(u)
 for c in (a,b):
  for k in range(16):v.append(c+r*(math.cos(k*math.tau/16)*u+math.sin(k*math.tau/16)*w))
 faces=[tuple(range(15,-1,-1)),tuple(range(16,32))]+[(k,(k+1)%16,(k+1)%16+16,k+16)for k in range(16)];return objmesh(name,v,faces,parent,mat)
# Raise the cool shadow floor; keep saturated body colors and light metal accents.
for m in bpy.data.materials:
 if not m.use_nodes or not m.name.startswith('V14 '):continue
 for n in m.node_tree.nodes:
  if n.type=='VALTORGB':
   for e in n.color_ramp.elements:
    if e.position<.01:e.color=(.68,.77,.84,1)
    elif e.position<.5:e.color=(.84,.90,.93,1)
for i in range(1,5):
 tr=bpy.data.objects[f'truck-{i}-tractor'];tl=bpy.data.objects[f'truck-{i}-trailer'];paint=material(f'{i} clean colored structure',colors[i]);edge=material(f'{i} soft edge highlight',tuple(v*.65+.25 for v in colors[i]));shade=material(f'{i} recessed body joints',tuple(v*.60+.06 for v in colors[i]))
 # Keep clean mechanical silhouette, lighten alloy/fuel tanks rather than white scan textures.
 for o in tr.children_recursive:
  if any(k in o.name for k in ('clean fuel tank','alloy rim ring','central hub')):
   for j in range(len(o.data.materials)):o.data.materials[j]=cream
 if i in (1,4):
  cloth=bpy.data.objects[f'V14 {i} continuous arched canvas']
  for v in cloth.data.vertices:
   x,y,z=v.co;phase=(x+6.8)/(.84 if i==1 else 1.06);wave=math.sin(math.pi*phase)**2
   if z>3.02:v.co.z-=.095*wave
   elif abs(y)>.89:
    envelope=max(0,math.sin(math.pi*(z-1.07)/2.01));v.co.y+=math.copysign(.036*math.sin(phase*math.tau)*envelope,y)
  cloth.data.update()
  # Attached longitudinal roof seams lie on the arched cloth, not floating rectangular patches.
  for sy in (-1,1):
   y=sy*.68
   points=[]
   for k in range(91):
    x=-6.78+7.46*k/90;phase=(x+6.8)/(.84 if i==1 else 1.06);z=3.08+.18*(1-(y/.915)**2)+.012*math.sin(x*4)*(1-(y/.915)**2)-.095*math.sin(math.pi*phase)**2+.008;points.append((x,y,z))
   for k in range(90):rod(f'{i} sewn canvas roof joint {sy} {k}',points[k],points[k+1],.012,tl,edge)
  # Curtain ties follow the lower edge and terminate at the existing buckles.
  for x in [-6.4+j*.70 for j in range(11)]:
   for sy in (-1,1):rod(f'{i} attached curtain tie {x} {sy}',(x,sy*.94,1.12),(x+.06,sy*.944,1.38),.019,tl,cream)
  # Wear lives on exposed lip edges and door sill, not arbitrary dirty rectangles.
  for sy in (-1,1):
   y=sy*(.95 if i==1 else .90)
   for j,(x,length) in enumerate(((.44,.22),(1.13,.17),(1.43,.10))):rod(f'{i} rubbed rain gutter {sy} {j}',(x,y,2.15 if i==1 else 2.01),(x+length,y,2.15 if i==1 else 2.01),.017,tr,edge)
   rod(f'{i} worn door sill {sy}',(.23,y,1.08),(.57,y,1.08),.021,tr,edge)
  # A connected low-density volume rises from the actual exhaust tip.
  pipe=bpy.data.objects[f'{i} exhaust stack'];pts=[tr.matrix_world.inverted()@pipe.matrix_world@Vector(v)for v in pipe.bound_box];tip=Vector((pipe.location.x,pipe.location.y,max(v.z for v in pts)))
  smoke=bpy.data.materials.new(f'V15 {i} coherent exhaust volume');smoke.use_nodes=True;n=smoke.node_tree.nodes;n.clear();vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.43,.52,.57,1);vol.inputs['Density'].default_value=1.8;vol.inputs['Anisotropy'].default_value=.15;out=n.new('ShaderNodeOutputMaterial');smoke.node_tree.links.new(vol.outputs['Volume'],out.inputs['Volume'])
  vs=[];fs=[]
  for k in range(10):
   t=k/9;center=tip+Vector((-.48*t,.10*math.sin(t*3),.92*t));radius=.034+.16*math.sin(math.pi*t*.85)
   for a in range(16):ang=a*math.tau/16;vs.append(center+Vector((radius*math.cos(ang),radius*math.sin(ang),0)))
  for k in range(9):
   for a in range(16):q=k*16+a;fs.append((q,k*16+(a+1)%16,(k+1)*16+(a+1)%16,q+16))
  fs +=[tuple(range(15,-1,-1)),tuple(range(144,160))];objmesh(f'{i} connected exhaust plume',vs,fs,tr,smoke)
 else:
  # Cargo has actual framed side construction and formed roof, not a uniform color slab.
  for sy in (-1,1):
   for z in (1.18,3.12):box(f'{i} continuous box side edge {sy} {z}',(-3.05,sy*.928,z),(7.40,.055,.070),tl,edge,.025)
   for j,x in enumerate((-4.88,-2.48) if i==3 else (-5.53,-4.03,-2.53,-1.03)):
    box(f'{i} integral panel divider {sy} {j}',(x,sy*.936,2.15),(.065,.042,1.91),tl,edge,.015)
  if i==2:
   for j,x in enumerate([-6.5+k*.54 for k in range(14)]):box(f'2 pressed roof rib {j}',(x,0,3.286),(.072,1.72,.052),tl,edge,.024)
  else:
   for j,x in enumerate((-5.56,-3.06,-.56)):
    box(f'3 large fitted roof panel {j}',(x,0,3.283),(2.35,1.63,.052),tl,paint,.052)
   for y in (-.85,.85):box(f'3 long clean roof edge {y}',(-3.05,y,3.28),(7.38,.054,.065),tl,edge,.025)
 # Rear doors and hardware are visibly built into all cargo bodies.
 for sy in (-1,1):
  rod(f'{i} rear door locking rod {sy}',(-6.865,sy*.47,1.25),(-6.865,sy*.47,3.05),.025,tl,cream)
# Recognizable front-mounted reefer: pale rounded body, two fan recesses, integral support frame.
tl=bpy.data.objects['truck-2-trailer']
for o in tl.children_recursive:
 if o.name.startswith('V08 2 refrigeration') or o.name=='V08 2 vent recess':o.hide_render=True
box('2 mounted refrigeration housing',(.84,0,3.04),(.29,1.28,.72),tl,cream,.075)
for sy in (-1,1):
 rod(f'2 round refrigeration fan {sy}',(.992,sy*.32,3.08),(1.013,sy*.32,3.08),.205,tl,vent)
 for a in range(4):
  ang=a*math.pi/2;rod(f'2 fan blade {sy} {a}',(1.019,sy*.32+.05*math.cos(ang),3.08+.05*math.sin(ang)),(1.019,sy*.32+.166*math.cos(ang+.24),3.08+.166*math.sin(ang+.24)),.022,tl,steel)
 box(f'2 mounted support {sy}',(.78,sy*.50,2.63),(.18,.10,.22),tl,steel,.015)
box('2 cooling lower vent',(.995,0,2.78),(.035,.83,.075),tl,steel,.012)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v15-readable.blend'))
(P/'build-receipt.json').write_text(json.dumps({'source':'../fleet-native-v14-2026-10-07/fleet-v14-native.blend','changes':['continuous draped canvas roofs and attached ties','localized exposed-edge wear','connected volumetric exhaust from true pipe tip','blue ribbed rigid roof and twin-fan mounted reefer','green broad fitted roof panels and side construction','light alloy hubs/tanks and higher shadow floor'],'preserved':['crew','root animation','map camera','fleet scale']},indent=2))
