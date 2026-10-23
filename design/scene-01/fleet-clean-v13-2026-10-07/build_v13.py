import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent;SOURCE=P.parent/'fleet-style-v12-2026-10-07/fleet-v12-style.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
removed=[]
for o in list(bpy.data.objects):
 if o.name.startswith('V12 ') and any(k in o.name for k in ('canvas repair','visible stitch','sewn patch stitch')):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# The roof stays plain: gentle continuous sunfade, strongest close to long seams.
for i in (1,4):
 m=bpy.data.materials[f'V12 {i} woven pale canvas'];n=m.node_tree.nodes;l=m.node_tree.links;mult=next(x for x in n if x.type=='MIX_RGB');base=mult.inputs[1].default_value[:]
 coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Generated'],sep.inputs[0]);ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements.remove(r.elements[1]);r.elements[0].position=0;r.elements[0].color=(.16,.16,.16,1)
 for pos,v in ((.08,.06),(.24,.015),(.76,.015),(.92,.06),(1,.16)):r.elements.new(pos).color=(v,v,v,1)
 l.new(sep.outputs['Y'],ramp.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=base;mix.inputs[2].default_value=tuple(v*.7+.19 for v in base[:3])+(1,);l.new(ramp.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],mult.inputs[1])
# Compress the refrigeration assembly around its flush mounting plane.
changed=[]
for o in bpy.data.objects:
 if o.name.startswith('V08 2 refrigeration') or o.name=='V08 2 vent recess':
  o.location.x=.7+(o.location.x-.7)*.5;o.location.y*=.68;o.location.z=2.75+(o.location.z-2.64)*.60
  o.scale.x*=.5;o.scale.y*=.68;o.scale.z*=.60;changed.append(o.name)
body=bpy.data.materials['V12 2 clean porcelain cargo'].copy();body.name='V13 integrated blue refrigeration housing';next(n for n in body.node_tree.nodes if n.type=='MIX_RGB').inputs[1].default_value=(.065,.27,.65,1)
vents=body.copy();vents.name='V13 inset blue gray cooling grille';next(n for n in vents.node_tree.nodes if n.type=='MIX_RGB').inputs[1].default_value=(.16,.31,.43,1)
for name in changed:
 o=bpy.data.objects[name]
 for slot in o.material_slots:slot.material=vents if 'vent' in name else body
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v13-clean.blend'))
(P/'change-receipt.json').write_text(json.dumps({'source':str(SOURCE),'removed_objects':removed,'refrigeration_objects':changed,'refrigeration_transform':{'x_about_mount_plane_.7':.5,'y':.68,'z_about_2.64_to_2.75':.6},'roof':'No isolated repair rectangles or stitches; continuous low-strength fade along long edges','preserved':['matching cab and entire trailer colors','routes','coupling','crew','lighting','camera']},indent=2))
