import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parent
SOURCE=P.parent/'fleet-exhaust-v17-2026-10-08/fleet-v17-exhaust.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(1)
baseline={o.name: {'hide':o.hide_render,'matrix':[list(r) for r in o.matrix_world],'vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in bpy.data.objects}
with bpy.data.libraries.load(str(P/'maz500-isolated-study.blend'),link=False) as (a,b):
 b.objects=[name for name in a.objects if name.startswith('Object_')]
sources=b.objects
source_matrices={o['name']:Matrix(o['matrix_world']) for o in json.loads((P/'asset-inspection.json').read_text())['objects']}
col=bpy.data.collections.new('V18 old civilian cab replacements');s.collection.children.link(col)

def material(name,color,wear=False):
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
 out=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');l.new(e.outputs[0],out.inputs['Surface'])
 geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.35,-.45,.82);l.new(geo.outputs['Normal'],dot.inputs[0])
 shade=n.new('ShaderNodeMapRange');shade.inputs['From Min'].default_value=-1;shade.inputs['From Max'].default_value=1;shade.inputs['To Min'].default_value=.48;shade.inputs['To Max'].default_value=1.04;l.new(dot.outputs['Value'],shade.inputs[0])
 rgb=n.new('ShaderNodeRGB');rgb.outputs[0].default_value=color;socket=rgb.outputs[0]
 if wear:
  tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=34;noise.inputs['Detail'].default_value=2;l.new(tc.outputs['Generated'],noise.inputs['Vector'])
  ramp=n.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=.66;ramp.inputs['From Max'].default_value=.88;ramp.inputs['To Max'].default_value=.22;l.new(noise.outputs['Fac'],ramp.inputs[0])
  mix=n.new('ShaderNodeMixRGB');mix.inputs[2].default_value=tuple(v*.7+.10 for v in color[:3])+(1,);l.new(socket,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[0]);socket=mix.outputs[0]
 mult=n.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;l.new(socket,mult.inputs[1]);l.new(shade.outputs[0],mult.inputs[2]);l.new(mult.outputs[0],e.inputs[0]);return m

trim=material('V18 soft slate trim',(.13,.18,.23,1));silver=material('V18 pale metal',(.52,.61,.67,1));glass=material('V18 blue side glass',(.13,.33,.46,1));lamp=material('V18 pale round headlamp',(.85,.85,.65,1));amber=material('V18 amber lamp',(.82,.40,.055,1))
crew=bpy.data.materials.new('V18 one driver across two real windshield panes');crew.use_nodes=True;n=crew.node_tree.nodes;n.clear();tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(P.parent/'fleet-style-v08-2026-10-07/textures/single-illustrated-shared-driver.png'),check_existing=True);e=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');crew.node_tree.links.new(tex.outputs['Color'],e.inputs[0]);crew.node_tree.links.new(e.outputs[0],out.inputs[0])
report=[];modified=[]
for truck,color in [(1,(.65,.095,.045,1)),(4,(.88,.54,.06,1))]:
 root=bpy.data.objects[f'truck-{truck}-tractor'];old=bpy.data.objects[f'V02 DETAILED {truck} complete tractor'];old.hide_render=True;modified.append(old.name)
 for o in root.children_recursive:
  if o.name.startswith(f'V09 CLEAN {truck} ') or o.name==f'V14 {truck} seated lower windshield gasket' or (o.name.startswith(f'V14 {truck} ') and 'rolled wheel arch' in o.name):o.hide_render=True;modified.append(o.name)
 paint=material(f'V18 {truck} aged bright paint',color,True)
 for src in sources:
  idx=int(src.name.split('_')[1].split('.')[0]);world=[source_matrices[f'Object_{idx}']@v.co for v in src.data.vertices]
  faces=[];front=[]
  for f in src.data.polygons:
   ps=[world[k] for k in f.vertices];c=sum(ps,Vector())/len(ps)
   if any(p.x> -2.78 for p in ps):continue
   if idx in (5,6,7,8,9) and not all(p.z>1.68 for p in ps):continue
   if idx in (16,17,18,19) and not (all(p.z>1.65 for p in ps) or all(p.x< -4.85 for p in ps)):continue
   if idx in (10,) and not (all(p.z>1.68 for p in ps) or all(p.x< -4.85 for p in ps)):continue
   if idx in (12,13) and c.x< -5.10 and abs(c.y)<.32 and 2.2<c.z<2.5:continue
   faces.append(list(f.vertices));front.append(idx==15 and max(p.x for p in ps)<-4.60 and max(abs(p.y) for p in ps)<1.16)
  if not faces:continue
  verts=[(-.64*(p.x+3.80)+.80,-.64*p.y,.64*(p.z-.893)+.355) for p in world]
  mesh=bpy.data.meshes.new(f'V18 cab {truck} source {idx}');mesh.from_pydata(verts,[],faces);mesh.update()
  o=bpy.data.objects.new(f'V18 {truck} MAZ cab part {idx}',mesh);col.objects.link(o);o.parent=root
  m=paint if idx in (3,4) else silver if idx in (2,12,13,16,17) else amber if idx==11 else lamp if idx==14 else glass if idx==15 else trim
  mesh.materials.append(m);mesh.materials.append(crew)
  uv=mesh.uv_layers.new(name='UVMap')
  for f,is_front in zip(mesh.polygons,front):
   f.use_smooth=True
   if is_front:f.material_index=1
   for li in f.loop_indices:
    p=world[mesh.loops[li].vertex_index];uv.data[li].uv=((p.y+1.14933)/2.29866,(p.z-2.5333)/.61165)
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(mesh);bm.free();mesh.update()
  report.append({'truck':truck,'part':idx,'polygons':len(faces),'driver_panel_faces':sum(front)})
for src in sources:bpy.data.objects.remove(src,do_unlink=True)
# Exact scene invariants, excluding the intentionally hidden old-cab objects.
unchanged=[];errors=[]
for name,data in baseline.items():
 o=bpy.data.objects.get(name)
 if not o:errors.append('missing '+name);continue
 if [list(r) for r in o.matrix_world]!=data['matrix']:errors.append('matrix '+name)
 if name not in modified and o.hide_render!=data['hide']:errors.append('visibility '+name)
 if o.type=='MESH' and len(o.data.vertices)!=data['vertices']:errors.append('mesh '+name)
assert not errors,errors
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v18-old-cabs.blend'))
(P/'integration-receipt.json').write_text(json.dumps({'source':str(SOURCE),'parts':report,'hidden_old_cab_objects':modified,'baseline_object_matrices_mesh_vertex_counts_and_other_visibility_unchanged':True,'existing_driver_image_reprojected_onto_actual_split_glass':True,'source_to_root_transform':'x=-0.64*(x+3.80)+0.80; y=-0.64*y; z=0.64*(z-0.893)+0.355','geometry_validation_errors':errors},indent=2))
