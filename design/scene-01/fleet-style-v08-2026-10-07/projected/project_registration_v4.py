"""Fixed camera artwork UV projection onto preserved truck geometry; no billboards."""
import bpy,sys,json,math,time
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;source=P.parent/'fleet-v08-finished.blend';args=sys.argv[sys.argv.index('--')+1:];art=Path(args[0]);assert art.is_file()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
roots=sorted([o for o in s.objects if o.name.startswith('truck-')],key=lambda o:o.name)
def capture():
 samples=[]
 for f in range(1,1153):
  s.frame_set(f);samples.append([float(x) for o in roots for row in o.matrix_world for x in row])
 return samples
before=capture();mastercamera={'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'ortho':s.camera.data.ortho_scale};actions={o.name:o.animation_data.action.name if o.animation_data and o.animation_data.action else None for o in roots};s.frame_set(769)
root=bpy.data.objects['truck-3-tractor'];base=bpy.data.objects['V02 DETAILED 3 complete tractor'];canon=[v.co.copy() for v in base.data.vertices]
camloc=Vector((11,-8,7));center=Vector((.25,0,1.65));rotation=(center-camloc).to_track_quat('-Z','Y');camrot=rotation.to_matrix();view=(camloc-center).normalized();scale=6.5
# Local reference projection is permanent UV. Root/object matrices never enter render-time nodes.
base_local=base.matrix_local.copy();uvs=[]
for co in canon:
 local=base_local@co;q=camrot.transposed()@(local-camloc);uu=.5+q.x*root.scale.x/scale;vv=.5+q.y*root.scale.y/scale;uvs.append((uu*1.18-.076,vv*1.10-.066))
image=bpy.data.images.load(str(art));image.pack();records=[]
for i in range(1,5):
 ob=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];original_coords=[tuple(v.co) for v in ob.data.vertices];assert len(ob.data.vertices)==len(canon)
 active=ob.data.uv_layers.active_index;uv=ob.data.uv_layers.new(name='V09 fixed painted cab projection')
 for loop in ob.data.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
 ob.data.uv_layers.active_index=active
 m=ob.data.materials[0].copy();m.name=f'V09 {i} painted cab front roof near side';n=m.node_tree.nodes;l=m.node_tree.links;originalout=next(node for node in n if node.type=='OUTPUT_MATERIAL');base_shader=originalout.inputs['Surface'].links[0].from_socket
 u=n.new('ShaderNodeUVMap');u.uv_map=uv.name;tex=n.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND';l.new(u.outputs['UV'],tex.inputs['Vector'])
 # Shift only the green paint in the illustration. Grey grille, hardware and lights retain artwork color.
 sep=n.new('ShaderNodeSeparateColor');l.new(tex.outputs['Color'],sep.inputs[0]);subs=[]
 for channel in ['Red','Blue']:
  node=n.new('ShaderNodeMath');node.operation='SUBTRACT';l.new(sep.outputs['Green'],node.inputs[0]);l.new(sep.outputs[channel],node.inputs[1]);subs.append(node)
 minimum=n.new('ShaderNodeMath');minimum.operation='MINIMUM';l.new(subs[0].outputs[0],minimum.inputs[0]);l.new(subs[1].outputs[0],minimum.inputs[1]);mask=n.new('ShaderNodeMapRange');mask.inputs['From Min'].default_value=.012;mask.inputs['From Max'].default_value=.09;mask.clamp=True;l.new(minimum.outputs[0],mask.inputs['Value'])
 hue=n.new('ShaderNodeHueSaturation');hue.inputs['Hue'].default_value={1:.25,2:.805,3:.5,4:.37}[i];hue.inputs['Saturation'].default_value=1.12;l.new(tex.outputs['Color'],hue.inputs['Color']);mix=n.new('ShaderNodeMixRGB');l.new(mask.outputs[0],mix.inputs[0]);l.new(tex.outputs['Color'],mix.inputs[1]);l.new(hue.outputs[0],mix.inputs[2])
 d=n.new('ShaderNodeBsdfDiffuse');l.new(mix.outputs[0],d.inputs[0]);e=n.new('ShaderNodeEmission');e.inputs['Strength'].default_value=1.0;l.new(mix.outputs[0],e.inputs[0]);sh=n.new('ShaderNodeMixShader');sh.inputs[0].default_value=.95;l.new(d.outputs[0],sh.inputs[1]);l.new(e.outputs[0],sh.inputs[2]);alpha_mix=n.new('ShaderNodeMixShader');l.new(tex.outputs['Alpha'],alpha_mix.inputs[0]);l.new(base_shader,alpha_mix.inputs[1]);l.new(sh.outputs[0],alpha_mix.inputs[2]);l.new(alpha_mix.outputs[0],originalout.inputs['Surface'])
 idx=len(ob.data.materials);ob.data.materials.append(m)
 def clean_material(name,color):
  mm=bpy.data.materials.new(name);mm.use_nodes=True;nn=mm.node_tree.nodes;nn.clear();ee=nn.new('ShaderNodeEmission');ee.inputs[0].default_value=(*color,1);ee.inputs[1].default_value=.85;oo=nn.new('ShaderNodeOutputMaterial');mm.node_tree.links.new(ee.outputs[0],oo.inputs['Surface']);return mm
 trimidx=len(ob.data.materials);ob.data.materials.append(clean_material(f'V09 {i} clean windshield slate trim',(.14,.205,.235)))
 lowertrimidx=len(ob.data.materials);ob.data.materials.append(clean_material(f'V09 {i} clean body colored lower sill',{1:(.55,.16,.09),2:(.10,.35,.65),3:(.40,.59,.16),4:(.72,.50,.13)}[i]))
 assigned=0;excluded_driver=0;excluded_rear=0;trimcount=0;steelcount=0;normmat=base_local.to_3x3().inverted().transposed()
 for poly in ob.data.polygons:
  if poly.material_index!=0:excluded_driver+=1;continue
  verts=[canon[j] for j in poly.vertices];c=sum(verts,Vector())/len(verts)
  # Cab upper body plus front grille/bumper; explicit wheel/chassis/rear exclusion.
  cab=(c.x<-.30 and c.z>-.15) or (c.x<-.88 and c.z>-.46 and abs(c.y)<.45)
  facing=(normmat@poly.normal).normalized().dot(view)>.10
  window_margin=(c.x<-.90 and .0<c.z<.40)
  if cab and facing and not window_margin:poly.material_index=idx;assigned+=1
  elif window_margin and c.z<.09:poly.material_index=lowertrimidx;trimcount+=1
  elif window_margin and c.z>.31:poly.material_index=trimidx;trimcount+=1
  elif c.x>=-.30 or c.z<=-.15:excluded_rear+=1
 assert original_coords==[tuple(v.co) for v in ob.data.vertices]
 records.append({'truck':i,'painted_body_polygons':assigned,'clean_windshield_trim_polygons':trimcount,'clean_nontyre_rear_hardware_polygons':steelcount,'driver_material_polygons_excluded':excluded_driver,'rear_lower_region_polygons_excluded':excluded_rear,'uv':uv.name,'original_uv_active_index_preserved':active,'geometry_vertex_delta':0})
