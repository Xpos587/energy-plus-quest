exec(open('/home/michael/Github/energy-plus-quest/design/warehouse-blockout-2026-10-21/build_blockout.py').read().split("S.render.resolution_percentage=100;")[0])
# V2 is standalone from same deterministic primitive definitions; v1 scene/artifacts remain historical.
for o in list(bpy.data.objects):
 if o.name.startswith('Keeper 1.76m'):o.location.x+=9.8;o.location.y-=2.8
 if o.name.startswith('WMS operator'):bpy.data.objects.remove(o,do_unlink=True);continue
 if o.name.startswith('WMS desk') or o.name.startswith('WMS terminal'):o.location.x-=1.1
 if o.name.startswith('Truck cargo roof') or o.name.startswith('Truck cargo side'):o.hide_render=True
# Explicit cargo cutaway retains open rear frame, bed at indoor z0, full true volume wire edges.
current='Architecture'
for x in [-4.9,-.1]:
 for y in [1,3.4]:line('Truck cargo wire vertical',(x,y,0),(x,y,2.65),.022,'steel')
 line('Truck cargo wire rear/header',(x,1,2.65),(x,3.4,2.65),.022,'steel')
for y in [1,3.4]:line('Truck cargo wire length',(-4.9,y,2.65),(-.1,y,2.65),.022,'steel')
# Blue/orange structural palette, still a plain geometry blockout.
C['steel'].diffuse_color=(.06,.32,.62,1)
m=bpy.data.materials.new('Rack orange beams');m.diffuse_color=(.95,.32,.055,1)
for o in bpy.data.objects:
 if 'beam' in o.name and o.name.startswith('Rack'):o.data.materials.clear();o.data.materials.append(m)
S.view_settings.view_transform='Standard';S.view_settings.look='None';S.display.shading.show_shadows=False
bpy.data.objects['Target keeper'].location=(10.8,2.3,1.5);bpy.data.objects['Target wms'].location=(9.5,.9,1.1)
targets={'receiving':[.25,2.2,1.4],'keeper':[10.8,2.3,1.5],'wms':[9.5,.9,1.1],'alphabet':[5.4,3.43,2.32]}
# Honest orthographic camera surface visibility, not anchor/bbox-only claims.
import random
random.seed(0)
def visibility(cam,group):
 S.camera=cam;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();toward=cam.matrix_world.to_quaternion()@Vector((0,0,1));count=inside=visible=0
 for o in group:
  if o.type!='MESH' or o.hide_render:continue
  mesh=o.evaluated_get(deps).to_mesh();mesh.calc_loop_triangles();mw=o.matrix_world
  for tri in mesh.loop_triangles:
   vs=[mw@mesh.vertices[i].co for i in tri.vertices];normal=(vs[1]-vs[0]).cross(vs[2]-vs[0]);
   if normal.dot(toward)<=0:continue
   for weights in [(1/3,1/3,1/3),(.6,.2,.2),(.2,.6,.2),(.2,.2,.6)]:
    p=sum((v*t for v,t in zip(vs,weights)),Vector());count+=1;uv=world_to_camera_view(S,cam,p)
    if not(0<=uv.x<=1 and 0<=uv.y<=1 and uv.z>0):continue
    inside+=1;hit,loc,no,ind,obj,mat=S.ray_cast(deps,p+toward*80,-toward,distance=80.01)
    if hit and (obj==o or obj.original==o) and (loc-p).length<.02:visible+=1
  o.evaluated_get(deps).to_mesh_clear()
 return {'front_surface_samples':count,'inside_viewport_samples':inside,'ray_visible_samples':visible,'visible_fraction':visible/count if count else 0,'viewport_visible_fraction':visible/inside if inside else 0,'visible':visible>0,'method':'orthographic camera rays to front-facing triangle samples; evaluated mesh'}
