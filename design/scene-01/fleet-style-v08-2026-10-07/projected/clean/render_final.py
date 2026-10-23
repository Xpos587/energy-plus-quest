import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v09-clean-sill.blend'));s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
for f in (1,385,769):s.frame_set(f);s.render.filepath=str(P/f'vehicles-{f:04}.png');bpy.ops.render.render(write_still=True)
roots=[o for o in s.objects if o.name.startswith('truck-')];flags={o.name:o.hide_render for o in s.objects};s.frame_set(769);cam=s.camera;s.render.resolution_x=1200;s.render.resolution_y=1200
for i in range(1,5):
 tractor=bpy.data.objects[f'truck-{i}-tractor'];trailer=bpy.data.objects[f'truck-{i}-trailer'];own={tractor,trailer};own.update(tractor.children_recursive);own.update(trailer.children_recursive)
 for o in s.objects:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags[o.name] or o not in own
 center=tractor.matrix_world@Vector((.25,0,1.65));cam.location=tractor.matrix_world@Vector((11,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.5;s.render.filepath=str(P/f'front-{i}.png');bpy.ops.render.render(write_still=True)
print('FINAL CLEAN FLEET 3 STILLS AND 4 FRONTS COMPLETE')
