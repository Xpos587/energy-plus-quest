import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v12-style.blend'))
colors={1:(.70,.07,.05),2:(.03,.22,.62),3:(.18,.50,.07),4:(.93,.50,.035)}
for i,c in colors.items():
 m=bpy.data.materials[f'V12 {i} '+('woven pale canvas' if i in (1,4) else 'clean porcelain cargo')];mult=next(n for n in m.node_tree.nodes if n.type=='MIX_RGB');mult.inputs[1].default_value=(*c,1)
 # Use the same shaded body pigment on front, rear and roof edge material slots.
 for o in bpy.data.objects:
  if o.parent and o.parent.name==f'truck-{i}-trailer':
   for slot in o.material_slots:
    if slot.material and slot.material.name in (f'{i} clay cargo',f'V12 {i} clean porcelain cargo',f'V12 {i} woven pale canvas'):slot.material=m
 if i in (1,4):
  faded=tuple(v*.60+.16 for v in c)
  m=bpy.data.materials[f'V12 {i} repair patch'];next(n for n in m.node_tree.nodes if n.type=='MIX_RGB').inputs[1].default_value=(*faded,1)
  m=bpy.data.materials[f'V12 {i} canvas fold'];next(n for n in m.node_tree.nodes if n.type=='MIX_RGB').inputs[1].default_value=(*(v*.73 for v in c),1)
  # Two broad abrasions across the lower colored band, preserving the windshield.
  m=bpy.data.materials[f'V12 {i} bright sill'];n=m.node_tree.nodes;l=m.node_tree.links;scuff=[x for x in n if x.type=='MIX_RGB' and x.blend_type=='MIX'][-1]
  coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Generated'],sep.inputs[0]);masks=[]
  for lo,hi in ((.08,.28),(.62,.83)):
   a=n.new('ShaderNodeMath');a.operation='GREATER_THAN';a.inputs[1].default_value=lo;l.new(sep.outputs['Y'],a.inputs[0]);b=n.new('ShaderNodeMath');b.operation='LESS_THAN';b.inputs[1].default_value=hi;l.new(sep.outputs['Y'],b.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(a.outputs[0],mul.inputs[0]);l.new(b.outputs[0],mul.inputs[1]);masks.append(mul.outputs[0])
  add=n.new('ShaderNodeMath');add.operation='ADD';l.new(masks[0],add.inputs[0]);l.new(masks[1],add.inputs[1]);noise=next(x for x in n if x.type=='TEX_NOISE');noise.inputs['Scale'].default_value=3
  mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(add.outputs[0],mul.inputs[0]);l.new(noise.outputs['Fac'],mul.inputs[1]);l.new(mul.outputs[0],scuff.inputs[0]);scuff.inputs[2].default_value=(.42,.40,.32,1)
  for j in range(3):
   m=bpy.data.materials[f'V10 {i} soft connected exhaust {j}']
   for n in m.node_tree.nodes:
    if n.type=='MATH' and n.operation=='MULTIPLY':n.inputs[1].default_value*=1.3
    elif n.type=='EMISSION':n.inputs[0].default_value=(.37,.40,.40,1)
# Slightly brighter two-person windshield; identity and count image remains untouched.
m=bpy.data.materials.get('V02 3 Permanent high-detail two-driver windshield.001')
if m and m.use_nodes:
 n=m.node_tree.nodes;l=m.node_tree.links
 for dst in list(n):
  if dst.type in ('EMISSION','BSDF_DIFFUSE') and dst.inputs['Color'].is_linked:
   src=dst.inputs['Color'].links[0].from_socket;g=n.new('ShaderNodeGamma');g.inputs[1].default_value=.92;l.new(src,g.inputs[0]);sat=n.new('ShaderNodeHueSaturation');sat.inputs['Saturation'].default_value=1.08;l.new(g.outputs[0],sat.inputs['Color']);l.new(sat.outputs[0],dst.inputs['Color'])
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v12-style.blend'))
