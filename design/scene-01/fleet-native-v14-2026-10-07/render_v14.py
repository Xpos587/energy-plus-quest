import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
s=bpy.context.scene;cam=s.camera
roots=[bpy.data.objects[f'truck-{i}-{p}']for i in range(1,5)for p in ('tractor','trailer')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
flags={o.name:o.hide_render for o in fleet};cm=cam.matrix_world.copy();ortho=cam.data.ortho_scale
s.render.resolution_percentage=100
for f in (385,1):
 s.frame_set(f);s.render.filepath=str(P/f'vehicles-{f:04d}.png');bpy.ops.render.render(write_still=True)
s.frame_set(769);s.render.resolution_x=1200;s.render.resolution_y=900
for i in (1,4,2,3):
 tr=bpy.data.objects[f'truck-{i}-tractor'];tl=bpy.data.objects[f'truck-{i}-trailer'];own={tr,tl,*tr.children_recursive,*tl.children_recursive}
 for o in fleet:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags[o.name] or o not in own
 target=tr.matrix_world@Vector((-.35,0,1.6));cam.location=tr.matrix_world@Vector((11,-8,7));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.7
 s.render.filepath=str(P/f'v14-front-{i}.png');bpy.ops.render.render(write_still=True)
