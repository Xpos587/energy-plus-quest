import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
for o in s.objects:
 if o.type not in ('CAMERA','LIGHT') and o not in fleet:o.hide_render=True
 if o.type=='LIGHT':o.hide_render=True
for o in fleet:o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False;o.visible_shadow=True
bpy.ops.mesh.primitive_plane_add(size=400,location=(0,0,-.002));g=bpy.context.object;g.name='v11 physical shadow receiver';g.is_shadow_catcher=True
mat=bpy.data.materials.new('v11 neutral receiver');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.8,.8,.8,1);bs.inputs['Roughness'].default_value=1;g.data.materials.append(mat)
ld=bpy.data.lights.new('v11 directional sky key','SUN');ld.energy=3;ld.angle=math.radians(8);l=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(l);l.location=(-40,35,70);l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
w=bpy.data.worlds.new('v11 diffuse sky');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs['Color'].default_value=(.68,.78,1,1);w.node_tree.nodes.get('Background').inputs['Strength'].default_value=.8;s.world=w
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=4;s.cycles.transparent_max_bounces=4;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.025
s.render.film_transparent=True;s.render.use_compositing=False;s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='16'
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v11-shadowcatcher.blend'))
(P/'shadow-receipt.json').write_text(json.dumps({'source':'fleet-v11-coupling.blend','method':'actual relocated fleet geometry Cycles shadow catcher; source hide_render preserved','sun_angle_degrees':8,'alpha_scale':.60,'tint_srgb':[83,91,96],'frames':[1,385,769],'samples':48,'dimensions':[1920,1334]},indent=2))
for f in [1,385,769]:s.frame_set(f);s.render.filepath=str(P/f'shadow-raw-{f:04}.png');bpy.ops.render.render(write_still=True)
