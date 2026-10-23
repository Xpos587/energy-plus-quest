"""Optional opaque illustration glazing with deterministic surface driver reliefs."""
import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;s=bpy.context.scene
for i in (1,2,3,4):
 root=bpy.data.objects[f'truck-{i}-tractor']
 glass=bpy.data.materials[f'PILOT {i} translucent cab glass'];n=glass.node_tree.nodes;l=glass.node_tree.links;out=next(x for x in n if x.type=='OUTPUT_MATERIAL');em=next(x for x in n if x.type=='EMISSION');em.inputs['Color'].default_value=(.22,.40,.48,1);l.new(em.outputs[0],out.inputs[0])
 for o in root.children:
  if 'driver head' not in o.name and 'driver torso' not in o.name: continue
  head='head' in o.name
  z=(2.22 if head else 1.98) if i!=4 else (1.99 if head else 1.74)
  plane=1.3967-(z-1.83)*(.1367/.82) if i!=4 else 1.4409-(z-1.5)*(.0531/.81)
  o.location.x=plane+.045;o.location.z=z;o.scale.x=.10 if head else .065
 bpy.context.view_layer.update()
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'painted-vehicles-driver-relief.blend'))
for f in (1,97,385):
 s.frame_set(f);s.render.filepath=str(O/f'trucks-relief-{f:04}.png');bpy.ops.render.render(write_still=True)
(O/'driver-relief-receipt.json').write_text(json.dumps({'source':'painted-vehicles-pilot.blend','change':'Opaque nonglossy blue glass; existing driver meshes moved into shallow native relief on windshield to avoid enclosed cab hiding figures and transparent crypto stipple. This is stylized illustration, not physically seated interior placement.','head_counts':[1,1,2,1],'routes_and_camera':'unchanged','frames':[1,97,385]},indent=2))
