import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
S=P.parent/'fleet-video-v11-2026-10-07/fleet-v11-video.blend'
bpy.ops.wm.open_mainfile(filepath=str(S));s=bpy.context.scene
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')]
fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
flags={o.name:o.hide_render for o in s.objects}
def poses():return {o.name:[list(row) for row in o.matrix_world] for o in roots}
baseline={}
for f in (1,385,769,1152):s.frame_set(f);baseline[f]=poses()
cam=s.camera; cm=cam.matrix_world.copy(); ortho=cam.data.ortho_scale
s.render.film_transparent=True;s.render.use_compositing=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
s.render.resolution_percentage=100
for o in s.objects:
 if o.type in ('MESH','FONT','CURVE') and o not in fleet:o.hide_render=True

def render_close(version):
 s.frame_set(769);s.render.resolution_x=1200;s.render.resolution_y=900
 for i in range(1,5):
  tr=bpy.data.objects[f'truck-{i}-tractor'];tl=bpy.data.objects[f'truck-{i}-trailer']; own={tr,tl,*tr.children_recursive,*tl.children_recursive}
  for o in fleet:
   if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags.get(o.name,False) or o not in own
  target=tr.matrix_world@Vector((-.35,0,1.6));cam.location=tr.matrix_world@Vector((11,-8,7));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.7
  s.render.filepath=str(P/f'{version}-front-{i}.png');bpy.ops.render.render(write_still=True)
 for o in fleet:o.hide_render=flags.get(o.name,False)
 cam.matrix_world=cm;cam.data.ortho_scale=ortho
render_close('v11')

def ink(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
 geo=n.new('ShaderNodeNewGeometry'); dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.3,-.4,.85);l.new(geo.outputs['Normal'],dot.inputs[0])
 ramp=n.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=-1;ramp.inputs['To Min'].default_value=.70;ramp.inputs['To Max'].default_value=1;l.new(dot.outputs['Value'],ramp.inputs[0])
 mult=n.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[1].default_value=(*color,1);l.new(ramp.outputs[0],mult.inputs[2])
 e=n.new('ShaderNodeEmission');l.new(mult.outputs[0],e.inputs[0]);o=n.new('ShaderNodeOutputMaterial');l.new(e.outputs[0],o.inputs[0]);return m
