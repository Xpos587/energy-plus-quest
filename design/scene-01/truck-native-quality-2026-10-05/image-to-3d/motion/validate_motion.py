import bpy,json,pathlib,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=pathlib.Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'green-tractor-turn.blend'));s=bpy.context.scene;d=json.loads((O/'motion-receipt.json').read_text());ps=[];errors=[];hitch=[]
meshes=[o for o in bpy.data.objects if o.type=='MESH' and 'ground' not in o.name]
for r in d['baked_world_samples']:
 s.frame_set(r['frame']);bpy.context.view_layer.update()
 for key,n in [('tractor','truck-3-tractor'),('trailer','truck-3-trailer')]:
  o=bpy.data.objects[n];errors.append(max(abs(o.location[i]-r[key]['location'][i]) for i in range(3)));errors.append(max(abs(o.rotation_euler[i]-r[key]['rotation'][i]) for i in range(3)))
 t=bpy.data.objects['truck-3-tractor'];rroot=bpy.data.objects['truck-3-trailer'];point=t.matrix_world@Vector((-2.3,0,0));hitch.append((point-rroot.location).length)
 for o in meshes:ps.extend([world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box])
res={'sampled_frames':144,'root_resample_max_abs_error':max(errors),'tractor_trailer_original_hitch_xy_max_distance':max(hitch),'all_frame_projected_bounds':{'xmin':min(p.x for p in ps),'xmax':max(p.x for p in ps),'ymin':min(p.y for p in ps),'ymax':max(p.y for p in ps)},'render_engine':s.render.engine,'mesh_count':len(meshes),'camera_fixed':s.camera.animation_data is None,'source_tractor_turn_degrees':math.degrees(d['baked_world_samples'][-1]['tractor']['rotation'][2]-d['baked_world_samples'][0]['tractor']['rotation'][2]),'source_trailer_turn_degrees':math.degrees(d['baked_world_samples'][-1]['trailer']['rotation'][2]-d['baked_world_samples'][0]['trailer']['rotation'][2])}
(O/'validation.json').write_text(json.dumps(res,indent=2));d['camera']['ortho_scale']=s.camera.data.ortho_scale;d['render_engine']=s.render.engine;d['tractor_mesh_rotation_mode']='XYZ';d['validated']=res;(O/'motion-receipt.json').write_text(json.dumps(d,indent=2));print(json.dumps(res))
