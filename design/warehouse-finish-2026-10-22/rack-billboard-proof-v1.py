import bpy,json,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';g=json.loads((R/'rack-geometry-preparation-v1.json').read_text());reg=json.loads((R/'rack-registration-v1.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'rack-open-cap-preparation-v1.blend'));s=bpy.context.scene;c=s.camera;W,H=1440,1000;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;A=reg['affine_native_to_source'];tx0,ty0,tx1,ty1=reg['native_alpha_bbox_192'];tw,th=reg['native_dimensions'];native=[(tx0,ty1),(tx1,ty1),(tx1,ty0),(tx0,ty0)];q=c.matrix_world.to_quaternion();right=q@Vector((1,0,0));up=q@Vector((0,1,0));normal=q@Vector((0,0,1));scale=c.data.ortho_scale/W
reference=Vector((2.4,4.1,1.35));p=world_to_camera_view(s,c,reference);reference_px=(p.x*W,(1-p.y)*H);verts=[];mapped=[]
# Camera-only sprite plane is lifted toward camera to avoid floor clipping.
# Original 3D boards/fonts remain intact; paired proof restores their exact source pixels.
reference+=normal*1.5
for x,y in native:
 sx=A[0][0]*x+A[0][1]*y+A[0][2];sy=A[1][0]*x+A[1][1]*y+A[1][2];mapped.append([sx,sy]);verts.append(reference+right*(sx-reference_px[0])*scale-up*(sy-reference_px[1])*scale)
mesh=bpy.data.meshes.new('rack proof affine card');mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.update();o=bpy.data.objects.new('rack illustrated proof card v1',mesh);bpy.data.collections['Illustration finishing'].objects.link(o);uv=mesh.uv_layers.new(name='UVMap');uvs=[(x/tw,1-y/th)for x,y in native]
for i,loop in enumerate(mesh.loops):uv.data[i].uv=uvs[loop.vertex_index]
m=bpy.data.materials.new('rack native illustration camera-only');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;out=n.new('ShaderNodeOutputMaterial');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'rack-sprite-v1-native.png'));tex.image.alpha_mode='STRAIGHT';em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=2**.25;l.new(tex.outputs['Color'],em.inputs['Color']);tr=n.new('ShaderNodeBsdfTransparent');cut=n.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=192/255;l.new(tex.outputs['Alpha'],cut.inputs[0]);ray=n.new('ShaderNodeLightPath');mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(cut.outputs[0],mul.inputs[0]);l.new(ray.outputs['Is Camera Ray'],mul.inputs[1]);mix=n.new('ShaderNodeMixShader');l.new(mul.outputs[0],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0]);mesh.materials.append(m)
for attr in ['visible_shadow','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter']:setattr(o,attr,False)
hidden=[]
for row in g['all_projected_corners']:
 name=row['object']
 if name.startswith('Plaque ') or name.endswith(' plaque'):continue
 bpy.data.objects[name].visible_camera=False;hidden.append(name)
x0,y0,x1,y1=g['source_crop_xyxy'];s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/W;s.render.border_max_x=x1/W;s.render.border_min_y=1-y1/H;s.render.border_max_y=1-y0/H;s.cycles.samples=16;s.cycles.seed=0;s.render.filepath=str(R/'rack-billboard-v1-native-render.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'rack-billboard-proof-v1.blend'));start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
# Exact fixed physical envelope projected corners, for no-disguise limit evidence.
env=[]
for x in [1.5,3.3]:
 for y in [3.5,4.7]:
  for z in [0,2.7]:
   v=world_to_camera_view(s,c,Vector((x,y,z)));env.append([v.x*W,(1-v.y)*H])
(R/'rack-billboard-v1.json').write_text(json.dumps({'status':'local stylistic comparison only; geometry gate pending residual evaluation','source_crop_xyxy':g['source_crop_xyxy'],'full_source_dimensions':[W,H],'mapped_card_source_corners':mapped,'world_card_corners':[list(v)for v in verts],'projected_physical_envelope_corners':env,'hidden_camera_only':hidden,'exact_3d_boards_and_fonts_retained':['А-Б plaque','В-К plaque','Plaque А-Б','Plaque В-К'],'original_shadow_casters_retained':True,'native_modified':False,'alpha_cutoff':192/255,'measured_crop_render_seconds':elapsed,'production_changed':False},ensure_ascii=False,indent=2));print('RACK_PROOF_SECONDS',elapsed)
