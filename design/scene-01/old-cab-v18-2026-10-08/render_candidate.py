import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v18-old-cabs.blend'));s=bpy.context.scene;cam=s.camera
s.eevee.taa_render_samples=32;s.eevee.volumetric_samples=64;s.eevee.volumetric_tile_size='4'
s.frame_set(96);bpy.context.view_layer.update();inv=cam.matrix_world.inverted()
depths=[-(inv@o.matrix_world@Vector(v)).z for o in bpy.data.collections['V17 worldspace exhaust puffs'].objects for v in o.bound_box]
s.eevee.use_volume_custom_range=True;s.eevee.volumetric_start=min(depths)-2;s.eevee.volumetric_end=max(depths)+2
s.render.resolution_percentage=100;s.render.filepath=str(P/'vehicles-0096.png');bpy.ops.render.render(write_still=True)
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
flags={o.name:o.hide_render for o in fleet}
for o in bpy.data.collections['V17 worldspace exhaust puffs'].objects:o.hide_render=True
s.render.resolution_x=1200;s.render.resolution_y=900
for i in (1,4):
 root=bpy.data.objects[f'truck-{i}-tractor'];own={root,*root.children_recursive}
 for o in fleet:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags[o.name] or o not in own
 target=root.matrix_world@Vector((.3,0,1));cam.location=root.matrix_world@Vector((9,-7,6));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=5.7
 s.render.filepath=str(P/f'v18-front-{i}.png');bpy.ops.render.render(write_still=True)
