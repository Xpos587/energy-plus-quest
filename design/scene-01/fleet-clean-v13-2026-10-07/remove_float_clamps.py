import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v13-clean.blend'))
removed=[]
for o in list(bpy.data.objects):
 if o.name.startswith('V12 ') and any(x in o.name for x in ('exhaust visible clamp','exhaust cab mounting bracket')):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
for i in (1,4):
 m=bpy.data.materials[f'V12 {i} bright sill'];n=m.node_tree.nodes;l=m.node_tree.links;scuff=[x for x in n if x.type=='MIX_RGB' and x.blend_type=='MIX'][-1];noise=next(x for x in n if x.type=='TEX_NOISE');noise.inputs['Scale'].default_value=3
 ramp=n.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.3;ramp.inputs['From Max'].default_value=.72;ramp.inputs['To Min'].default_value=0;ramp.inputs['To Max'].default_value=.28;l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],scuff.inputs[0])
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v13-clean.blend'))
r=json.loads((P/'change-receipt.json').read_text());r['removed_floating_added_mounts']=removed;r['cab_wear']='Continuous restrained irregular fade; hard rectangular wear masks removed';(P/'change-receipt.json').write_text(json.dumps(r,indent=2))