palette={1:(.77,.19,.13),2:(.09,.43,.75),3:(.27,.61,.15),4:(.95,.64,.09)}
for i in range(1,5):
 m=bpy.data.materials[f'V09 {i} painted cab front roof near side'];n=m.node_tree.nodes;l=m.node_tree.links
 original=n['Image Texture.001'].outputs['Color'];pigment=n['Map Range'].outputs[0]
 bw=n.new('ShaderNodeRGBToBW');l.new(original,bw.inputs[0]);shade=n.new('ShaderNodeMapRange');shade.inputs['To Min'].default_value=.60;shade.inputs['To Max'].default_value=1.05;l.new(bw.outputs[0],shade.inputs[0])
 tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[1].default_value=(*palette[i],1);l.new(shade.outputs[0],tint.inputs[2])
 mix=n.new('ShaderNodeMixRGB');l.new(pigment,mix.inputs[0]);l.new(original,mix.inputs[1]);l.new(tint.outputs[0],mix.inputs[2])
 for key in ('Diffuse BSDF.001','Emission.001'):l.new(mix.outputs[0],n[key].inputs['Color'])
 sill=ink(f'V12 {i} bright sill',palette[i]);trim=ink(f'V12 {i} blue gray trim',(.26,.37,.43))
 for o in fleet:
  if hasattr(o.data,'materials'):
   for j,mat in enumerate(o.data.materials):
    if mat and mat.name==f'V09 {i} clean body colored lower sill':o.data.materials[j]=sill
    elif mat and mat.name==f'V09 {i} clean windshield slate trim':o.data.materials[j]=trim
 cargo=ink(f'V12 {i} '+('woven pale canvas' if i in (1,4) else 'clean porcelain cargo'),(.59,.68,.70) if i==1 else (.73,.77,.71) if i==4 else (.86,.91,.91))
 metal=ink(f'V12 {i} clean hardware',(.40,.52,.57));rubber=ink(f'V12 {i} rubber',(.16,.23,.27))
 for o in fleet:
  if hasattr(o.data,'materials'):
   for j,mat in enumerate(o.data.materials):
    if mat and mat.name==f'{i} clay cargo':o.data.materials[j]=cargo
    elif mat and mat.name==f'{i} metal form':o.data.materials[j]=metal
    elif mat and mat.name==f'{i} rubber form':o.data.materials[j]=rubber
 if i in (1,4):
  fold=ink(f'V12 {i} canvas fold',(.42,.53,.56));repair=ink(f'V12 {i} repair patch',(.28,.41,.47));seam=ink(f'V12 {i} linen stitches',(.87,.89,.80))
  for o in fleet:
   if o.name.startswith(f'V08 {i} softly folded'):o.data.materials.clear();o.data.materials.append(fold)
   if o.name.startswith(f'V08 {i} subdued canvas'):o.hide_render=True;flags[o.name]=True
  root=bpy.data.objects[f'truck-{i}-trailer']
  def cube(name,loc,scale,mat):
   bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name=name;o.parent=root;o.location=loc;o.scale=scale;o.data.materials.append(mat);fleet.add(o);flags[o.name]=False;return o
  for side in (-1,1):
   for j,x in enumerate((-4.9,-1.6)):
    z=2.4 if j==0 else 1.62;w=.62 if j==0 else .43;h=.36
    o=cube(f'V12 {i} stitched canvas repair {side} {j}',(x,side*.941,z),(w,.012,h),repair);o.rotation_euler[1]=.09 if j else -.06
    for k in range(7):
     for zz in (z-h+.06,z+h-.06):cube(f'V12 {i} visible stitch',(x-w+.10+k*(2*w-.2)/6,side*.962,zz),(.025,.014,.045),seam)
  # broad paint abrasions remain local to the lower colored sill; no dirt across windows.
  m=sill;n=m.node_tree.nodes;l=m.node_tree.links;e=next(x for x in n if x.type=='EMISSION');base=e.inputs[0].links[0].from_socket
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=10;tex.inputs['Detail'].default_value=1
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.56;ramp.color_ramp.elements[1].position=.65;l.new(tex.outputs['Fac'],ramp.inputs[0])
  scuff=n.new('ShaderNodeMixRGB');l.new(ramp.outputs[0],scuff.inputs[0]);l.new(base,scuff.inputs[1]);scuff.inputs[2].default_value=(.38,.45,.44,1);l.new(scuff.outputs[0],e.inputs[0])
for f in baseline:s.frame_set(f);assert poses()==baseline[f]
s.frame_set(1);cam.matrix_world=cm;cam.data.ortho_scale=ortho;s.render.resolution_x=1920;s.render.resolution_y=1334
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v12-style.blend'))
for f in (1,385,769):
 s.frame_set(f);s.render.filepath=str(P/f'vehicles-{f:04d}.png');bpy.ops.render.render(write_still=True)
render_close('v12')
(P/'receipt.json').write_text(json.dumps({'source':str(S),'pipeline':'Standard / None / exposure 0 / gamma 1; brightness corrected in material pigment and canvas, no global exposure change','root_transform_checks':list(baseline),'crew':'existing windshield materials untouched','changes':['cool pale canvas versus clean ivory rigid trailers','large stitched repairs only old red/yellow canvas','bright pigment-local cab palette','local lower sill abrasion on old trucks','lighter blue-gray trim and hardware'],'camera_preserved':True,'routes_and_coupling_preserved':True,'render_dimensions':[1920,1334]},indent=2))
