import bpy
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(385)
s.render.use_compositing=False;s.render.film_transparent=True
roots=[bpy.data.objects[f'truck-{i}-{p}']for i in range(1,5)for p in ('tractor','trailer')]
colors=[(1,.05,.02,1),(.02,.3,1,1),(.02,1,.1,1),(1,.8,.02,1)]
def emission(name):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m,e
for i in range(1,5):
 m,e=emission(f'ID {i}');e.inputs[0].default_value=colors[i-1]
 for root in roots[(i-1)*2:i*2]:
  for o in root.children_recursive:
   if o.type=='MESH':
    if 'exhaust' in o.name and 'stack'not in o.name:o.hide_render=True
    for j in range(len(o.data.materials)):o.data.materials[j]=m
s.render.filepath=str(P/'ids-0385.png');bpy.ops.render.render(write_still=True)
m,e=emission('world surface normals');n=m.node_tree.nodes;l=m.node_tree.links;g=n.new('ShaderNodeNewGeometry');mult=n.new('ShaderNodeVectorMath');mult.operation='MULTIPLY_ADD';mult.inputs[1].default_value=(.5,.5,.5);mult.inputs[2].default_value=(.5,.5,.5);l.new(g.outputs['Normal'],mult.inputs[0]);l.new(mult.outputs[0],e.inputs[0])
for root in roots:
 for o in root.children_recursive:
  if o.type=='MESH':
   for j in range(len(o.data.materials)):o.data.materials[j]=m
s.render.filepath=str(P/'normals-0385.png');bpy.ops.render.render(write_still=True)
