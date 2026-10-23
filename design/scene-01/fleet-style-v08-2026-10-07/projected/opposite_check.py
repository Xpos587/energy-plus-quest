import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-painted-projected-v09.blend'));s=bpy.context.scene;s.frame_set(769);root=bpy.data.objects['truck-3-tractor'];trailer=bpy.data.objects['truck-3-trailer'];own={root,trailer};own.update(root.children_recursive);own.update(trailer.children_recursive)
for o in s.objects:
 if o.type in ('MESH','FONT','CURVE') and o not in own:o.hide_render=True
cam=s.camera;center=root.matrix_world@Vector((.25,0,1.65));cam.location=root.matrix_world@Vector((11,8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.5;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.filepath=str(P/'green-opposite-side.png');bpy.ops.render.render(write_still=True)
print('OPPOSITE SIDE RENDERED; master unchanged')
