import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-finish-2026-10-22';R=ROOT/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-finish-v3.blend'));S=bpy.context.scene;cam=bpy.data.objects['FullSourceOverscan'];S.camera=cam
W,H=1440,1000
S.render.resolution_x=W;S.render.resolution_y=H;S.render.resolution_percentage=100
keeper=[o for o in bpy.data.objects if o.name.startswith('Finish keeper ')]
def px(p):
 v=world_to_camera_view(S,cam,Vector(p));return [v.x*W,(1-v.y)*H]
bpy.context.view_layer.update();head=Vector((9.8,2.3,1.76));feet=Vector((9.8,2.3,0));hp,fp=px(head),px(feet)
coords=[px(o.matrix_world@v.co) for o in keeper if o.type=='MESH' for v in o.data.vertices]
oldbounds=[min(v[0] for v in coords),min(v[1] for v in coords),max(v[0] for v in coords),max(v[1] for v in coords)]
# Small source-world proof region includes keeper, WMS, frame and rack edge.
region=[875,605,1125,805];x0,y0,x1,y1=region
S.render.use_border=True;S.render.use_crop_to_border=True;S.render.border_min_x=x0/W;S.render.border_max_x=x1/W;S.render.border_min_y=1-y1/H;S.render.border_max_y=1-y0/H
S.render.filepath=str(R/'keeper-v3-paired-render.png');bpy.ops.render.render(write_still=True)
# Camera-facing card projects exactly between the original physical z0 and z1.76 landmarks.
up=cam.matrix_world.to_quaternion()@Vector((0,1,0));right=cam.matrix_world.to_quaternion()@Vector((1,0,0));normal=cam.matrix_world.to_quaternion()@Vector((0,0,1))
height=abs((head-feet).dot(up));texbounds=[242,116,780,1459];tw,th=1024,1536;ratio=(780-242)/(1459-116);width=height*ratio
# Original centerline in the same camera-depth plane; no context warp or X/Y landmark changes.
center=(head+feet)/2
verts=[center-right*width/2-up*height/2,center+right*width/2-up*height/2,center+right*width/2+up*height/2,center-right*width/2+up*height/2]
mesh=bpy.data.meshes.new('Keeper illustration card');mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.update();o=bpy.data.objects.new('Keeper illustrated proof card',mesh);bpy.data.collections['Illustration finishing'].objects.link(o)
uv=mesh.uv_layers.new(name='UVMap');uvs=[(242/tw,1-1459/th),(780/tw,1-1459/th),(780/tw,1-116/th),(242/tw,1-116/th)]
for i,loop in enumerate(mesh.loops):uv.data[i].uv=uvs[loop.vertex_index]
mat=bpy.data.materials.new('Keeper native illustration camera-only');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links;out=n.new('ShaderNodeOutputMaterial');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'keeper-sprite-v1-native.png'),check_existing=True);tex.image.alpha_mode='STRAIGHT';tex.interpolation='Linear';em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=2**.25;l.new(tex.outputs['Color'],em.inputs['Color']);transparent=n.new('ShaderNodeBsdfTransparent')
# Native broad alpha glow is excluded by an explicit shader cutoff, without editing native pixels.
threshold=n.new('ShaderNodeMath');threshold.operation='GREATER_THAN';threshold.inputs[1].default_value=192/255;l.new(tex.outputs['Alpha'],threshold.inputs[0]);path=n.new('ShaderNodeLightPath');mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(threshold.outputs[0],mul.inputs[0]);l.new(path.outputs['Is Camera Ray'],mul.inputs[1]);mix=n.new('ShaderNodeMixShader');l.new(mul.outputs[0],mix.inputs[0]);l.new(transparent.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface']);mesh.materials.append(mat)
for attr in ['visible_shadow','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter']:setattr(o,attr,False)
for obj in keeper:obj.visible_camera=False # retain exactly the v3 shadow caster for every other ray
S.render.filepath=str(R/'keeper-v4-native-render.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'warehouse-keeper-proof-v4.blend'));bpy.ops.render.render(write_still=True)
projected=[px(v) for v in verts];bounds=[min(v[0] for v in projected),min(v[1] for v in projected),max(v[0] for v in projected),max(v[1] for v in projected)]
(R/'keeper-billboard-v4.json').write_text(json.dumps({'status':'local style proof only, not production','native_sprite':'keeper-sprite-v1-native.png','native_dimensions':[tw,th],'native_texture_bbox':texbounds,'alpha_cutoff':192/255,'alpha_policy':'Shader threshold only. Native pixels untouched. Camera-ray-only emission; original 3D keeper invisible to camera but retains shadow.','physical_head_world':list(head),'physical_feet_world':list(feet),'projected_head':hp,'projected_feet':fp,'original_keeper_projected_bounds':oldbounds,'billboard_projected_bounds':bounds,'billboard_world_dimensions':[width,height],'physical_landmark_height_m':1.76,'card_height_note':'Camera-facing plane height equals projection of physical 1.76m vertical, not 1.76m in camera-up direction. Prevents inflated projected scale.','source_crop_xyxy':region,'source_full_dimensions':[W,H],'original_geometry_moved':False},indent=2))
print('LOCAL KEEPER PROOF COMPLETE')
