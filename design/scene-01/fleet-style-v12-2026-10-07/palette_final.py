import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v12-style.blend'))
palette={1:(.70,.07,.05),2:(.03,.22,.62),3:(.18,.50,.07),4:(.93,.50,.035)}
for i,color in palette.items():
 m=bpy.data.materials[f'V09 {i} painted cab front roof near side'];n=[n for n in m.node_tree.nodes if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY'][-1];n.inputs[1].default_value=(*color,1)
 m=bpy.data.materials[f'V12 {i} bright sill'];n=[n for n in m.node_tree.nodes if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY'][0];n.inputs[1].default_value=(*color,1)
 if i in (1,4):
  for n in m.node_tree.nodes:
   if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=4
  m=bpy.data.materials[f'V12 {i} woven pale canvas'];n=[n for n in m.node_tree.nodes if n.type=='MIX_RGB'][0];n.inputs[1].default_value=(.80,.77,.65,1)
  m=bpy.data.materials[f'V12 {i} repair patch'];n=[n for n in m.node_tree.nodes if n.type=='MIX_RGB'][0];n.inputs[1].default_value=(.42,.45,.36,1)
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v12-style.blend'))
