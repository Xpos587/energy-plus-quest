import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v12-style.blend'));s=bpy.context.scene
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')];fleet=set(roots)
for root in roots:fleet.update(root.children_recursive)
for i in range(1,5):
 cargo=bpy.data.materials[f'V12 {i} '+('woven pale canvas' if i in (1,4) else 'clean porcelain cargo')]
 for o in fleet:
  for slot in o.material_slots:
   if slot.material and slot.material.name==f'PILOT {i} warm woven trailer':slot.material=cargo
 if i in (1,4):
  root=bpy.data.objects[f'truck-{i}-trailer'];repair=bpy.data.materials[f'V12 {i} repair patch'];seam=bpy.data.materials[f'V12 {i} linen stitches']
  for j,x in enumerate((-4.6,-1.45)):
   bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name=f'V12 {i} roof canvas repair {j}';o.parent=root;o.location=(x,.12 if j else -.1,3.269);o.scale=(.56,.52,.01);o.data.materials.append(repair);fleet.add(o)
   for k in range(7):
    for y in (-.42,.42):
     bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name=f'V12 {i} roof visible stitch';o.parent=root;o.location=(x-.44+k*.146,(.12 if j else -.1)+y,3.283);o.scale=(.022,.045,.009);o.data.materials.append(seam);fleet.add(o)
cam=s.camera;cm=cam.matrix_world.copy();scale=cam.data.ortho_scale
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v12-style.blend'))
for f in (1,385,769):
 s.frame_set(f);s.render.filepath=str(P/f'vehicles-{f:04d}.png');bpy.ops.render.render(write_still=True)
flags={o.name:o.hide_render for o in fleet}
s.frame_set(769);s.render.resolution_x=1200;s.render.resolution_y=900
for i in range(1,5):
 tr=bpy.data.objects[f'truck-{i}-tractor'];tl=bpy.data.objects[f'truck-{i}-trailer'];own={tr,tl,*tr.children_recursive,*tl.children_recursive}
 for o in fleet:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags[o.name] or o not in own
 target=tr.matrix_world@Vector((-.35,0,1.6));cam.location=tr.matrix_world@Vector((11,-8,7));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.7
 s.render.filepath=str(P/f'v12-front-{i}.png');bpy.ops.render.render(write_still=True)
