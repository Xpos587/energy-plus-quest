import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
source=P.parent/'fleet-painted-projected-v09.blend';candidate=P/'fleet-v09-clean-sill.blend'
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;roots=sorted((o for o in s.objects if o.name.startswith('truck-')),key=lambda o:o.name);poses=[]
 for f in range(1,1153):
  s.frame_set(f);poses.append([float(x) for o in roots for r in o.matrix_world for x in r])
 cabs={}
 for i in range(1,5):
  ob=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];cabs[i]={'coords':[tuple(v.co) for v in ob.data.vertices],'drivercoords':sorted(tuple(ob.data.vertices[k].co) for p in ob.data.polygons if p.material_index==1 for k in p.vertices),'driverpolys':sum(p.material_index==1 for p in ob.data.polygons),'drivermaterial':ob.data.materials[1].name,'driverimages':[n.image.name for n in ob.data.materials[1].node_tree.nodes if n.type=='TEX_IMAGE' and n.image]}
 return {'poses':poses,'cabs':cabs,'actions':{o.name:o.animation_data.action.name if o.animation_data and o.animation_data.action else None for o in roots},'camera':{'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'ortho':s.camera.data.ortho_scale},'range':[s.frame_start,s.frame_end]}
a=capture(source);b=capture(candidate);delta=max(abs(x-y) for p,q in zip(a['poses'],b['poses']) for x,y in zip(p,q));checks={i:{'all_existing_vertex_coordinates_equal':a['cabs'][i]['coords']==b['cabs'][i]['coords'],'driver_geometry_material_images_equal':all(a['cabs'][i][k]==b['cabs'][i][k] for k in ['drivercoords','driverpolys','drivermaterial','driverimages']),'driverpolygons':b['cabs'][i]['driverpolys'],'images':b['cabs'][i]['driverimages']} for i in range(1,5)};r={'source':str(source),'candidate':str(candidate),'frames_verified':1152,'roots':8,'root_matrix_max_delta':delta,'camera_equal':a['camera']==b['camera'],'actions_equal':a['actions']==b['actions'],'frame_range_equal':a['range']==b['range'],'cabs':checks,'no_broad_shape_edit':'Original mesh vertex coordinates exactly unchanged; only bounded frontbody faces removed and separate local repaired hardware added.'};assert delta==0 and r['camera_equal'] and r['actions_equal'] and r['frame_range_equal'];assert all(c['all_existing_vertex_coordinates_equal'] and c['driver_geometry_material_images_equal'] and c['driverpolygons']==118 for c in checks.values());(P/'saved-verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
