import bpy,json,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';g=json.loads((R/'rack-geometry-preparation-v1.json').read_text());reg=json.loads((R/'rack-registration-v1.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'rack-open-cap-preparation-v1.blend'));s=bpy.context.scene;c=s.camera;W,H=1440,1000;before={o.name:([list(v.co)for v in o.data.vertices],[list(x)for x in o.matrix_world])for o in bpy.data.objects if o.type=='MESH'};cams={o.name:([list(x)for x in o.matrix_world],o.data.ortho_scale)for o in bpy.data.objects if o.type=='CAMERA'};uvanchors={x['name']:x['native_xy']for x in reg['anchor_residuals']};tw,th=reg['native_dimensions'];texture=bpy.data.images.load(str(R/'rack-sprite-v1-native.png'));texture.alpha_mode='STRAIGHT'
m=bpy.data.materials.new('rack-worldplane-v1 immutable texture camera surface');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;out=n.new('ShaderNodeOutputMaterial');tex=n.new('ShaderNodeTexImage');tex.image=texture;tex.interpolation='Linear';em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=2**.25;l.new(tex.outputs['Color'],em.inputs['Color']);tr=n.new('ShaderNodeBsdfTransparent');cut=n.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=192/255;l.new(tex.outputs['Alpha'],cut.inputs[0]);ray=n.new('ShaderNodeLightPath');mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(cut.outputs[0],mul.inputs[0]);l.new(ray.outputs['Is Camera Ray'],mul.inputs[1]);mix=n.new('ShaderNodeMixShader');l.new(mul.outputs[0],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0]);collection=bpy.data.collections.new('rack-worldplane-v1 fixed faces');s.collection.children.link(collection)
faces=[('front Y=3.5',[(1.5,3.5,0),(3.3,3.5,0),(3.3,3.5,2.7),(1.5,3.5,2.7)],['front-left-foot','front-right-foot','front-right-top','front-left-top']),('right X=3.3',[(3.3,3.5,0),(3.3,4.7,0),(3.3,4.7,2.7),(3.3,3.5,2.7)],['front-right-foot','back-right-foot','back-right-top','front-right-top']),('top Z=2.7',[(1.5,3.5,2.7),(3.3,3.5,2.7),(3.3,4.7,2.7),(1.5,4.7,2.7)],['front-left-top','front-right-top','back-right-top','back-left-top'])];records=[]
for name,vertices,names in faces:
 mesh=bpy.data.meshes.new('rack-worldplane-v1 '+name);mesh.from_pydata(vertices,[],[(0,1,2,3)]);mesh.update();o=bpy.data.objects.new('rack-worldplane-v1 '+name,mesh);collection.objects.link(o);mesh.materials.append(m);uv=mesh.uv_layers.new(name='UVMap');coords=[(uvanchors[x][0]/tw,1-uvanchors[x][1]/th)for x in names]
 for i,loop in enumerate(mesh.loops):uv.data[i].uv=coords[loop.vertex_index]
 for attr in ['visible_shadow','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter']:setattr(o,attr,False)
 projected=[]
 for v in vertices:
  p=world_to_camera_view(s,c,Vector(v));projected.append([p.x*W,(1-p.y)*H])
 records.append({'name':o.name,'exact_world_corners':vertices,'source_projected_corners':projected,'native_corner_anchor_names':names,'native_corner_uv_pixels':[uvanchors[x]for x in names]})
for row in g['all_projected_corners']:
 name=row['object']
 if name.startswith('Plaque ')or name.endswith(' plaque'):continue
 bpy.data.objects[name].visible_camera=False
errors=[]
for name,(v,mat)in before.items():
 o=bpy.data.objects[name]
 if v!=[list(x.co)for x in o.data.vertices]or mat!=[list(x)for x in o.matrix_world]:errors.append(name)
for name,(mat,scale)in cams.items():
 o=bpy.data.objects[name]
 if mat!=[list(x)for x in o.matrix_world]or scale!=o.data.ortho_scale:errors.append(name)
assert not errors,errors
s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;x0,y0,x1,y1=g['source_crop_xyxy'];s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/W;s.render.border_max_x=x1/W;s.render.border_min_y=1-y1/H;s.render.border_max_y=1-y0/H;s.cycles.samples=16;s.cycles.seed=0;s.render.filepath=str(R/'rack-worldplane-v1-native-render.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'rack-worldplane-v1.blend'));start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
rec={'status':'one bounded world-plane surface comparison; visual gate pending','geometry_source':'rack-open-cap-preparation-v1.blend','source_crop_xyxy':g['source_crop_xyxy'],'source_full_dimensions':[W,H],'faces':records,'all_existing_meshes_checked':len(before),'all_existing_cameras_checked':len(cams),'coordinate_or_transform_changes':errors,'original_209_geometry_preserved':True,'native_unchanged':True,'texture_native':'rack-sprite-v1-native.png','alpha_cutoff':192/255,'physical_envelope':[[1.5,3.5,0],[3.3,4.7,2.7]],'original_boards_and_letters_retained':True,'original_shadows_retained':True,'mapping_limits':['2.5D camera-only texture surfaces, not true modeled stock/metal geometry.','Native post-center corner UVs shared exactly along adjacent faces. Native rounded post thickness outside these face splits is clipped to fixed physical envelope.','Top stock is painted on Z2.7 plane; apparent depth must be visually judged in the fixed source camera, no camera orbit supported.','Back plane not visible from approved source camera and not added.'],'measured_crop_render_seconds':elapsed,'production_changed':False};(R/'rack-worldplane-v1-receipt.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print('WORLDPLANE_RENDER_SECONDS',elapsed)
