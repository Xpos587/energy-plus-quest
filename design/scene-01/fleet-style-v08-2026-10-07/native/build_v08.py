import bpy,json,math,time
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent
source=O.parents[1]/'whole-map-v06-2026-10-06/fleet/fleet-textured-v07.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
roots=sorted([o for o in s.objects if o.name.startswith('truck-')],key=lambda o:o.name)
def poses():
 out=[]
 for f in range(1,1153):
  s.frame_set(f);out.append([float(x) for o in roots for row in o.matrix_world for x in row])
 return out
before=poses();camera={'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'scale':s.camera.data.ortho_scale};actions={o.name:o.animation_data.action.name if o.animation_data and o.animation_data.action else None for o in roots};s.frame_set(1)
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();d=n.new('ShaderNodeBsdfDiffuse');d.inputs['Color'].default_value=(*color,1);d.inputs['Roughness'].default_value=1;e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1);e.inputs['Strength'].default_value=.8;mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.38;o=n.new('ShaderNodeOutputMaterial');l=m.node_tree.links;l.new(d.outputs[0],mix.inputs[1]);l.new(e.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],o.inputs['Surface']);return m
def box(name,root,loc,dims,material,bevel=.08):
 bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name='V08 '+name;o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o.location=loc;o.scale=[d/2 for d in dims];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:b=o.modifiers.new('Soft manufactured edges','BEVEL');b.width=bevel;b.segments=3;o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
colors={1:(.69,.22,.13),2:(.10,.40,.72),3:(.36,.59,.19),4:(.84,.59,.17)}
roof=[]
for i in range(1,5):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];m=o.data.materials[0];n=m.node_tree.nodes
 # Preserve detailed cab mesh and original body mask, replace near-black contour by a light slate palette.
 neutral=n['Mix (Legacy)'];neutral.inputs[0].default_value=.78;neutral.inputs[2].default_value=(.115,.18,.22,1)
 n['Mix (Legacy).001'].inputs[2].default_value=(*colors[i],1);n['Mix Shader'].inputs[0].default_value=.46
 # No dirty noise, metallic highlights, normal maps or black ink treatment.
 # Yellow older vehicle has an identifiable modest raised roof/hatch; red stays the lowest.
 count=0
 if i==4:
  for v in o.data.vertices:
   if v.co.z>.33 and v.co.x<-.30:v.co.z+=.065;count+=1
  o.data.update()
 roof.append({'truck':i,'upper_roof_vertices_raised':count,'raise_model_z':.065 if i==4 else 0})
# Common illustrated hardware. Drivers remain original packed pixels, intentionally for parent finishing.
metal=mat('V08 cool pale hardware',(.29,.38,.41));rubber=mat('V08 soft charcoal tyres',(.075,.11,.13));ivory=mat('V08 reefer ivory',(.86,.88,.82));vent=mat('V08 reefer recessed vents',(.30,.40,.43));redcloth=mat('V08 red worn canvas',(.54,.44,.30));yellowcloth=mat('V08 yellow lightly aged canvas',(.70,.62,.45));redfold=mat('V08 red broad seam folds',(.47,.39,.28));yellowfold=mat('V08 yellow broad seam folds',(.64,.56,.41));redwear=mat('V08 red gentle wear',(.59,.49,.35));yellowwear=mat('V08 yellow gentle wear',(.75,.67,.50))
for i in range(1,5):
 for o in bpy.data.objects[f'truck-{i}-trailer'].children_recursive:
  if o.type!='MESH':continue
  for slot in o.material_slots:
   if not slot.material:continue
   name=slot.material.name
   if 'rubber form' in name:slot.material=rubber
   elif 'metal form' in name:slot.material=metal
   elif 'clay cargo' in name:slot.material=redcloth if i==1 else yellowcloth if i==4 else ivory
 # Fifth-wheel catwalk occupies rear chassis deck only; hitch point/tyres remain untouched.
 box(f'{i} rear chassis catwalk',bpy.data.objects[f'truck-{i}-tractor'],(-1.62,0,1.13),(1.05,1.46,.10),metal,.04)
# Weathered curtain: broad seams, asymmetric moderate wear patches. No cargo symbols.
for i in (1,4):
 root=bpy.data.objects[f'truck-{i}-trailer'];fold=redfold if i==1 else yellowfold;wear=redwear if i==1 else yellowwear
 for side in (-1,1):
  for j in range(10):
   x=-6.7+j*.78
   vs=[(x+.025*math.sin(k*.8),side*1.027,.96+k*.38) for k in range(7)]+[(x+.045+.025*math.sin(k*.8),side*1.028,.96+k*.38) for k in range(7)]
   faces=[(k,k+1,k+8,k+7) for k in range(6)];me=bpy.data.meshes.new(f'V08 {i} curtain seam mesh');me.from_pydata(vs,[],faces);me.materials.append(fold);ob=bpy.data.objects.new(f'V08 {i} softly folded canvas seam {side} {j}',me);s.collection.objects.link(ob);ob.parent=root
  for j in range(3 if i==1 else 1):
   x=-5.7+j*2.0;z=1.30+.14*(j%2)
   vs=[(x,side*1.029,z),(x+.7,side*1.029,z+.05),(x+.66,side*1.029,z+.22),(x+.04,side*1.029,z+.17)];me=bpy.data.meshes.new('broad canvas aging');me.from_pydata(vs,[],[(0,1,2,3)]);me.materials.append(wear);ob=bpy.data.objects.new(f'V08 {i} subdued canvas wear {side} {j}',me);s.collection.objects.link(ob);ob.parent=root
