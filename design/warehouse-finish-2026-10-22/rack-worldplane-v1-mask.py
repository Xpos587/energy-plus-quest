import bpy
from pathlib import Path
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'rack-worldplane-v1.blend'));s=bpy.context.scene;m=bpy.data.materials.new('rack-worldplane-v1 black context');m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,0,0,1);m.node_tree.links.new(em.outputs[0],out.inputs[0])
for o in list(bpy.data.objects):
 if o.type not in {'MESH','FONT','CURVE'}:continue
 if o.name.startswith('rack-worldplane-v1 '):continue
 o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(m)
 for slot in o.material_slots:slot.material=m
 if o.type=='MESH':
  for p in o.data.polygons:p.material_index=0
 for mod in o.modifiers:
  if hasattr(mod,'material'):mod.material=0
mat=bpy.data.materials['rack-worldplane-v1 immutable texture camera surface'];em=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
for link in list(em.inputs['Color'].links):mat.node_tree.links.remove(link)
em.inputs['Color'].default_value=(1,1,1,1);em.inputs['Strength'].default_value=1
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Strength'].default_value=0
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.cycles.samples=4;s.cycles.use_denoising=False;s.render.use_compositing=False;s.render.use_sequencer=False;s.render.filepath=str(R/'rack-worldplane-v1-visible-alpha-mask.png');bpy.ops.render.render(write_still=True)
