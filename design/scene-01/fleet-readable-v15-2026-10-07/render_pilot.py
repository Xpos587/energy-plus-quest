import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;cam=s.camera
roots=[bpy.data.objects[f'truck-{i}-{p}']for i in range(1,5)for p in ('tractor','trailer')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
flags={o.name:o.hide_render for o in fleet};cm=(cam.location.copy(),cam.rotation_euler.copy(),cam.scale.copy());ortho=cam.data.ortho_scale
s.render.resolution_percentage=100;s.eevee.volumetric_tile_size='2';s.eevee.volumetric_samples=96;s.eevee.use_volume_custom_range=True;ranges=[]
def volume_range(label):
 bpy.context.view_layer.update();inv=cam.matrix_world.inverted();depths=[]
 for o in fleet:
  if 'connected exhaust plume'in o.name and not o.hide_render:depths +=[-(inv@o.matrix_world@Vector(v)).z for v in o.bound_box]
 start=max(.01,min(depths)-2)if depths else .1;end=max(depths)+2 if depths else 50
 s.eevee.volumetric_start=start;s.eevee.volumetric_end=end;ranges.append({'render':label,'start':start,'end':end,'tile_size':2,'samples':96})
for f in (385,1):
 s.frame_set(f);volume_range(f'map-{f}');s.render.filepath=str(P/f'vehicles-{f:04d}.png');bpy.ops.render.render(write_still=True)
s.frame_set(769);s.render.resolution_x=1200;s.render.resolution_y=900
for i in (1,4,2,3):
 tr=bpy.data.objects[f'truck-{i}-tractor'];tl=bpy.data.objects[f'truck-{i}-trailer'];own={tr,tl,*tr.children_recursive,*tl.children_recursive}
 for o in fleet:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags[o.name]or o not in own
 target=tr.matrix_world@Vector((-.35,0,1.6));cam.location=tr.matrix_world@Vector((11,-8,7));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.7;volume_range(f'close-{i}')
 s.render.filepath=str(P/f'v15-front-{i}.png');bpy.ops.render.render(write_still=True)
(P/'volume-render-ranges.json').write_text(json.dumps(ranges,indent=2))
# Persist sane map settings only; never save the temporary close camera or isolated visibility.
for o in fleet:o.hide_render=flags[o.name]
cam.location,cam.rotation_euler,cam.scale=cm;cam.data.ortho_scale=ortho;s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;volume_range('saved-map-camera');bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v15-readable.blend'))
