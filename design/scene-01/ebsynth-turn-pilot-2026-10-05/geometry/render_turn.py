import bpy,json,math
from pathlib import Path
O=Path(__file__).parent;s=bpy.context.scene
for d in ('vehicleframes','normalframes'): (O/d).mkdir(exist_ok=True)
s.view_layers[0].use_pass_normal=True
T=bpy.data.node_groups.new('guide color and normals','CompositorNodeTree');T.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');s.compositing_node_group=T
n=T.nodes;l=T.links
rl=n.new('CompositorNodeRLayers');out=n.new('NodeGroupOutput');l.new(rl.outputs['Image'],out.inputs[0])
# Map signed camera-independent world normals [-1,1] into RGB [0,1].
mul=n.new('ShaderNodeVectorMath');mul.operation='SCALE';mul.inputs[3].default_value=.5;l.new(rl.outputs['Normal'],mul.inputs[0])
add=n.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.5,.5,.5);l.new(mul.outputs['Vector'],add.inputs[0])
a=n.new('CompositorNodeSetAlpha');l.new(add.outputs[0],a.inputs['Image']);l.new(rl.outputs['Alpha'],a.inputs['Alpha'])
f=n.new('CompositorNodeOutputFile');print('FILE_API', [x for x in dir(f) if 'slot' in x or 'item' in x or 'path' in x or 'directory' in x]);
if hasattr(f,'file_slots'):
 f.base_path=str(O/'normalframes');f.file_slots[0].path='normal-';f.format.file_format='PNG';f.format.color_mode='RGBA'
else:
 f.directory=str(O/'normalframes');f.file_name='normal-';item=f.file_output_items.new('RGBA','normal');item.override_node_format=True;item.format.file_format='PNG';item.format.color_mode='RGBA'
l.new(a.outputs[0],f.inputs[0])
roots=[bpy.data.objects[n] for n in ('truck-3-tractor','truck-3-trailer')]
records=[]
for i in range(72):
 frame=85+(217-85)*i/71;s.frame_set(int(frame),subframe=frame%1)
 s.render.filepath=str(O/'vehicleframes'/f'{i:04}.png');f.file_name=f'{i:04}'
 records.append({'index':i,'source_frame':frame,'tractor_heading_deg':math.degrees(roots[0].rotation_euler.z),'trailer_heading_deg':math.degrees(roots[1].rotation_euler.z),'root_matrices':{r.name:[list(row) for row in r.matrix_world] for r in roots}})
 bpy.ops.render.render(write_still=True)
 print('GUIDE_FRAME',i,flush=True)
(O/'transform-receipt.json').write_text(json.dumps(records,indent=2))
