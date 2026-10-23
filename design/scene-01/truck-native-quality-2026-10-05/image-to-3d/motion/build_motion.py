import bpy, math, pathlib, json
from mathutils import Vector,Matrix
O=pathlib.Path(__file__).resolve().parent;P=O.parent
bpy.ops.wm.open_mainfile(filepath='/home/michael/Github/energy-plus-quest/design/scene-01/controlled-motion-2026-10-04/v2b/controlled-straight-start.blend');s=bpy.context.scene
tractor=bpy.data.objects['truck-3-tractor'];trailer=bpy.data.objects['truck-3-trailer'];camera_rotation=bpy.data.objects['desktop'].rotation_euler.copy()
# Read both baked independent world-space motions before deleting old scene contents.
samples=[]
for i in range(1,145):
 sf=2+(i-1)*97/143;s.frame_set(math.floor(sf),subframe=sf%1)
 samples.append({'frame':i,'source_frame':sf,'tractor':{'location':list(tractor.location),'rotation':list(tractor.rotation_euler)},'trailer':{'location':list(trailer.location),'rotation':list(trailer.rotation_euler)}})
keep={tractor,trailer,*trailer.children_recursive}
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
for root,key in [(tractor,'tractor'),(trailer,'trailer')]:
 root.animation_data_clear()
 for r in samples:
  root.location=r[key]['location'];root.rotation_euler=r[key]['rotation'];root.keyframe_insert('location',frame=r['frame']);root.keyframe_insert('rotation_euler',frame=r['frame'])
# imported mesh's existing local/world matrix defines the generated GLB upright orientation
with bpy.data.libraries.load(str(P/'green-tractor-finished.blend'),link=False) as (src,dst):dst.objects=['Mesh_0']
mesh=dst.objects[0];bpy.context.collection.objects.link(mesh)
original=mesh.matrix_world.copy();vs=[original@v.co for v in mesh.data.vertices];lo=Vector(tuple(min(v[j] for v in vs) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vs) for j in range(3)))
for v,co in zip(mesh.data.vertices,vs):v.co=co
mesh.parent=tractor;mesh.matrix_parent_inverse=Matrix.Identity(4);mesh.location=(1.48+lo.x*2.2,0,-lo.z*2.2);mesh.rotation_euler=(0,0,math.pi);mesh.scale=(2.2,2.2,2.2);mesh.name='New textured whole green 6x4 tractor'
# White separate articulated semitrailer; retain old modeled running gear/hardware.
white=bpy.data.materials.new('Warm white semitrailer paint');white.use_nodes=True;bs=white.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.87,.89,.85,1);bs.inputs['Roughness'].default_value=.85;bs.inputs['Specular IOR Level'].default_value=.1
body=bpy.data.objects['3 long semitrailer'];body.data.materials.clear();body.data.materials.append(white)
for p in body.data.polygons:p.material_index=0
# sole clean presentation ground
floor=bpy.data.materials.new('Clean pale blue presentation ground');floor.use_nodes=True;bs=floor.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.73,.85,.91,1);bs.inputs['Roughness'].default_value=1;bs.inputs['Specular IOR Level'].default_value=0
bpy.ops.mesh.primitive_plane_add(size=200,location=(18,21,-.035));bpy.context.object.name='Clean pale blue ground';bpy.context.object.data.materials.append(floor)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.81,.9,.95,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for loc,energy,size in [((15,8,32),2200,24),((33,30,23),900,20)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.size=size;l.rotation_euler=(Vector((18,22,0))-l.location).to_track_quat('-Z','Y').to_euler()
# Same fixed map view orientation; compute an all-frame crop for complete tractor and trailer.
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Fixed map maneuver camera';cam.rotation_euler=camera_rotation;cam.data.type='ORTHO';s.camera=cam
rot=cam.rotation_euler.to_matrix();axisx=rot@Vector((1,0,0));axisy=rot@Vector((0,1,0));normal=rot@Vector((0,0,1));coords=[]
visible=[mesh,*[o for o in trailer.children_recursive if o.type=='MESH' and not o.hide_render]]
for i in range(1,145):
 s.frame_set(i);bpy.context.view_layer.update()
 for o in visible:
  for p in o.bound_box:
   q=o.matrix_world@Vector(p);coords.append((q.dot(axisx),q.dot(axisy),q.dot(normal)))
xmin=min(q[0] for q in coords);xmax=max(q[0] for q in coords);ymin=min(q[1] for q in coords);ymax=max(q[1] for q in coords)
center=axisx*((xmin+xmax)/2)+axisy*((ymin+ymax)/2)+normal*1
cam.location=center+normal*60;cam.data.ortho_scale=max((xmax-xmin)/(768/640),ymax-ymin)*1.13
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.render.resolution_x=768;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=144;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'frames/frame-');(O/'frames').mkdir(exist_ok=True)
s.render.film_transparent=False
# Disable any inherited compositing overlays, render borders, or sequencer.
s.use_nodes=False;s.render.use_border=False;s.render.use_sequencer=False
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-tractor-turn.blend'))
receipt={'source_interval':[2,99],'output_frames':[1,144],'fps':24,'duration_seconds':6,'baked_world_samples':samples,'source_mesh_bounds':{'min':list(lo),'max':list(hi)},'tractor_local_mesh_scale':2.2,'tractor_local_mesh_location':list(mesh.location),'tractor_mesh_rotation_z':math.pi,'camera':{'location':list(cam.location),'rotation':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale,'resolution':[768,640]},'limitations':['Generated whole tractor is a single textured mesh; wheels do not rotate independently.','Trailer remains old separately baked articulated geometry.','This is a six-second motion proof, not an integrated game asset.','Image-to-3D texture defects and fixed painted occupants remain visible.']}
(O/'motion-receipt.json').write_text(json.dumps(receipt,indent=2))
for frame,name in [(1,'entry'),(42,'apex'),(144,'exit')]:
 s.frame_set(frame);s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
s.render.filepath=str(O/'frames/frame-');bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-tractor-turn.blend'));bpy.ops.render.render(animation=True)
