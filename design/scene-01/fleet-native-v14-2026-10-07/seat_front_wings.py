import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
for i in range(1,5):
 root=bpy.data.objects[f'truck-{i}-tractor'];paint=bpy.data.materials[f'V14 {i} painted body']
 if i in (1,4):
  for sy in (-1,1):
   ob=bpy.data.objects[f'V14 {i} formed side cab {sy}'];ob.data.vertices[5].co.x=1.30;ob.data.vertices[5].co.z=.56
   for j,k in enumerate(range(3,17)):
    a=math.pi*k/18;v=ob.data.vertices[6+j];v.co.x=.8+.425*math.cos(a);v.co.z=.355+.425*math.sin(a)
   ob.data.vertices[-1].co.x=.28;ob.data.vertices[-1].co.z=.56;ob.data.update()
   for k in range(16):
    o=bpy.data.objects[f'V14 {i} rolled wheel arch {sy} {k}'];a=math.pi*k/16;b=math.pi*(k+1)/16
    p=Vector((.8+.425*math.cos(a),o.location.y,.355+.425*math.sin(a)));q=Vector((.8+.425*math.cos(b),o.location.y,.355+.425*math.sin(b)));o.location=(p+q)/2;o.scale.z*=.425/.54;o.rotation_euler=(q-p).to_track_quat('Z','Y').to_euler()
 else:
  for sy in (-1,1):
   profile=[(.12,1.24),(1.46,1.24),(1.46,.56),(1.21,.56)]
   profile +=[(.8+.425*math.cos(math.pi*k/18),.355+.425*math.sin(math.pi*k/18))for k in range(3,17)]
   profile +=[(.12,.56)]
   me=bpy.data.meshes.new('continuous cab wing');me.from_pydata([(x,sy*.949,z)for x,z in profile],[],[tuple(range(len(profile)))]);me.update();o=bpy.data.objects.new(f'V14 {i} continuous side wing {sy}',me);s.collection.objects.link(o);o.parent=root;me.materials.append(paint);so=o.modifiers.new('Formed wing thickness','SOLIDIFY');so.thickness=.035
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
