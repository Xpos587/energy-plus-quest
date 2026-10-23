import bpy,json,math
from pathlib import Path
from mathutils import Vector
p=Path('design/scene-01/whole-map-v06-2026-10-06/source-research').resolve()
bpy.ops.wm.open_mainfile(filepath=str(p/'preview.blend'))
for o in list(bpy.context.scene.objects):
 if o.type=='MESH' and o.name!='Plane':bpy.data.objects.remove(o,do_unlink=True)
source=Path('design/scene-01/truck-native-quality-2026-10-05/image-to-3d/green-tractor-finished.blend').resolve()
with bpy.data.libraries.load(str(source),link=False) as (a,b):b.objects=['Mesh_0']
o=b.objects[0];bpy.context.scene.collection.objects.link(o);o.rotation_euler.z=-math.pi/2;o.scale=(.527,.527,.527);bpy.context.view_layer.update()
pts=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector(tuple(min(v[a] for v in pts) for a in range(3)));hi=Vector(tuple(max(v[a] for v in pts) for a in range(3)));center=(lo+hi)/2
# Match center and ground clearance of Volvo preview.
o.location-=center;o.location.z+=.00546;bpy.context.view_layer.update()
s=bpy.context.scene;cam=s.camera;center=Vector((.00171,-.00008,.00546));cam.location=Vector((1.6,-2.2,1))+center;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(p/'higgs-front3q-comparison.png');bpy.ops.render.render(write_still=True)
