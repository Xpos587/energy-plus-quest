import bpy,bmesh,json,math,time
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent;source=P.parent/'fleet-painted-projected-v09.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
roots=sorted([o for o in s.objects if o.name.startswith('truck-')],key=lambda o:o.name)
def poses():
 out=[]
 for f in range(1,1153):
  s.frame_set(f);out.append([float(x) for o in roots for r in o.matrix_world for x in r])
 return out
before=poses();camera={'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'ortho':s.camera.data.ortho_scale};actions={o.name:o.animation_data.action.name if o.animation_data and o.animation_data.action else None for o in roots};s.frame_set(1);records=[]
def box(name,parent,loc,dims,mat,radius=.012):
 bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name=name;o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);o.location=loc;o.scale=[v/2 for v in dims];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);b=o.modifiers.new('Rounded mirror housing','BEVEL');b.width=radius;b.segments=4;o.modifiers.new('Smooth housing normals','WEIGHTED_NORMAL');return o
for i in range(1,5):
 ob=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];coords=[tuple(v.co) for v in ob.data.vertices];driver_before=[tuple(ob.data.vertices[k].co) for p in ob.data.polygons if p.material_index==1 for k in p.vertices];driverpolys_before=sum(p.material_index==1 for p in ob.data.polygons);images=[n.image.name for n in ob.data.materials[1].node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
 bm=bmesh.new();bm.from_mesh(ob.data);remove=[];sillcount=0;mirrorcount=0
 for face in bm.faces:
  if face.material_index==1:continue
  c=face.calc_center_median()
  sill=c.x<-.93 and -.080<c.z<.110 and abs(c.y)<.425
  mirror=c.x<-.94 and .400<abs(c.y)<.510 and .075<c.z<.370
  if sill or mirror:remove.append(face);sillcount+=bool(sill);mirrorcount+=bool(mirror)
 bmesh.ops.delete(bm,geom=remove,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free();ob.data.update()
 assert coords==[tuple(v.co) for v in ob.data.vertices]
 driver_after=[tuple(ob.data.vertices[k].co) for p in ob.data.polygons if p.material_index==1 for k in p.vertices];assert sorted(driver_before)==sorted(driver_after);assert driverpolys_before==118
 pigment=ob.data.materials[4];slate=ob.data.materials[3]
 # Thin closed ribbon: smooth straight lower windshield edge, modest side returns.
 ys=[-.442,-.417,-.385,0,.385,.417,.442];xs=[-.995,-1.089,-1.115,-1.115,-1.115,-1.089,-.995];vertices=[]
 for rear in (0,.009):
  for z in (-.079,.055):
   for y,x in zip(ys,xs):vertices.append((x+rear,y,z))
 faces=[];N=len(ys)
 for j in range(N-1):faces.extend([(j,j+1,N+j+1,N+j),(2*N+j,3*N+j,3*N+j+1,2*N+j+1),(j,2*N+j,2*N+j+1,j+1),(N+j,N+j+1,3*N+j+1,3*N+j)])
 faces.extend([(0,N,3*N,2*N),(N-1,3*N-1,4*N-1,2*N-1)])
 me=bpy.data.meshes.new(f'V09 clean {i} continuous sill mesh');me.from_pydata(vertices,[],faces);me.materials.append(pigment);ribbon=bpy.data.objects.new(f'V09 CLEAN {i} continuous cab sill',me);s.collection.objects.link(ribbon);ribbon.parent=ob;ribbon.matrix_parent_inverse=Matrix.Identity(4);bevel=ribbon.modifiers.new('Soft sill manufactured edge','BEVEL');bevel.width=.003;bevel.segments=3;ribbon.modifiers.new('Sill normals','WEIGHTED_NORMAL')
 # New compact mirror housings and mounting stems replace only removed protruding seam faces.
 for side in (-1,1):
  box(f'V09 CLEAN {i} mirror housing {side}',ob,(-1.037,side*.451,.222),(.068,.061,.196),slate,.014)
  box(f'V09 CLEAN {i} mirror mounting stem {side}',ob,(-1.013,side*.414,.308),(.024,.073,.024),slate,.009)
  # Thin continuous A-pillar facing strip follows windshield plane slope.
  vs=[(-1.104,side*.388,.055),(-1.104,side*.416,.055),(-.985,side*.416,.353),(-.985,side*.388,.353)];mm=bpy.data.meshes.new('clean window facing');mm.from_pydata(vs,[],[(0,1,2,3)]);mm.materials.append(slate);oo=bpy.data.objects.new(f'V09 CLEAN {i} windshield side facing {side}',mm);s.collection.objects.link(oo);oo.parent=ob;oo.matrix_parent_inverse=Matrix.Identity(4);solid=oo.modifiers.new('Facing strip thickness','SOLIDIFY');solid.thickness=.004
 records.append({'truck':i,'removed_sill_body_faces':sillcount,'removed_mirror_body_faces':mirrorcount,'driver_polygons_before':driverpolys_before,'driver_polygons_after':sum(p.material_index==1 for p in ob.data.polygons),'driver_vertices_unchanged':True,'driver_images':images,'all_existing_vertex_coordinates_unchanged':True,'added_geometry':['Thin closed continuous sill ribbon in cabmesh local space','Two compact rounded mirror housings/stems','Two thin continuous windshield side strips'],'repair_bounds_model':{'sill_z':[-.079,.055],'sill_y':[-.442,.442],'mirror_z':[.124,.32]}})
after=poses();delta=max(abs(x-y) for p,q in zip(before,after) for x,y in zip(p,q));assert delta==0;assert camera=={'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'ortho':s.camera.data.ortho_scale}
fleet=set(roots)
for root in roots:fleet.update(root.children_recursive)
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');crypto.matte_id=', '.join(o.name for o in fleet if o.type in ('MESH','FONT') and not o.hide_render)
s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v09-clean-sill.blend'));receipt={'source':str(source),'records':records,'frames_verified':1152,'root_count':8,'root_matrix_max_delta':delta,'camera_unchanged':True,'actions':actions,'protected_regions':'All pre-existing vertex coordinates unchanged. Face deletion restricted to frontal windshield sill/mirror regions; no wheel/contact/rear/hitch region touched.','geometry_method':'Real closed sill ribbon and compact mirror hardware parented to existing detailed tractor mesh; no billboard or overlay.','visual_status':'Await actual front and opposite-side inspection.'};(P/'repair-receipt.json').write_text(json.dumps(receipt,indent=2))
flags={o.name:o.hide_render for o in s.objects};s.frame_set(769);cam=s.camera;s.render.resolution_x=1200;s.render.resolution_y=1200
for i,side in [(3,-1),(3,1)]:
 tractor=bpy.data.objects[f'truck-{i}-tractor'];trailer=bpy.data.objects[f'truck-{i}-trailer'];own={tractor,trailer};own.update(tractor.children_recursive);own.update(trailer.children_recursive)
 for o in s.objects:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags[o.name] or o not in own
 center=tractor.matrix_world@Vector((.25,0,1.65));cam.location=tractor.matrix_world@Vector((11,8*side,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.5;s.render.filepath=str(P/('front-3.png' if side==-1 else 'green-opposite-side.png'));bpy.ops.render.render(write_still=True)
print('COHERENT SILL AND MIRROR REPAIR QA READY',flush=True)
