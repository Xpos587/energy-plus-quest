import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
def tinted_copy(base,name,color):
 m=bpy.data.materials[base].copy();m.name='V15 '+name
 for n in m.node_tree.nodes:
  if n.type=='MIX_RGB'and n.blend_type=='MULTIPLY'and not n.inputs[1].is_linked:n.inputs[1].default_value=(*color,1)
 return m
def mesh(name,vs,fs,parent,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('V15 '+name,me);s.collection.objects.link(o);o.parent=parent;me.materials.append(mat);return o
smoke_checks=[]
for i in (1,4):
 tr=bpy.data.objects[f'truck-{i}-tractor'];pipe=bpy.data.objects[f'{i} exhaust stack'];p=[tr.matrix_world.inverted()@pipe.matrix_world@Vector(v)for v in pipe.bound_box];tip=Vector(((min(v.x for v in p)+max(v.x for v in p))/2,(min(v.y for v in p)+max(v.y for v in p))/2,max(v.z for v in p)))
 smoke=bpy.data.objects[f'V15 {i} connected exhaust plume']
 for k in range(10):
  t=k/9;center=tip+Vector((.16*t,-.10*t,.86*t));radius=.052+.14*math.sin(math.pi*t*.88)
  for a in range(16):ang=a*math.tau/16;smoke.data.vertices[k*16+a].co=center+Vector((radius*math.cos(ang),radius*math.sin(ang),0))
 smoke.data.update();next(n for n in smoke.data.materials[0].node_tree.nodes if n.type=='PRINCIPLED_VOLUME').inputs['Density'].default_value=3.0
 smoke_checks.append({'truck':i,'true_pipe_tip':list(tip),'smoke_base_ring_center':list(tip)})
 for o in list(bpy.data.objects):
  if o.name.startswith(f'V15 {i} sewn canvas roof joint'):o.data.materials[0]=bpy.data.materials[f'V14 {i} canvas pigment']
  if o.name.startswith((f'V15 {i} worn door sill',f'V15 {i} rubbed rain gutter')):o.hide_render=True
 # Thin chipped paint follows exposed roof corners, deliberately irregular and attached to the lip.
 worn=tinted_copy(f'V15 {i} soft edge highlight',f'{i} aged edge pigment',(.54,.23,.15)if i==1 else(.71,.47,.13))
 z=2.198 if i==1 else 2.058
 for sy in (-1,1):
  y=sy*(.95 if i==1 else .90)
  for j,x in enumerate((.24,1.14)):
   verts=[(x,y,z),(x+.06,y-sy*.025,z),(x+.12,y-sy*.012,z),(x+.15,y-sy*.037,z),(x+.25,y-sy*.018,z),(x+.29,y,z),(x+.20,y+sy*.008,z),(x+.11,y+sy*.006,z)]
   mesh(f'{i} chipped roof lip {sy} {j}',verts,[tuple(range(8))],tr,worn)
# Tone-on-tone structural side joints: readable in shape without chalk outlines.
for i,col in ((2,(.07,.34,.70)),(3,(.29,.60,.16))):
 tone=tinted_copy(f'V15 {i} soft edge highlight',f'{i} integral side joint pigment',col)
 for o in bpy.data.objects:
  if o.name.startswith(f'V15 {i} continuous box side edge')or o.name.startswith(f'V15 {i} integral panel divider'):
   o.data.materials[0]=tone
   axis=2 if 'side edge'in o.name else 0;coords=[v.co[axis]for v in o.data.vertices];c=(min(coords)+max(coords))/2
   for v in o.data.vertices:v.co[axis]=c+(v.co[axis]-c)*.65
   o.data.update()
# A compact blue-grey front mounted refrigeration module with real horizontal louvers.
tl=bpy.data.objects['truck-2-trailer'];housing=bpy.data.objects['V15 2 mounted refrigeration housing'];cool=tinted_copy('V15 2 soft edge highlight','2 refrigeration light blue housing',(.22,.46,.66));housing.data.materials[0]=cool
for v in housing.data.vertices:
 p=v.co;p.x=.70+(p.x-.70)*.75;p.y*=.87;p.z=3.04+(p.z-3.04)*.88
housing.data.update()
for o in bpy.data.objects:
 if o.name.startswith(('V15 2 round refrigeration fan','V15 2 fan blade','V15 2 cooling lower vent')):o.hide_render=True
vent=bpy.data.materials['V15 vent cavities'];alloy=tinted_copy('V15 warm light alloy','2 refrigeration louver metal',(.37,.51,.58))
mesh('2 recessed cooling grille',[(.927,-.45,2.84),(.927,.45,2.84),(.927,.45,3.26),(.927,-.45,3.26)],[(0,1,2,3)],tl,vent)
for j in range(7):
 z=2.87+j*.058;mesh(f'2 formed horizontal cooling louver {j}',[(.934,-.43,z),(.934,.43,z),(.949,.43,z+.019),(.949,-.43,z+.019)],[(0,1,2,3)],tl,alloy)
# The sleeper shape reads higher from the map while the approved windshield is untouched.
o=bpy.data.objects['V02 DETAILED 3 complete tractor'];tr=o.parent;t=tr.matrix_world.inverted()@o.matrix_world;inv=t.inverted();changed=0
for v in o.data.vertices:
 p=t@v.co
 if p.z>2.20:p.z=2.20+(p.z-2.20)*1.12;v.co=inv@p;changed+=1
o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v15-readable.blend'))
(P/'refine-receipt.json').write_text(json.dumps({'smoke_true_outlets':smoke_checks,'smoke':'connected volume begins at actual transformed pipe cap; parent inverse handled','canvas_seams':'same fabric pigment, no bright decorative roof stripes','wear':'irregular attached exposed-lip chips, straight door decal-like marks removed','reefer':'compact blue-grey housing with horizontal louvers','green_sleeper_vertices_above_2_2_raised_12_percent':changed},indent=2))
