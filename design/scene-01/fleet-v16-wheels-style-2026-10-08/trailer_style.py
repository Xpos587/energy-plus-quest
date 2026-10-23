"""Merge painted trailer treatment into finalized wheel source; preserve other art/animation."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
assert Path(bpy.data.filepath).name=='wheels-base.blend','Load finalized wheels-base.blend explicitly'
frames=(1,48,96,144,192);objects=list(s.objects);before={}
for f in frames:
 s.frame_set(f);bpy.context.view_layer.update();before[f]={o.name:o.matrix_world.copy() for o in objects}
image=bpy.data.images.load(str(P/'textures/trailer-painted-albedo-imagegen.png'),check_existing=True);image.colorspace_settings.name='sRGB';image.pack()
removed=[];assigned={};palettes={}
for i in (1,2,3,4):
 root=bpy.data.objects[f'truck-{i}-trailer'];oldname=f'V14 {i} '+('canvas pigment' if i in (1,4) else 'painted body');src=bpy.data.materials[oldname];mat=src.copy();mat.name=f'STYLE {i} coherent broad painted trailer';n=mat.node_tree.nodes;l=mat.node_tree.links
 base=n.get('Mix (Legacy)');palette=tuple(base.inputs['Color1'].default_value);palettes[i]=palette
 for link in list(base.inputs['Color1'].links):l.remove(link)
 # Continuous scalar field: equal blends ofXY/XZ/YZ samples, independent of face
 # normal. The SAME point on adjacent roof/side/end faces gets the SAME paint.
 tex=n.new('ShaderNodeTexCoord');tex.object=root
 scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.84/7.58,.84/2.10,.84/2.40);l.new(tex.outputs['Object'],scale.inputs[0])
 offset=n.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.08+6.84*.84/7.58,.08+1.05*.84/2.10,.08-.98*.84/2.40);l.new(scale.outputs[0],offset.inputs[0])
 separate=n.new('ShaderNodeSeparateXYZ');l.new(offset.outputs[0],separate.inputs[0]);samples=[]
 for a,b in (('X','Y'),('X','Z'),('Y','Z')):
  combine=n.new('ShaderNodeCombineXYZ');l.new(separate.outputs[a],combine.inputs['X']);l.new(separate.outputs[b],combine.inputs['Y']);img=n.new('ShaderNodeTexImage');img.image=image;img.extension='EXTEND';img.interpolation='Linear';l.new(combine.outputs[0],img.inputs['Vector']);bw=n.new('ShaderNodeRGBToBW');l.new(img.outputs['Color'],bw.inputs['Color']);samples.append(bw.outputs[0])
 add=n.new('ShaderNodeMath');add.operation='ADD';l.new(samples[0],add.inputs[0]);l.new(samples[1],add.inputs[1]);add2=n.new('ShaderNodeMath');add2.operation='ADD';l.new(add.outputs[0],add2.inputs[0]);l.new(samples[2],add2.inputs[1]);avg=n.new('ShaderNodeMath');avg.operation='MULTIPLY';avg.inputs[1].default_value=1/3;l.new(add2.outputs[0],avg.inputs[0])
 # Center the bright neutral image on1.0 instead of multiplying/darkening paint.
 variation=n.new('ShaderNodeMapRange');variation.clamp=True;variation.inputs['From Min'].default_value=.7117558;variation.inputs['From Max'].default_value=.7700027;variation.inputs['To Min'].default_value=.88;variation.inputs['To Max'].default_value=1.12;l.new(avg.outputs[0],variation.inputs['Value'])
 pigment=n.new('ShaderNodeMixRGB');pigment.blend_type='MULTIPLY';pigment.inputs[0].default_value=1;pigment.inputs[1].default_value=palette;l.new(variation.outputs[0],pigment.inputs[2]);l.new(pigment.outputs[0],base.inputs['Color1'])
 assigned[i]=[]
 for o in root.children_recursive:
  if o.type!='MESH' or o.hide_render:continue
  if i==3 and any(t in o.name for t in ('large fitted roof panel','integral panel divider','long clean roof edge')):
   o.hide_render=True;removed.append(o.name);continue
  material_names={m.name for m in o.data.materials if m}
  paint_materials={oldname,f'V15 {i} integral side joint pigment',f'V15 {i} clean colored structure',f'V15 {i} soft edge highlight'}
  if material_names & paint_materials:
   if o.data.users>1:o.data=o.data.copy()
   o.data.materials.clear();o.data.materials.append(mat);assigned[i].append(o.name)
maxerror=0
for f in frames:
 s.frame_set(f);bpy.context.view_layer.update()
 for o in objects:
  error=max(abs(x-y) for a,b in zip(o.matrix_world,before[f][o.name]) for x,y in zip(a,b));maxerror=max(maxerror,error);assert error<1e-7,(f,o.name,error)
s.frame_set(144);bpy.ops.wm.save_as_mainfile(filepath=str(P/'merged.blend'))
receipt={'source':'wheels-base.blend','image':'textures/trailer-painted-albedo-imagegen.png','image_packed':True,'base_linear_rgba_preserved':palettes,'paint_multiplier_bounds':[.88,1.12],'mapping':'continuous shared trailer-root scalar field: average imageXY/XZ/YZ; interior.08..92 sampling andEXTEND; no seam/tile assumption; same3Dpoint samepaint independent of face normal','assigned_trailer_objects':assigned,'hidden_mismatched_green_overlays':removed,'geometry_change':'only remove visibility of mismatched green roof slabs/side divider bars; continuous original box remains','all_source_world_matrix_max_error':maxerror,'frames_checked':frames,'protected':'cabs,crew,shake,smoke,routes,camera,wheelgeometry/animation unchanged','contact_shadows':'wheel-source radial contact planes rendered once in color; exclude WHEEL contact from broadSUNcaster pass'}
(P/'trailer-style-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
