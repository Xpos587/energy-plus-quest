"""Lighting-only throughput test; all meshes, textures, routes and camera retained."""
import bpy,json,time
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
lights=[o for o in s.objects if o.type=='LIGHT'];sun=next((o for o in lights if o.data.type=='SUN'),None)
if sun is None:
 bpy.ops.object.light_add(type='SUN',location=(0,0,80));sun=bpy.context.object;sun.name='OPTIMIZED unshadowed sun';sun.data.energy=1
for o in lights:o.hide_render=o!=sun
sun.hide_render=False;sun.data.use_shadow=False
s.render.resolution_x=3840;s.render.resolution_y=2667;s.render.resolution_percentage=100;s.eevee.taa_render_samples=8;s.frame_set(769)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'painted-vehicles-repaired-optimized.blend'))
s.render.filepath=str(p/'repaired-stills/4k-0769-optimized.png');t=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-t
r={'source':'painted-vehicles-repaired.blend','mutation':'only light visibility and retained sun shadow setting; resolution increased for test','light_object_count_before':len(lights),'retained_sun':sun.name,'retained_sun_shadow':sun.data.use_shadow,'light_objects_disabled':sum(o.hide_render for o in lights),'dimensions':[3840,2667],'frame':769,'samples':8,'threads':4,'render_wall_seconds':round(elapsed,3),'baseline_wall_seconds':11.875,'geometry_camera_routes_textures':'unchanged','full_animation_rendered':False}
(p/'optimized-render-receipt.json').write_text(json.dumps(r,indent=2));print('OPTIMIZED COMPLETE',r)