after=capture();delta=max(abs(x-y) for p,q in zip(before,after) for x,y in zip(p,q));assert delta==0
assert mastercamera=={'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'ortho':s.camera.data.ortho_scale}
s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
receipt={'source':str(source),'artwork':str(art),'projection_camera_local':{'location':list(camloc),'target':list(center),'ortho_scale':scale,'image_aspect':1},'records':records,'frames_verified':1152,'roots':8,'max_root_matrix_delta':delta,'geometry_delta':0,'camera_preserved':True,'actions':actions,'driver_slots':'Existing material slot1 unchanged; no image changes or UV overrides.','registration_fit':{'uv_u_scale':1.18,'uv_u_offset':-.076,'uv_v_scale':1.10,'uv_v_offset':-.066,'reason':'Generated painting expands cab right and downward; roof and frontal lower-body anchors fit back onto native geometry.'},'windshield_margin_exclusion':'Front x<-.90 and model z between0 and.40 upper brow gets clean slate, lower sill gets body pigment; center border retains original base. Generated paintedpeople never projected there.','method':'Matched canonical green mesh indices yield fixed per-loop cab UVs on each existing real mesh; subset visibility chosen in canonical object space. No image plane, no billboard, no runtime camera projection.','limitations':['Projection covers reference-visible front/near-side/roof only. Opposite sides retain original light shader.','Painted reflections are baked in canonical illustration; native geometry and object rotation remain real.'],'render_frames':[1,385,769]};(P/'projection-receipt.json').write_text(json.dumps(receipt,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-painted-projected-v09.blend'))
for f in (1,385,769):s.frame_set(f);s.render.filepath=str(P/f'vehicles-{f:04}.png');bpy.ops.render.render(write_still=True)
flags={o.name:o.hide_render for o in s.objects};fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
s.frame_set(769);cam=s.camera;s.render.resolution_x=1200;s.render.resolution_y=1200
for i in range(1,5):
 tractor=bpy.data.objects[f'truck-{i}-tractor'];trailer=bpy.data.objects[f'truck-{i}-trailer'];own={tractor,trailer};own.update(tractor.children_recursive);own.update(trailer.children_recursive)
 for o in s.objects:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags[o.name] or o not in own
 centerworld=tractor.matrix_world@center;cam.location=tractor.matrix_world@camloc;cam.rotation_euler=(centerworld-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(P/f'front-{i}.png');bpy.ops.render.render(write_still=True)
print('PROJECTION PILOT COMPLETE',flush=True)
