import bpy
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;s=bpy.context.scene;roots=[o for o in s.objects if o.name.startswith('truck-')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
for o in s.objects:
 if o.type in ('MESH','FONT','CURVE') and o not in fleet:o.hide_render=True
s.frame_set(769);root=bpy.data.objects['truck-3-tractor'];cam=s.camera;center=root.matrix_world@Vector((0,0,1.7));cam.location=root.matrix_world@Vector((10,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6
s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.filepath=str(O/'green-original-close.png');bpy.ops.render.render(write_still=True)
