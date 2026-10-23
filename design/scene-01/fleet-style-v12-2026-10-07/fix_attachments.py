import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v12-style.blend'));s=bpy.context.scene
changed=[]
for o in bpy.data.objects:
 if o.name.startswith('V08 2 refrigeration') or o.name=='V08 2 vent recess':o.location.x-=.38;changed.append(o.name)
# Mounted to the cab roof, not suspended above its mesh.
hatch=bpy.data.objects['V08 4 older rectangular roof hatch'];hatch.location.z-=.21
# Canvas patches have irregular hand-cut corners, unlike roof vents.
for o in bpy.data.objects:
 if 'roof canvas repair' in o.name:
  for v in o.data.vertices:
   if v.co.x>0 and v.co.y>0:v.co.x-=.23
   elif v.co.x<0 and v.co.y<0:v.co.y+=.20
 if 'roof visible stitch' in o.name:o.hide_render=True
# A few diagonal stitch marks in the corner identify sewn repairs at close scale.
for i in (1,4):
 root=bpy.data.objects[f'truck-{i}-trailer'];mat=bpy.data.materials[f'V12 {i} linen stitches']
 for j,x in enumerate((-4.6,-1.45)):
  for k in range(5):
   bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name=f'V12 {i} diagonal sewn patch stitch';o.parent=root;o.location=(x-.4+k*.17,(.12 if j else -.1)-.39,3.286);o.scale=(.028,.035,.008);o.rotation_euler.z=.6;o.data.materials.append(mat)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v12-style.blend'))
(P/'attachment-fix.json').write_text(json.dumps({'fridge_objects':changed,'fridge_local_x_shift':-.38,'housing_rear_local_x':.68,'trailer_front_local_x':.7,'overlap':.02,'yellow_hatch_local_z_shift':-.21},indent=2))
# Reusable final render script handles map and all close views.
