import bpy,json,time
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
palette={1:'e9563c',2:'218ee4',3:'85c753',4:'eabe43'}
def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def color(h):return tuple(linear(int(h[j:j+2],16)/255) for j in (0,2,4))
changed=[]
for m in bpy.data.materials:
 if 'projected paint' not in m.name:continue
 i=int(m.name.split()[1]);n=m.node_tree.nodes
 mix=next(x for x in n if x.type=='MIX_RGB')
 scale=mix.inputs[2].links[0].from_node
 gain=scale.inputs['Scale'].links[0].from_node
 rgb=scale.inputs[0].links[0].from_node
 assert gain.operation=='MULTIPLY_ADD' and rgb.type=='RGB'
 gain.inputs[1].default_value=.60;gain.inputs[2].default_value=.40
 rgb.outputs[0].default_value=color(palette[i])+(1,)
 changed.append(m.name)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(p/'lookdev-test-detail.blend'))
times={}
for f in (1,133,769):
 s.frame_set(f);s.render.filepath=str(p/f'lookdev-test-{f:04}.png');start=time.monotonic();bpy.ops.render.render(write_still=True);times[str(f)]=round(time.monotonic()-start,3)
(p/'lookdev-test-receipt.json').write_text(json.dumps({'candidate_only':True,'style_accepted':False,'source':'painted-vehicles-driver-fixed-optimized.blend','dimensions':[3840,2667],'samples':8,'changed_materials':changed,'value_gain':.60,'value_bias':.40,'palette_srgb':palette,'frames':times,'geometry_camera_routes_drivers_glazing':'unchanged','neutral_floor_skin_mask':'unchanged'},indent=2))
