import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'rack-open-cap-preparation-v1.blend'));s=bpy.context.scene;c=s.camera
points=[('front-left-top',(1.5275,3.5275,2.7)),('front-middle-top',(2.4,3.5275,2.7)),('front-right-top',(3.2725,3.5275,2.7)),('back-left-top',(1.5275,4.6725,2.7)),('back-right-top',(3.2725,4.6725,2.7)),('front-left-foot',(1.5275,3.5275,0)),('front-middle-foot',(2.4,3.5275,0)),('front-right-foot',(3.2725,3.5275,0)),('back-right-foot',(3.2725,4.6725,0))];rows=[]
for name,p in points:
 v=world_to_camera_view(s,c,Vector(p));rows.append({'name':name,'world':p,'source_xy':[v.x*1440,(1-v.y)*1000]})
(R/'rack-registration-targets-v1.json').write_text(json.dumps(rows,indent=2))
