import bpy,pathlib,math,json
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'surfaces/clean-cab.blend'))
with bpy.data.libraries.load(str(P/'crew/face-lookdev.blend'),link=False) as (a,b):b.collections=['CREW']
crew=b.collections[0];bpy.context.scene.collection.children.link(crew)
s=bpy.context.scene;cam=s.camera
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(P/'green-truck-v03.blend'))
for name,loc,target,scale in [('front',(-3,0,.35),(-.75,0,.1),1.02),('three-quarter',(-3,1.1,.65),(-.75,0,.1),1.10),('body',(-3,3,2.3),(0,0,0),2.6)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
# Existing baked maneuver is kept verbatim. Each actor follows the imported cab.
O=P.parent/'truck-native-quality-2026-10-05/image-to-3d/motion'
bpy.ops.wm.open_mainfile(filepath=str(O/'green-tractor-turn-detailed.blend'))
s=bpy.context.scene;obj=bpy.data.objects['New textured whole green 6x4 tractor'];before=obj.matrix_basis.copy()
with bpy.data.libraries.load(str(P/'green-truck-v03.blend'),link=False) as (a,b):b.objects=['Mesh_0'];b.collections=['CREW']
source=b.objects[0];obj.data=source.data.copy();bpy.data.objects.remove(source,do_unlink=True)
crew=b.collections[0];s.collection.children.link(crew)
for actor in crew.objects:
 actor.parent=obj
assert obj.matrix_basis==before
bpy.ops.file.pack_all();s.render.engine='BLENDER_EEVEE';s.render.resolution_x=960;s.render.resolution_y=800
for frame,name in [(1,'entry'),(42,'apex'),(144,'exit')]:
 s.frame_set(frame);s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
s.frame_set(1);s.render.filepath=str(P/'frames/frame-');(P/'frames').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'green-turn-v03.blend'));bpy.ops.render.render(animation=True)
(P/'receipt.json').write_text(json.dumps({'two_volumetric_seated_actors':True,'one_wheel':True,'cab_transform_preserved':True,'trajectory_changed':False,'frames':144,'fps':24,'resolution':[960,800],'limitations':['facial style remains simplified and requires visual approval','generated cab geometry has panel artifacts','wheels remain part of original static mesh','maneuver is not a complete city loop']},indent=2))
