import bpy,math,json
from pathlib import Path
P=Path(__file__).resolve().parent
s=bpy.context.scene
bpy.data.lights['v10 directional sky key'].angle=math.radians(8)
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v10-real-shadowcatcher.blend'))
r=json.loads((P/'shadow-receipt.json').read_text());r['key']['angular_diameter_deg']=8;r['composite']={'alpha_scale':.60,'shadow_tint_srgb':[64,101,129],'semantics':'straight RGBA tinted physical shadow coverage; standard shadow alpha-over then vehicle alpha-over','vehicle_light_change':False};(P/'shadow-receipt.json').write_text(json.dumps(r,indent=2))
for frame in (1,385,769):
 s.frame_set(frame);s.render.filepath=str(P/f'shadow-raw-{frame:04}.png');bpy.ops.render.render(write_still=True)
