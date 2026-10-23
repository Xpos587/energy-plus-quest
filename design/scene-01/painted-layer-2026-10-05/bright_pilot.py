"""Bounded 12-second palette and continuity pilot, unchanged rig geometry."""
import bpy,json,sys
from pathlib import Path
O=Path(__file__).resolve().parent;P=O/'pilot-frames';P.mkdir(exist_ok=True);s=bpy.context.scene
palette={1:'c24630',2:'1779cf',3:'64aa54',4:'e5ba40'}
def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def color(h):return tuple(linear(int(h[j:j+2],16)/255) for j in (0,2,4))
for m in bpy.data.materials:
 if 'projected paint' not in m.name:continue
 i=int(m.name.split()[1]);n=m.node_tree.nodes;l=m.node_tree.links
 hsv=next(x for x in n if x.type=='SEPARATE_COLOR');mix=next(x for x in n if x.type=='MIX_RGB');em=next(x for x in n if x.type=='EMISSION')
 # Preserve the existing selected chromatic paint mask and original neutral/skin pixels.
 gain=n.new('ShaderNodeMath');gain.operation='MULTIPLY_ADD';gain.inputs[1].default_value=.18;gain.inputs[2].default_value=.82;l.new(hsv.outputs[2],gain.inputs[0])
 rgb=n.new('ShaderNodeRGB');rgb.outputs[0].default_value=color(palette[i])+(1,)
 mul=n.new('ShaderNodeVectorMath');mul.operation='SCALE';l.new(rgb.outputs[0],mul.inputs[0]);l.new(gain.outputs[0],mul.inputs['Scale']);l.new(mul.outputs[0],mix.inputs[2])
 floor=n.new('ShaderNodeVectorMath');floor.operation='MAXIMUM';floor.inputs[1].default_value=(.055,.075,.085);l.new(mix.outputs[0],floor.inputs[0]);l.new(floor.outputs[0],em.inputs['Color'])
s.eevee.taa_render_samples=8;s.eevee.taa_samples=8;s.render.resolution_x=1280;s.render.resolution_y=889;s.render.resolution_percentage=100;s.render.fps=24;s.render.use_freestyle=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'painted-vehicles-bright-12sec.blend'))
frames=[1,97,385,769] if '--stills' in sys.argv else range(1,289)
poses={};local_start={o.name:[list(r) for r in o.matrix_local] for o in s.objects if o.name.startswith('PILOT') and 'reconstructed' in o.name}
for f in frames:
 s.frame_set(f);s.render.filepath=str(P/f'{f:04}.png');bpy.ops.render.render(write_still=True)
 poses[str(f)]={o.name: {'position':list(o.location),'rotation':list(o.rotation_euler)} for o in s.objects if o.name.startswith('truck-')}
local_end={o.name:[list(r) for r in o.matrix_local] for o in s.objects if o.name in local_start}
receipt={'frames':list(frames),'dimensions':[1280,889],'fps':24,'samples':8,'palette_srgb':{str(k):'#'+v for k,v in palette.items()},'deep_linework_floor_linear':[.055,.075,.085],'cab_relative_transform_constant':local_start==local_end,'root_poses':poses,'limitations':['Archived texture body mask uses hue/saturation/value selection; light blue window reflections or blue clothing may also be selected. Neutral and skin hues remain outside body hue mask.','Baked detail is projected onto reconstructed meshes; this is a departure from approved truck cards.','Map-scale faces remain small; green painted pair requires front-facing evidence.']}
(O/('bright-stills-receipt.json' if '--stills' in sys.argv else 'bright-12sec-receipt.json')).write_text(json.dumps(receipt,indent=2))
print('BRIGHT PILOT COMPLETE',len(poses))
