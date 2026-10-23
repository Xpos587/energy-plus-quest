import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v12-style.blend'));s=bpy.context.scene
bpy.data.objects['V08 4 older rectangular roof hatch'].location.z-=.07
for i in (1,4):
 bpy.data.objects[f'{i} exhaust stack'].location.x+=.2
 for j in range(3):bpy.data.objects[f'V08 {i} light exhaust {j}'].location.x+=.2
for i in range(1,5):
 root=bpy.data.objects[f'truck-{i}-tractor'];mat=bpy.data.materials[f'V12 {i} clean hardware']
 for y in (-.4,.4):
  bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name=f'V12 {i} catwalk structural support';o.parent=root;o.location=(-1.62,y,.975);o.scale=(.35,.055,.125);o.data.materials.append(mat)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v12-style.blend'))
r=json.loads((P/'attachment-fix.json').read_text());r.update({'yellow_hatch_local_z_shift':-.28,'exhaust_stack_and_cloud_local_x_shift':.2,'catwalk_supports_per_truck':2,'fridge_all_frame_min_clearance_tractor_local':.25827048,'fridge_worst_frame':239});(P/'attachment-fix.json').write_text(json.dumps(r,indent=2))