# Blue refrigeration unit, mounted on actual front face of smooth reefer trailer.
r=bpy.data.objects['truck-2-trailer'];box('2 refrigeration housing',r,(1.27,0,2.64),(.42,1.30,1.08),ivory,.13);box('2 vent recess',r,(1.50,0,2.63),(.032,1.01,.58),vent,.025)
for j in range(6):box(f'2 refrigeration vent louver {j}',r,(1.535,0,2.39+j*.09),(.05,1.01,.035),ivory,.009)
box('2 refrigeration lower control panel',r,(1.51,.37,2.17),(.045,.22,.16),metal,.025)
# Yellow's old flat roof uses a discrete hatch, lower than either modern sleeper roof.
yellowroot=bpy.data.objects['truck-4-tractor'];box('4 older rectangular roof hatch',yellowroot,(1.13,0,2.74),(.58,.54,.075),metal,.04)
# Red retains upright original exhaust; yellow exhaust lowered locally.
stack=bpy.data.objects.get('4 exhaust stack')
if stack:stack.scale.z*=.78;stack.location.z-=.13
# Adjust lights to airy diffuse shading without outlines.
for light in [o for o in s.objects if o.type=='LIGHT']:
 if light.data.type=='AREA':light.data.size=max(light.data.size,18)
fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');crypto.matte_id=', '.join(o.name for o in fleet if o.type in ('MESH','FONT') and not o.hide_render)
after=poses();delta=max(abs(a-b) for p,q in zip(before,after) for a,b in zip(p,q));assert delta==0
s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
receipt={'source':str(source),'frames_verified':1152,'root_count':len(roots),'max_root_matrix_delta':delta,'actions':actions,'camera':camera,'shape_records':roof,'shape_changes':['Original detailed tractor retained. Yellow older roof raised .065 model units only above .33, red remains lower.','Blue front refrigeration unit with recessed six-louver face and small control panel.','Red canvas 10 broad folds per side + 3 subdued worn patches; yellow 10 folds + 1 patch per side.','Local rear chassis catwalk fills skeletal deck; rear hitch and root transforms unchanged.','Yellow discrete roof hatch and lowered original exhaust. Green high sleeper/2-driver windshield unchanged.'],'material_changes':['Neutral cab ink .016/.022/.026 replaced .115/.18/.22, blend .78 retains only 22 percent original atlas detail.','Cab pigment updated warm red, blue, green, ochre; diffuse/emission mix .46, no metallic specular.','Trailers/hardware use diffuse-emission with 38 percent fill, pale metal and charcoal rubber; old canvas warm beige, modern ivory.','Area lights minimum size18 for soft shadows.'],'driver_images':'Unmodified packed source; parent owns texture finishing','contact_tyres':'No wheel mesh vertices changed; detailed cab contact/rear zones unchanged.','hitch':'No source objects or rig roots moved; catwalk is new child geometry','render_frames':[1,385,769],'resolution':[1920,1334]}
(O/'v08-native-receipt.json').write_text(json.dumps(receipt,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'fleet-illustrated-v08.blend'))
for f in (1,385,769):
 s.frame_set(f);s.render.filepath=str(O/f'fleet-v08-{f:04}.png');t=time.perf_counter();bpy.ops.render.render(write_still=True);print('RENDER SECONDS',f,time.perf_counter()-t,flush=True)
# Native front QA only. Camera edits never saved over master.
for o in s.objects:
 if o.type in ('MESH','FONT','CURVE') and o not in fleet:o.hide_render=True
s.frame_set(769);cam=s.camera;s.render.resolution_x=900;s.render.resolution_y=900
for i in range(1,5):
 target=bpy.data.objects[f'truck-{i}-tractor'];own=set([target,bpy.data.objects[f'truck-{i}-trailer']]);own.update(target.children_recursive);own.update(bpy.data.objects[f'truck-{i}-trailer'].children_recursive)
 for o in fleet:
  if o.type in ('MESH','FONT','CURVE') and o not in own:o.hide_render=True
 center=target.matrix_world@Vector((.25,0,1.65));cam.location=target.matrix_world@Vector((11,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.5;s.render.filepath=str(O/f'front-{i}.png');bpy.ops.render.render(write_still=True)
 for o in fleet:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=(o.name in [])
 # Restore render flags exactly from master before next isolate.
 for ob in bpy.data.objects:
  if ob.name.startswith('V02') or ob.name.startswith('V08'):continue
  if ob in fleet and ob.type in ('MESH','FONT','CURVE'):
   inventory=json.loads((O/'source-inventory.json').read_text());flags={x['name']:x['hide_render'] for x in inventory['objects']};ob.hide_render=flags.get(ob.name,ob.hide_render)
print('V08 COMPLETE',flush=True)
