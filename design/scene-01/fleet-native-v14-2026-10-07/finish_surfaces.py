import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
metal=bpy.data.materials['V14 soft warm alloy'];trim=bpy.data.materials['V14 satin charcoal trim']
for n in metal.node_tree.nodes:
 if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and not n.inputs[1].is_linked:n.inputs[1].default_value=(.30,.38,.415,1)
removed={}
for i in range(1,5):
 root=bpy.data.objects[f'truck-{i}-tractor'];o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];t=root.matrix_world.inverted()@o.matrix_world
 bm=bmesh.new();bm.from_mesh(o.data);delete=[]
 for f in bm.faces:
  if f.material_index==1:continue
  p=sum((t@v.co for v in f.verts),Vector())/len(f.verts);x,y,z=p;rad=min(math.hypot(x-c,z-.35)for c in (.80,-1.35,-2.20))
  if rad<.405 and abs(y)>.35 and z<.80:delete.append(f)
 bmesh.ops.delete(bm,geom=delete,context='FACES');removed[i]=len(delete);bm.to_mesh(o.data);bm.free();o.data.update()
 for ob in root.children_recursive:
  if 'catwalk' in ob.name and ob.type=='MESH':
   for j in range(len(ob.data.materials)):ob.data.materials[j]=trim
 # The fifth-wheel table visibly connects cab chassis to the articulated trailer.
 bpy.ops.mesh.primitive_cube_add();ob=bpy.context.object;ob.name=f'V14 {i} fifth wheel support platform';ob.scale=(.54,.42,.045);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.parent=root;ob.location=(-1.70,0,1.105);ob.data.materials.append(trim)
 b=ob.modifiers.new('Rounded fifth wheel casting','BEVEL');b.width=.045;b.segments=3
 if i in (2,3):
  cargo=bpy.data.objects[f'{i} long semitrailer']
  for b in cargo.modifiers:
   if b.type=='BEVEL':b.width=.065;b.segments=4
  if not any(b.type=='BEVEL'for b in cargo.modifiers):
   b=cargo.modifiers.new('Rigid cargo rounded corners','BEVEL');b.width=.065;b.segments=4
  # Wide soft tonal drift over the panel: no discrete patches or added seam geometry.
  m=bpy.data.materials[f'V14 {i} painted body'];n=m.node_tree.nodes;l=m.node_tree.links
  mult=next(q for q in n if q.type=='MIX_RGB'and q.blend_type=='MULTIPLY'and not q.inputs[1].is_linked)
  base=mult.inputs[1].default_value[:];tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.2;tex.inputs['Detail'].default_value=0
  mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=tuple(v*.96 for v in base[:3])+(1,);mix.inputs[2].default_value=tuple(v*1.04 for v in base[:3])+(1,);l.new(tex.outputs['Fac'],mix.inputs[0]);l.new(mix.outputs[0],mult.inputs[1])
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
(P/'finish-receipt.json').write_text(json.dumps({'removed_original_broken_wheel_faces':removed,'new_wheels':'Same axle centers and near-identical radius, machined recessed rims and blue charcoal rubber','fifth_wheel_platform_center':[-1.70,0,1.105],'rigid_body_edge_radius':.065,'rigid_panel_tone_range':[.96,1.04]},indent=2))
