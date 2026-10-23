import bpy,math,json,time
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
roots=[bpy.data.objects[f'truck-{i}-{p}']for i in range(1,5)for p in ('tractor','trailer')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
mat=bpy.data.materials.new('V14 neutral shadow casting surface');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.4,.4,.4,1);bs.inputs['Roughness'].default_value=1
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
 elif o not in fleet and o.type not in ('CAMERA',):o.hide_render=True
for o in fleet:
 o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False;o.visible_shadow=True
 if 'light exhaust'in o.name:o.hide_render=True
 if o.type=='MESH':
  for j in range(len(o.data.materials)):o.data.materials[j]=mat
bpy.ops.mesh.primitive_plane_add(size=400,location=(0,0,-.002));g=bpy.context.object;g.name='V14 physical contact receiver';g.is_shadow_catcher=True;g.data.materials.append(mat)
ld=bpy.data.lights.new('V14 sun aligned to body shade','SUN');ld.energy=3;ld.angle=math.radians(9);sun=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(sun);sun.location=(-40,35,70);sun.rotation_euler=(-sun.location).to_track_quat('-Z','Y').to_euler()
w=bpy.data.worlds.new('V14 diffuse sky fill');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs['Color'].default_value=(.72,.82,1,1);w.node_tree.nodes.get('Background').inputs['Strength'].default_value=.9;s.world=w
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.max_bounces=3;s.cycles.transparent_max_bounces=2
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 s.cycles.device='GPU'
except Exception as e:print('GPU fallback',e)
s.render.film_transparent=True;s.render.use_compositing=False;s.render.resolution_percentage=50;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.view_settings.view_transform='Standard';s.view_settings.look='None';timings=[]
for frame in (385,1):
 t=time.monotonic();s.frame_set(frame);s.render.filepath=str(P/f'physical-shadow-{frame:04}.png');bpy.ops.render.render(write_still=True);timings.append({'frame':frame,'seconds':time.monotonic()-t})
(P/'physical-shadow-receipt.json').write_text(json.dumps({'method':'Cycles actual mesh shadow catcher including tyre contact and fifth wheel','samples':8,'sun':[-40,35,70],'sun_angle_deg':9,'sky_fill':.9,'resolution_percentage':50,'timings':timings},indent=2))
