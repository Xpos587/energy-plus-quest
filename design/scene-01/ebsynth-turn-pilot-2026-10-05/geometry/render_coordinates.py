"""Stable per-mesh Generated coordinate render; isolated source, camera and pose unchanged."""
import bpy,json,math
from pathlib import Path
O=Path(__file__).parent;D=O/'coordinateframes';D.mkdir(exist_ok=True)
s=bpy.context.scene
roots=[bpy.data.objects[n] for n in ('truck-3-tractor','truck-3-trailer')]
meshes=set()
for root in roots:meshes.update(o for o in root.children_recursive if o.type=='MESH' and not o.hide_render)
for o in meshes:
 m=bpy.data.materials.new('COORDINATE '+o.name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 t=n.new('ShaderNodeTexCoord');e=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(t.outputs['Generated'],e.inputs['Color']);l.new(e.outputs[0],out.inputs[0]);e.inputs['Strength'].default_value=1
 if not o.material_slots:o.data.materials.append(m)
 for slot in o.material_slots:slot.link='OBJECT';slot.material=m
s.compositing_node_group=None
s.view_settings.view_transform='Raw';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.film_transparent=True;s.render.use_freestyle=False
for i in range(72):
 frame=85+132*i/71;s.frame_set(int(frame),subframe=frame%1)
 s.render.filepath=str(D/f'{i:04}.png');bpy.ops.render.render(write_still=True)
 print('COORDINATE_FRAME',i,flush=True)
