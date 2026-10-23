import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
s=bpy.context.scene
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')]
fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
for o in s.objects:
 if o.type not in ('CAMERA','LIGHT') and o not in fleet:o.hide_render=True
 if o.type=='LIGHT':o.hide_render=True
for o in fleet:
 o.visible_camera=False
 o.visible_glossy=False
 o.visible_transmission=False
 o.visible_shadow=True
bpy.ops.mesh.primitive_plane_add(size=400,location=(0,0,-.002))
g=bpy.context.object;g.name='v10 real tyre contact shadowcatcher';g.is_shadow_catcher=True
mat=bpy.data.materials.new('v10 matte neutral receiver');mat.diffuse_color=(.8,.8,.8,1);mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.8,.8,.8,1);bs.inputs['Roughness'].default_value=1
g.data.materials.append(mat)
ld=bpy.data.lights.new('v10 directional sky key','SUN');ld.energy=3.0;ld.angle=math.radians(5)
l=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(l);l.location=(-40,35,70);l.rotation_euler=(Vector((0,0,0))-l.location).to_track_quat('-Z','Y').to_euler()
w=bpy.data.worlds.new('v10 diffuse blue sky');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs['Color'].default_value=(.68,.78,1,1);w.node_tree.nodes.get('Background').inputs['Strength'].default_value=.8;s.world=w
s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=4;s.cycles.transparent_max_bounces=4;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.025
s.render.film_transparent=True;s.render.use_compositing=False
s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='16'
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v10-real-shadowcatcher.blend'))
receipt={'source':'../fleet-style-v08-2026-10-07/projected/clean/fleet-v09-clean-sill.blend','method':'Cycles real geometry shadow catcher, camera-invisible fleet, horizontal receiver at tyre z=0; diffuse sky + single SUN','camera':{'name':s.camera.name,'location':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'ortho_scale':s.camera.data.ortho_scale},'ground_z':-.002,'key':{'position':list(l.location),'rotation':list(l.rotation_euler),'energy':ld.energy,'angular_diameter_deg':5},'frames':[1,385,769],'resolution':[1920,1334],'samples':48,'preserved':'all source vehicle roots, mesh geometry, materials, animation data, camera transform unchanged; pass camera ray visibility only altered','source_issue':'Cryptomatte Matte replaces Combined alpha, omitting ground shadows; source overhead sun has no shadows.'}
(P/'shadow-receipt.json').write_text(json.dumps(receipt,indent=2))
s.render.filepath=str(P/'shadow-raw-0001.png');bpy.ops.render.render(write_still=True)
