"""Bounded native surface pilot; authored paths/camera preserved; no raster painting."""
import bpy,json,math
from pathlib import Path
OUT=Path(__file__).resolve().parent
s=bpy.context.scene
roots=[o for o in s.objects if o.name.startswith('truck-')]
vehicles=set(roots)
for root in roots: vehicles.update(root.children_recursive)
original_camera={'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'ortho_scale':s.camera.data.ortho_scale}
original_routes={o.name: {'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None} for o in roots}
def paint(name,color,wear=0):
 m=bpy.data.materials.new('PILOT '+name); m.use_nodes=True
 n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 out=n.new('ShaderNodeOutputMaterial'); em=n.new('ShaderNodeEmission'); l.new(em.outputs[0],out.inputs[0])
 geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.22,-.36,.9);l.new(geo.outputs['Normal'],dot.inputs[0])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=tuple(c*.73 for c in color)+(1,);ramp.color_ramp.elements[1].position=.9;ramp.color_ramp.elements[1].color=tuple(color)+(1,);l.new(dot.outputs['Value'],ramp.inputs[0]);final=ramp.outputs[0]
 if wear:
  coords=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=38;noise.inputs['Detail'].default_value=2;l.new(coords.outputs['Generated'],noise.inputs['Vector'])
  tint=n.new('ShaderNodeValToRGB');tint.color_ramp.elements[0].color=(.90,.90,.90,1);tint.color_ramp.elements[1].color=(1,1,1,1);l.new(noise.outputs['Fac'],tint.inputs[0])
  mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=wear;l.new(final,mul.inputs[1]);l.new(tint.outputs[0],mul.inputs[2]);final=mul.outputs[0]
 l.new(final,em.inputs[0]); return m
colors={1:(.64,.135,.09),2:(.045,.32,.70),3:(.10,.51,.275),4:(.88,.57,.12)}
body={i:paint(f'{i} clean enamel',colors[i],.45 if i in (1,4) else .15) for i in colors}
cargo={i:paint(f'{i} warm woven trailer',(.90,.83,.66) if i in (1,4) else (.91,.93,.89),.5) for i in colors}
metal=paint('soft slate fittings',(.28,.39,.43));rubber=paint('blue charcoal tyres',(.065,.105,.13));lamp=paint('cream headlights',(.98,.88,.57));skin=paint('driver skin',(.82,.52,.31));shirt=paint('driver blue shirt',(.05,.21,.39));hair=paint('driver hair',(.18,.12,.08));glass=paint('glazing blue',(.30,.53,.62))
for o in vehicles:
 if o.type not in ('MESH','FONT'): continue
 root=o
 while root.parent:root=root.parent
 i=int(root.name.split('-')[1]);mat=body[i]
 name=o.name.lower()
 if any(t in name for t in ('trailer','rear doors')) and not any(t in name for t in ('chassis','guard','lower rail')):mat=cargo[i]
 if any(t in name for t in ('metal','grille','hub','step','locking bar','buckle','fuel tank','door handle','door seam','exhaust','chassis','mirror arm','lower rail','side guard')):mat=metal
 if any(t in name for t in ('tire','rim recess','radiator','fifth wheel','mirror')) and 'arm' not in name:mat=rubber
 if 'lamp' in name:mat=lamp
 if 'driver head' in name:mat=skin
 if 'driver torso' in name:mat=shirt
 if 'window' in name or 'windshield' in name:mat=glass
 if o.type=='FONT':mat=metal
 for slot in o.material_slots:slot.link='OBJECT';slot.material=mat
# Native interior figures: copy existing seated crew geometry into three other cabs.
head=bpy.data.objects['FIX crew driver head'];torso=bpy.data.objects['FIX crew driver torso']
for i in (1,2,4):
 root=bpy.data.objects[f'truck-{i}-tractor'];dz=-.37 if i==4 else -.1
 for source in (head,torso):
  o=source.copy();o.data=source.data.copy();s.collection.objects.link(o);o.name=f'PILOT {i} '+('driver head' if source==head else 'driver torso');o.parent=root;o.location=source.location.copy();o.location.z+=dz;vehicles.add(o)
# Glazing as tinted transparent surface permits exact figure count while preserving cab.
for i in colors:
 m=bpy.data.materials.new(f'PILOT {i} translucent cab glass');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 out=n.new('ShaderNodeOutputMaterial');trans=n.new('ShaderNodeBsdfTransparent');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.22,.43,.56,1);mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.24;l.new(trans.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0]);m.surface_render_method='DITHERED'
 for o in vehicles:
  if o.name.startswith(str(i)+' ') and any(t in o.name for t in ('windshield','side window')):
   for slot in o.material_slots:slot.material=m
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=2048;s.render.resolution_y=1422;s.render.resolution_percentage=100;s.render.use_freestyle=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
vl=s.view_layers[0];vl.use_pass_cryptomatte_object=True;vl.pass_cryptomatte_depth=6
# Blender 5 compositor group; crypto works against the complete city beauty pass.
tree=bpy.data.node_groups.new('PILOT city-occluded vehicles','CompositorNodeTree');tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');s.compositing_node_group=tree
n=tree.nodes;l=tree.links;rl=n.new('CompositorNodeRLayers');rl.layer=vl.name
crypto=n.new('CompositorNodeCryptomatteV2');crypto.source='RENDER';crypto.scene=s;crypto.layer_name=vl.name+'.CryptoObject';crypto.matte_id=', '.join(o.name for o in vehicles if o.type in ('MESH','FONT'))
l.new(rl.outputs['Image'],crypto.inputs['Image'])
alpha=n.new('CompositorNodeSetAlpha');alpha.inputs['Type'].default_value='Replace Alpha';l.new(rl.outputs['Image'],alpha.inputs['Image']);l.new(crypto.outputs['Matte'],alpha.inputs['Alpha']);output=n.new('NodeGroupOutput');l.new(alpha.outputs['Image'],output.inputs['Image'])
receipt={'source':'design/scene-01/controlled-motion-2026-10-04/v2b/controlled-straight-start.blend','camera':original_camera,'routes':original_routes,'frames':[1,97,385],'dimensions':[2048,1422],'driver_head_geometry_counts':{str(i):sum(1 for o in vehicles if 'driver head' in o.name and o.parent==bpy.data.objects[f'truck-{i}-tractor']) for i in colors},'treatment':'native soft orientation shading; emission removes gloss and cast shadows; subtle generated enamel variation; no raster textures','occlusion':'Cryptomatte against full native city','limitations':['No AI painted cab textures exist in this frozen source; fine detail comes from existing native fittings.','Native cabin opaque shell may occlude interior figures at some headings; head geometry counts do not establish face readability.','No ground shadow pass: user requires shadow-free artwork.']}
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2))
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'painted-vehicles-pilot.blend'))
for frame in (1,97,385):
 s.frame_set(frame);s.render.filepath=str(OUT/f'trucks-{frame:04}.png');bpy.ops.render.render(write_still=True)
print('PILOT COMPLETE',receipt['driver_head_geometry_counts'])
