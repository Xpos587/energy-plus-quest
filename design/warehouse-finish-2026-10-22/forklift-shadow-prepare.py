import bpy,json
from pathlib import Path
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';m=json.loads((R/'forklift-geometry-receipt.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-finish-v3.blend'));s=bpy.context.scene;x0,y0,x1,y1=m['source_crop_xyxy'];s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/1440;s.render.border_max_x=x1/1440;s.render.border_min_y=1-y1/1000;s.render.border_max_y=1-y0/1000;s.cycles.samples=16;s.cycles.use_denoising=False;s.cycles.seed=0
s.render.filepath=str(R/'forklift-shadow-on-crop.png');bpy.ops.render.render(write_still=True)
for row in m['objects']:bpy.data.objects[row['object']].hide_render=True
s.render.filepath=str(R/'forklift-shadow-off-crop.png');bpy.ops.render.render(write_still=True)
print('FORKLIFT_SHADOW_PAIR_COMPLETE')
