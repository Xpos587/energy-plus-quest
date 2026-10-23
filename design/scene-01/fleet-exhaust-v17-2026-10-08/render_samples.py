import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;cam=s.camera
s.render.resolution_percentage=100;s.eevee.volumetric_tile_size='2';s.eevee.volumetric_samples=128;s.eevee.use_volume_custom_range=True
ranges=[]
for f in (48,96,144):
 s.frame_set(f);bpy.context.view_layer.update();inv=cam.matrix_world.inverted()
 depths=[-(inv@o.matrix_world@Vector(v)).z for o in bpy.data.collections['V17 worldspace exhaust puffs'].objects for v in o.bound_box]
 s.eevee.volumetric_start=min(depths)-2;s.eevee.volumetric_end=max(depths)+2
 ranges.append({'frame':f,'start':min(depths)-2,'end':max(depths)+2})
 s.render.filepath=str(P/f'vehicles-{f:04}.png');bpy.ops.render.render(write_still=True)
(P/'sample-volume-ranges.json').write_text(json.dumps(ranges,indent=2))
