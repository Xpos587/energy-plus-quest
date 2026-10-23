"""Append archived projected cab meshes, preserve native route rig and trailers."""
import bpy,json,math
from pathlib import Path
O=Path(__file__).resolve().parent;D=Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-21-live/atlas');s=bpy.context.scene
records=[]
for i,family in ((1,'old-cab'),(2,'near-cab'),(3,'crew-cab'),(4,'old-cab')):
 root=bpy.data.objects[f'truck-{i}-tractor']
 # Archive front body already includes its front tyres, lamps, grille, and mirrors.
 for o in root.children_recursive:
  name=o.name.lower()
  preserve=any(t in name for t in ('ladder frame','fifth wheel','rear mudguard'))
  if any(t in name for t in ('tire','rim recess','hub')):preserve=o.location.x<0
  if not preserve and o.type in ('MESH','FONT'):o.hide_render=True
 with bpy.data.libraries.load(str(D/f'{family}.blend'),link=False) as (src,dst):dst.objects=['Mesh_0']
 cab=dst.objects[0];s.collection.objects.link(cab);cab.name=f'PILOT {i} reconstructed {family}';cab.parent=root;cab.location=(0,0,0);cab.rotation_euler=(0,0,0);cab.animation_data_clear();cab.hide_render=False
 target_height={1:2.5806,2:2.5806,3:2.72646,4:2.09814}[i]*.85
 b=[(min(v.co[a] for v in cab.data.vertices),max(v.co[a] for v in cab.data.vertices)) for a in range(3)]
 factors=(2.61426*.85/(b[0][1]-b[0][0]),2.0196*.85/(b[1][1]-b[1][0]),target_height/(b[2][1]-b[2][0]))
 for v in cab.data.vertices:
  v.co.x=(v.co.x-b[0][0])*factors[0]-1.025
  v.co.y=(v.co.y-(b[1][0]+b[1][1])/2)*factors[1]
  v.co.z=(v.co.z-b[2][0])*factors[2]+.08
 cab.data.update();cab.scale=(1,1,1)
 for idx,previous in enumerate(list(cab.data.materials)):
  m=previous.copy();m.name=f'PILOT {i} projected paint {idx}';cab.data.materials[idx]=m
  n=m.node_tree.nodes;l=m.node_tree.links;tex=next(x for x in n if x.type=='TEX_IMAGE')
  if not tex.image.packed_file:
   tex.image.filepath=str(D.parent.parent/'pass-20-live'/Path(tex.image.filepath).name);tex.image.reload();tex.image.pack()
  em=next(x for x in n if x.type=='EMISSION')
  hsv=n.new('ShaderNodeSeparateColor');hsv.mode='HSV';l.new(tex.outputs['Color'],hsv.inputs[0])
  def threshold(op,socket,value):
   t=n.new('ShaderNodeMath');t.operation=op;l.new(socket,t.inputs[0]);t.inputs[1].default_value=value;return t.outputs[0]
  sat=threshold('GREATER_THAN',hsv.outputs[1],.07 if family=='old-cab' else .28)
  val=threshold('GREATER_THAN',hsv.outputs[2],.13 if family=='old-cab' else .12)
  hue_low=threshold('GREATER_THAN',hsv.outputs[0],.46);hue_hi=threshold('LESS_THAN',hsv.outputs[0],.72)
  mask=sat
  for socket in (val,hue_low,hue_hi):
   mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(mask,mul.inputs[0]);l.new(socket,mul.inputs[1]);mask=mul.outputs[0]
  rgb=n.new('ShaderNodeCombineColor');rgb.mode='HSV';rgb.inputs[0].default_value={1:.015,2:.57,3:.39,4:.12}[i];rgb.inputs[1].default_value=.67 if family=='old-cab' else .76;l.new(hsv.outputs[2],rgb.inputs[2])
  mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';l.new(mask,mix.inputs[0]);l.new(tex.outputs['Color'],mix.inputs[1]);l.new(rgb.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs['Color'])
 records.append({'truck':i,'family':family,'dimensions':[2.61426*.85,2.0196*.85,target_height],'mapping_scale':list(factors),'native_front_parts_hidden':True,'front_wheels':'archived mesh only','driver_source':'old painted single driver' if family=='old-cab' else 'crew painted pair; near requires one-driver opaque overlay'})
# Blue shares crew painted windows: overlay native glazing and one existing relief.
root=bpy.data.objects['truck-2-tractor']
for o in root.children:
 if o.name=='2 windshield':
  o.hide_render=False
  # Existing native face scaled into smaller archive windshield footprint.
  o.scale=(.85,.85,.85);o.location.x=-.07;o.location.z=-.10
  glass=bpy.data.materials['PILOT 2 translucent cab glass'];n=glass.node_tree.nodes;l=glass.node_tree.links;out=next(x for x in n if x.type=='OUTPUT_MATERIAL');em=next(x for x in n if x.type=='EMISSION');l.new(em.outputs[0],out.inputs[0])
 if 'PILOT 2 driver' in o.name:
  o.hide_render=False;o.location.x=.85*o.location.x-.07;o.location.y*=.85;o.location.z=.85*o.location.z-.10;o.scale*=.85
# Crypto selectors must be rebuilt from currently rendered truck meshes.
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2')
objects=[]
for root in [o for o in s.objects if o.name.startswith('truck-')]:objects.extend(o for o in root.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
crypto.matte_id=', '.join(o.name for o in objects)
s.render.use_freestyle=False;s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'painted-vehicles-reconstructed.blend'))
for f in (1,97,385):s.frame_set(f);s.render.filepath=str(O/f'trucks-reconstructed-{f:04}.png');bpy.ops.render.render(write_still=True)
(O/'reconstructed-receipt.json').write_text(json.dumps({'records':records,'camera_and_routes':'unchanged','textures':'archived source textures packed; no raster modification','tint':'HSV chroma selection with dark/neutral pixel exclusion','limitations':['Baked texture linework and shading remain present, although renderer outlines and cast shadows are disabled.','85 percent footprint changes cab-to-chassis alignment; first three frames only, not whole-loop verified.','Painted single/pair count depends on archived camera-projected views; green count must be inspected at headings with windshield visible.']},indent=2))
