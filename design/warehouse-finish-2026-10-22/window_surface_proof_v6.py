import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-finish-2026-10-22';R=ROOT/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-keeper-proof-v5.blend'));S=bpy.context.scene;cam=bpy.data.objects['FullSourceOverscan'];S.camera=cam;W,H=1440,1000;S.render.resolution_x=W;S.render.resolution_y=H
windows=sorted([o for o in bpy.data.objects if o.name.startswith('Finish window glass')],key=lambda o:o.location.x)
def points(o):
 return [[(p:=world_to_camera_view(S,cam,o.matrix_world@v.co)).x*W,(1-p.y)*H] for v in o.data.vertices]
bpy.context.view_layer.update();before={o.name:{'matrix':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices]} for o in bpy.data.objects if o.type=='MESH'}
p=points(windows[0]);xs=[v[0] for v in p];ys=[v[1] for v in p];region=[math.floor(min(xs))-32,math.floor(min(ys))-30,math.ceil(max(xs))+32,math.ceil(max(ys))+30];x0,y0,x1,y1=region
S.render.use_border=True;S.render.use_crop_to_border=True;S.render.border_min_x=x0/W;S.render.border_max_x=x1/W;S.render.border_min_y=1-y1/H;S.render.border_max_y=1-y0/H
S.render.filepath=str(R/'window-v5-paired-render.png');bpy.ops.render.render(write_still=True)
image=bpy.data.images.load(str(R/'window-view-texture-v1-native.png'),check_existing=True);image.colorspace_settings.name='sRGB';mappings=[]
for i,o in enumerate(windows):
 uv=o.data.uv_layers.new(name='Window painted view')
 # UVs are additive attributes; original physical vertices/transforms stay unchanged.
 for loop in o.data.loops:
  v=o.data.vertices[loop.vertex_index].co;u=v.x/1.8+.5;vv=v.z/1.97+.5
  if i%2:u=1-u
  uv.data[loop.index].uv=(u,vv)
 mat=bpy.data.materials.new('Window illustrated view '+str(i+1));mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links;out=n.new('ShaderNodeOutputMaterial');tex=n.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear';uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map=uv.name;l.new(uvnode.outputs['UV'],tex.inputs['Vector']);diff=n.new('ShaderNodeBsdfDiffuse');diff.inputs['Roughness'].default_value=.7;l.new(tex.outputs['Color'],diff.inputs['Color']);em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1.05;l.new(tex.outputs['Color'],em.inputs['Color']);mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.72;l.new(diff.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface']);o.data.materials.clear();o.data.materials.append(mat)
 mappings.append({'object':o.name,'position':list(o.location),'dimensions':list(o.dimensions),'mirror_u':bool(i%2),'projected_vertices':points(o),'uv_layer':uv.name})
hidden=[]
for o in bpy.data.objects:
 if o.name.startswith(('Finish distant foliage','Finish window sky top','Finish window horizon')):o.visible_camera=False;hidden.append(o.name)
changed=[]
for name,data in before.items():
 o=bpy.data.objects[name]
 if [list(r) for r in o.matrix_world]!=data['matrix'] or [list(v.co) for v in o.data.vertices]!=data['vertices']:changed.append(name)
assert not changed,changed
S.render.filepath=str(R/'window-v6-native-render.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'warehouse-window-proof-v6.blend'));bpy.ops.render.render(write_still=True)
(R/'window-surface-v6.json').write_text(json.dumps({'status':'window-only local surface proof, not production','source_scene':'warehouse-keeper-proof-v5.blend','candidate_scene':'warehouse-window-proof-v6.blend','texture_native':'window-view-texture-v1-native.png','native_texture_edited':False,'window_count':len(windows),'windows':mappings,'source_crop_xyxy':region,'source_dimensions':[W,H],'camera_hidden_fake_surface_objects':hidden,'original_mesh_objects_checked':len(before),'geometry_or_transform_changes':changed,'frame_mullion_sill_wall_moved':False,'shading':'72% emission at1.05 strength +28% rough diffuse; same physical glass panel meshes. No window invented. Keeper billboard proof retained.'},indent=2));print('WINDOW V6 LOCAL PROOF COMPLETE')
