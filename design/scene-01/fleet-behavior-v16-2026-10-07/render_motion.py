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

dest=P/"turn-vehicles";dest.mkdir(exist_ok=True)
for f in range(1,193):
 s.frame_set(f);volume_range(str(f));s.render.filepath=str(dest/f"{f:04d}.png");bpy.ops.render.render(write_still=True);print("FRAME",f,flush=True)
