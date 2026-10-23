"""Scenario separation: lower old roofs; existing original exhaust hardware only."""
import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;ROOT=O.parents[3];s=bpy.context.scene
source=ROOT/'design/scene-01/truck-native-quality-2026-10-05/image-to-3d/green-tractor-detailed.blend'
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=['Mesh_0']
base=dst.objects[0];oldroof=[];exhaust=[]
for i,factor in ((1,.30),(4,.22)):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];before=[min(v.co.z for v in o.data.vertices),max(v.co.z for v in o.data.vertices)];wind_delta=0;wheel_delta=0;n=0
 assert len(o.data.vertices)==len(base.data.vertices)
 for v,original in zip(o.data.vertices,base.data.vertices):
  co=original.co.copy()
  if co.z>.30:co.z=.30+(co.z-.30)*factor;n+=1
  v.co=co
  if original.co.z<=.248:wind_delta=max(wind_delta,(v.co-original.co).length)
  if original.co.z<0:wheel_delta=max(wheel_delta,(v.co-original.co).length)
 o.data.update();assert wind_delta==0 and wheel_delta==0
 stack=bpy.data.objects.get(f'{i} exhaust stack')
 if stack:stack.hide_render=False;exhaust.append(stack.name)
 oldroof.append({'truck':i,'roof_factor':factor,'pivot_z':.30,'roof_vertices_changed':n,'old_z_bounds':before,'new_z_bounds':[min(v.co.z for v in o.data.vertices),max(v.co.z for v in o.data.vertices)],'windshield_max_vertex_delta':wind_delta,'wheel_max_vertex_delta':wheel_delta})
bpy.data.objects.remove(base,do_unlink=True)
roots=[o for o in s.objects if o.name.startswith('truck-')];crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');crypto.matte_id=', '.join(o.name for r in roots for o in r.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
receipt={'parent_candidate':'fleet-textured-v02.blend','candidate':'fleet-textured-v06.blend','roof_records':oldroof,'restored_exhaust_hardware':exhaust,'exhaust_plumes':'No named smoke/puff/plume objects exist in frozen source. Nothing invented.','frames':[1,385,769],'dimensions':[1920,1334],'scenario':{'red':'lower older roof, beige trailer, one driver','yellow':'lowest older roof, beige trailer, one driver','blue':'tall modern roof, white trailer, one driver','green':'tall modern roof, white trailer, two crew'},'limitations':['Old red/yellow identity is approximated with compressed modern base; exact card shapes remain unmodelled.','Driver details remain permanent projected windshield textures.']}
(O/'textured-v06-receipt.json').write_text(json.dumps(receipt,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'fleet-textured-v06.blend'))
for f in (1,385,769):s.frame_set(f);s.render.filepath=str(O/f'textured-v06-vehicles-{f:04}.png');bpy.ops.render.render(write_still=True)
print('TEXTURED V06 PILOT COMPLETE')
