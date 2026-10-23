import bpy
from pathlib import Path
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-finish-2026-10-22';R=ROOT/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-finish-v2.blend'));S=bpy.context.scene
# Added upper body leans forward within unchanged guard; body and camera authority untouched.
for o in bpy.data.objects:
 if o.name.startswith('Finish driver ') and not any(s in o.name for s in ['thigh','shin','boot']):o.location.y-=.23
# Camera background is bright sky, independently from environment illumination.
w=S.world.node_tree;n=w.nodes;links=w.links;original=n['Background'];output=n['World Output'];path=n.new('ShaderNodeLightPath');camera=n.new('ShaderNodeBackground');camera.inputs['Color'].default_value=(.58,.79,.94,1);camera.inputs['Strength'].default_value=1;mix=n.new('ShaderNodeMixShader');links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);links.new(original.outputs[0],mix.inputs[1]);links.new(camera.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs[0])
S.cycles.samples=32;S.render.filepath=str(R/'source-v3-clean.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'warehouse-finish-v3.blend'));bpy.ops.render.render(write_still=True);print('FINISH V3 COMPLETE')
