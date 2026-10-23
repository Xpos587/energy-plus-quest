import bpy
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
for i,col in ((2,(.035,.235,.61,1)),(3,(.18,.50,.075,1))):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];root=o.parent
 # Repair bright neutral source-texture fringe per shading point, never by triangle centroid.
 for m in o.data.materials:
  if not m or 'windshield' in m.name.lower():continue
  n=m.node_tree.nodes;l=m.node_tree.links
  for e in list(n):
   if e.type!='EMISSION' or not e.inputs[0].is_linked:continue
   src=e.inputs[0].links[0].from_socket;bw=n.new('ShaderNodeRGBToBW');l.new(src,bw.inputs[0]);ramp=n.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=.53;ramp.inputs['From Max'].default_value=.72;l.new(bw.outputs[0],ramp.inputs[0])
   geo=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Object'],sep.inputs[0]);high=n.new('ShaderNodeMath');high.operation='GREATER_THAN';high.inputs[1].default_value=.26;l.new(sep.outputs['Z'],high.inputs[0]);mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(high.outputs[0],mask.inputs[0]);l.new(ramp.outputs[0],mask.inputs[1]);mix=n.new('ShaderNodeMixRGB');l.new(mask.outputs[0],mix.inputs[0]);l.new(src,mix.inputs[1]);mix.inputs[2].default_value=col;l.new(mix.outputs[0],e.inputs[0])
 bpy.ops.mesh.primitive_cube_add();g=bpy.context.object;g.name=f'V14 {i} seated lower windshield gasket';g.scale=(.030,.851,.019);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);g.parent=root;g.location=(1.815,0,1.413);g.data.materials.append(bpy.data.materials['V14 satin charcoal trim']);b=g.modifiers.new('Soft gasket edge','BEVEL');b.width=.008;b.segments=3
for o in bpy.data.objects:
 if o.name.startswith(('V08 1 light exhaust','V08 4 light exhaust')):o.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
