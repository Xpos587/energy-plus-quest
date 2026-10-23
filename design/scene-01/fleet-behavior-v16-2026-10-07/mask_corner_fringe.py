import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
for fn in ('fleet-v16.blend','fleet-v16-motion.blend'):
 bpy.ops.wm.open_mainfile(filepath=str(P/fn))
 for i in (1,4):
  o=bpy.data.objects[f'V14 {i} seated lower windshield gasket']
  for v in o.data.vertices:v.co.y/=1.18;v.co.z/=2.4
  o.location.x=1.815;o.location.z=1.413
  m=bpy.data.materials[f'V02 {i} Permanent high-detail two-driver windshield.001'];ns=m.node_tree.nodes;ls=m.node_tree.links;e=next(n for n in ns if n.type=='EMISSION');src=e.inputs[0].links[0].from_socket
  bw=ns.new('ShaderNodeRGBToBW');ls.new(src,bw.inputs[0]);light=ns.new('ShaderNodeMath');light.operation='GREATER_THAN';light.inputs[1].default_value=.65;ls.new(bw.outputs[0],light.inputs[0]);tc=ns.new('ShaderNodeTexCoord');sep=ns.new('ShaderNodeSeparateXYZ');ls.new(tc.outputs['Object'],sep.inputs[0]);low=ns.new('ShaderNodeMath');low.operation='LESS_THAN';low.inputs[1].default_value=.10;ls.new(sep.outputs['Z'],low.inputs[0]);mask=ns.new('ShaderNodeMath');mask.operation='MULTIPLY';ls.new(low.outputs[0],mask.inputs[0]);ls.new(light.outputs[0],mask.inputs[1]);mix=ns.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.12,.20,.24,1);ls.new(mask.outputs[0],mix.inputs[0]);ls.new(src,mix.inputs[1]);ls.new(mix.outputs[0],e.inputs[0])
 bpy.ops.wm.save_as_mainfile(filepath=str(P/fn))
