import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=Path('design/scene-01/truck-native-quality-2026-10-05/sources/GREEN-TURN-INTERVAL.json');d=json.loads(p.read_text());s=bpy.context.scene
roots=[bpy.data.objects[n] for n in ['truck-3-tractor','truck-3-trailer']];pts=[];pro=[]
for f in range(2,100):
 s.frame_set(f)
 for o in s.objects:
  if o.type=='MESH' and o.parent in roots and not o.hide_render:
   for b in o.bound_box:
    v=o.matrix_world@Vector(b);pts.append(v);pro.append(world_to_camera_view(s,s.camera,v))
d['suggested_presentation_interval_with_trailer_exit_settling']={'frames_inclusive':[2,99],'exit_sample':{o.name:{'xyz':list(o.location),'rotation_z_degrees_mod360':math.degrees(o.rotation_euler.z)%360} for o in roots},'world_xy_rectangle_with_1_unit_margin':{'xmin':min(v.x for v in pts)-1,'xmax':max(v.x for v in pts)+1,'ymin':min(v.y for v in pts)-1,'ymax':max(v.y for v in pts)+1},'existing_camera_normalized_crop':{'left':min(v.x for v in pro),'right':max(v.x for v in pro),'bottom':min(v.y for v in pro),'top':max(v.y for v in pro)}}
p.write_text(json.dumps(d,indent=2));print(json.dumps(d['suggested_presentation_interval_with_trailer_exit_settling'],indent=2))
