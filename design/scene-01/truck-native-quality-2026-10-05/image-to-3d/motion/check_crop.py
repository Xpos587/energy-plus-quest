import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p='/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/image-to-3d/motion/green-tractor-turn.blend';bpy.ops.wm.open_mainfile(filepath=p);s=bpy.context.scene
for f in [1,42,144]:
 s.frame_set(f);bpy.context.view_layer.update();t=bpy.data.objects['truck-3-tractor'];r=bpy.data.objects['truck-3-trailer'];ps=[]
 for o in bpy.data.objects:
  if o.type=='MESH' and 'ground' not in o.name:
   ps.extend([world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for v in o.bound_box])
 print(f,list(t.location),list(r.location),'crop',min(p.x for p in ps),max(p.x for p in ps),min(p.y for p in ps),max(p.y for p in ps))
