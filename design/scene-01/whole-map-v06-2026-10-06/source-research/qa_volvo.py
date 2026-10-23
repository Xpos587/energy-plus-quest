import bpy,math,json
from mathutils import Vector
from pathlib import Path
p=Path('design/scene-01/whole-map-v06-2026-10-06/source-research').resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(p/'free3d-volvo-fh-green.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];lo=Vector(tuple(min(v[a] for v in points) for a in range(3)));hi=Vector(tuple(max(v[a] for v in points) for a in range(3)));center=(lo+hi)/2
# Cab roof lies on one end of the longitudinal Y-axis after standard glTF import.
upper=[v.y for v in points if v.z>lo.z+(hi.z-lo.z)*.65];front=-1 if sum(upper)/len(upper)<center.y else 1
print('BOUNDS',tuple(lo),tuple(hi),'FRONT_Y',front)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('soft daylight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.78,.84,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
s.view_settings.view_transform='AgX'
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for loc,power,size in [((1,-2,3),150,3),((-2,1,2),80,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,center)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,lo.z-.002));floor=bpy.context.object;mat=bpy.data.materials.new('neutral studio');mat.diffuse_color=(.58,.62,.66,1);floor.data.materials.append(mat)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='QA camera';cam.data.type='ORTHO';cam.data.ortho_scale=1.65;s.camera=cam
manifest={'source':'free3d-volvo-fh-green.glb','bounds':{'min':list(lo),'max':list(hi)},'front_axis':'%sY'%('+'if front>0 else '-'),'triangles':sum(len(o.data.polygons) for o in meshes),'cameras':{}}
for name,pos in [('front3q',(1.6,front*2.2,1.0)),('desktop-high',(1.4,front*1.8,2.4))]:
 cam.location=Vector(pos)+center;aim(cam,center);s.render.filepath=str(p/('volvo-'+name+'.png'));manifest['cameras'][name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale,'render':s.render.filepath};bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'preview.blend'));(p/'volvo-qa-manifest.json').write_text(json.dumps(manifest,indent=2))
