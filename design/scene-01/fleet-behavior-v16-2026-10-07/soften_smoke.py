import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
for fn in ('fleet-v16.blend','fleet-v16-motion.blend'):
 bpy.ops.wm.open_mainfile(filepath=str(P/fn))
 for i in (1,4):
  o=bpy.data.objects[f'V02 DETAILED {i} complete tractor']
  for m in o.data.materials:
   if not m or 'windshield' in m.name.lower():continue
   for n in m.node_tree.nodes:
    if n.type=='MATH' and n.operation=='GREATER_THAN' and abs(n.inputs[1].default_value-.26)<.001:n.inputs[1].default_value=.025
  smoke=bpy.data.objects[f'V15 {i} connected exhaust plume'];m=smoke.data.materials[0];ns=m.node_tree.nodes;ls=m.node_tree.links
  vol=next(n for n in ns if n.type=='PRINCIPLED_VOLUME');vol.inputs['Color'].default_value=(.24,.27,.29,1)
  tc=ns.new('ShaderNodeTexCoord');noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5.5;noise.inputs['Detail'].default_value=3;ls.new(tc.outputs['Generated'],noise.inputs['Vector'])
  ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.30;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(1,1,1,1);ls.new(noise.outputs['Fac'],ramp.inputs[0])
  sep=ns.new('ShaderNodeSeparateXYZ');ls.new(tc.outputs['Generated'],sep.inputs[0]);fade=ns.new('ShaderNodeMapRange');fade.clamp=True;fade.inputs['From Min'].default_value=.45;fade.inputs['From Max'].default_value=1;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;ls.new(sep.outputs['Z'],fade.inputs[0])
  mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';ls.new(ramp.outputs[0],mul.inputs[0]);ls.new(fade.outputs[0],mul.inputs[1]);strength=ns.new('ShaderNodeMath');strength.operation='MULTIPLY';strength.inputs[1].default_value=3.3;ls.new(mul.outputs[0],strength.inputs[0]);ls.new(strength.outputs[0],vol.inputs['Density'])
 bpy.ops.wm.save_as_mainfile(filepath=str(P/fn))
