import bpy
from pathlib import Path
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-finish-2026-10-22';R=ROOT/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-window-proof-v6.blend'));S=bpy.context.scene
mats=[]
for name,v in [('mask black',0),('mask white',1)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(v,v,v,1);em.inputs['Strength'].default_value=1;m.node_tree.links.new(em.outputs[0],out.inputs['Surface']);mats.append(m)
for o in bpy.data.objects:
 if o.type in {'MESH','FONT','CURVE'}:
  o.data.materials.clear();o.data.materials.append(mats[int(o.name.startswith('Finish window glass'))])
for n in S.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Strength'].default_value=0
S.view_settings.view_transform='Standard';S.view_settings.look='None';S.view_settings.exposure=0;S.cycles.samples=8;S.cycles.use_denoising=False;S.render.image_settings.color_mode='RGB';S.render.filepath=str(R/'window-v6-semantic-mask-render.png');bpy.ops.render.render(write_still=True);print('WINDOW SEMANTIC MASK COMPLETE')