groups={'receiving':[o for o in bpy.data.objects if o.name.startswith('ПРИЁМКА jamb') or o.name.startswith('ПРИЁМКА header')], 'keeper':[o for o in bpy.data.objects if o.name.startswith('Keeper 1.76m')], 'wms':[o for o in bpy.data.objects if o.name.startswith('WMS desk') or o.name.startswith('WMS terminal')], 'alphabet':[o for o in bpy.data.objects if 'plaque' in o.name]}
manifest={'units':'m','seed':0,'engine':'BLENDER_WORKBENCH','room':{'bounds':[[0,0,0],[12,7.5,3.6]],'receiving_plane':'X=0','dispatch_plane':'X=12','parallel_normals':[[1,0,0],[1,0,0]],'cutaway':'roof and south wall omitted; dispatch opaque wall cut at z .2, full-height wire retained; truck cargo roof/side surfaces omitted with exact volume wire and open rear'},'rack_runs':rackmeta,'pedestrian_service_gaps_m':[1.2,1.2],'front_cross_aisle_m':3.5,'operational_limit':'3.5m modeled front cross-aisle is not a certified turning envelope; forklift excluded from 1.2m gaps','human_height_m':1.76,'floor_pallet':[1.2,.8,.15],'forklift_body':[1.65,1.1,.85],'forklift_total_length_m':2.8,'gate_opening_m':[3,3],'dock':{'indoor_and_cargo_bed_z':0,'exterior_yard_z':-1.1,'truck_long_axis':'X perpendicular to X0; no drive to yard'},'targets':targets,'cameras':{},'art_status':'plain geometry sourceproof; no AI/production edits'}
projectpoints={'origin':[0,0,0],'X12':[12,0,0],'Y7.5':[0,7.5,0],'Z3.6':[0,0,3.6],'dispatch0':[12,0,3.6],'dispatchY':[12,7.5,3.6],'receiving0':[0,0,3.6],'receivingY':[0,7.5,3.6],'rackA':[1.5,3.5,0],'rackB':[3.3,3.5,0],'rackC':[3.3,4.7,0],'rackD':[1.5,4.7,0],'rackTop':[1.5,3.5,2.7],'gapA':[3.3,4.1,.02],'gapB':[4.5,4.1,.02],'aisleA':[5.4,0,.02],'aisleB':[5.4,3.5,.02]}
for name,c in cams.items():
 S.camera=c['object'];S.render.resolution_x,S.render.resolution_y=c['resolution'];S.render.resolution_percentage=100;bpy.context.view_layer.update();coords={k:list(world_to_camera_view(S,S.camera,Vector(p))) for k,p in targets.items()};
 manifest['cameras'][name]={'type':'ORTHO','location':list(S.camera.location),'rotation_euler':list(S.camera.rotation_euler),'look_at':c['look_at'],'ortho_scale':S.camera.data.ortho_scale,'resolution':c['resolution'],'safe_margin':.05,'target_projection_uvz':coords,'proof_points_uvz':{k:list(world_to_camera_view(S,S.camera,Vector(p))) for k,p in projectpoints.items()},'same_scene':True,'visibility':{k:visibility(S.camera,g) for k,g in groups.items()}}
 for guide in [False,True]:
  cols['Guides'].hide_render=not guide;S.render.filepath=str(R/(name.lower()+'-v2-'+('axes' if guide else 'clean')+'.png'));bpy.ops.render.render(write_still=True)
# Full runtime source is Desktop. Derive exact portrait viewport rectangle in its source plane.
import numpy as np
from mathutils import Vector as V
S.camera=cams['Desktop']['object'];S.render.resolution_x,S.render.resolution_y=cams['Desktop']['resolution'];p0=world_to_camera_view(S,S.camera,V((0,0,0)));px=world_to_camera_view(S,S.camera,V((1,0,0)));py=world_to_camera_view(S,S.camera,V((0,1,0)))
S.camera=cams['Portrait']['object'];S.render.resolution_x,S.render.resolution_y=cams['Portrait']['resolution'];q0=world_to_camera_view(S,S.camera,V((0,0,0)));qx=world_to_camera_view(S,S.camera,V((1,0,0)));qy=world_to_camera_view(S,S.camera,V((0,1,0)))
P=np.array([[px.x-p0.x,py.x-p0.x],[px.y-p0.y,py.y-p0.y]]);Q=np.array([[qx.x-q0.x,qy.x-q0.x],[qx.y-q0.y,qy.y-q0.y]]);M=P@np.linalg.inv(Q);t=np.array([p0.x,p0.y])-M@np.array([q0.x,q0.y]);corners=[M@np.array(c)+t for c in [(0,1),(1,0)]];W,H=cams['Desktop']['resolution'];rect=[corners[0][0]*W,(1-corners[0][1])*H,corners[1][0]*W,(1-corners[1][1])*H]
manifest['runtime_source_contract']={'full_source':'desktop-v2-clean.png','dimensions':[W,H],'origin':'top-left','all_four_anchor_px':{k:[v[0]*W,(1-v[1])*H] for k,v in manifest['cameras']['Desktop']['target_projection_uvz'].items()},'portrait_initial_viewport_source_xyxy':rect,'portrait_initial_frame':'portrait-v2-clean.png','portrait_policy':'same full source plane; viewport plus pan, clipped items remain reachable; allow transparent overflow if source rect exceeds full source','projection_mapping_uv':{'matrix':M.tolist(),'translation':t.tolist()}}
cols['Guides'].hide_render=False;S.camera=cams['Desktop']['object'];S.render.resolution_x,S.render.resolution_y=cams['Desktop']['resolution'];bpy.ops.wm.save_as_mainfile(filepath=str(D/'warehouse-blockout-v2.blend'));(D/'manifest-v2.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('V2 complete; source crop',rect)
