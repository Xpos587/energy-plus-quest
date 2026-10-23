import bpy,pathlib,math
from mathutils import Vector
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05');bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1400;s.render.resolution_y=1000;s.world.color=(.5,.5,.5)
for k in [1,8,46,31,38,39,9,10,11]:
 f=next((P/'sources/scania-r730-paolo').glob('r730-'+str(k)+'.stl'));bpy.ops.wm.stl_import(filepath=str(f));o=bpy.context.object;o.name='Part'+str(k)
 for ob in bpy.context.scene.objects:ob.hide_render=(ob.type=='MESH' and ob!=o)
 vs=[Vector(v) for v in o.bound_box];lo=Vector(tuple(min(v[j] for v in vs) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vs) for j in range(3)));mid=(lo+hi)/2
 bpy.ops.object.camera_add(location=mid+Vector((150,-190,190)));c=bpy.context.object;c.rotation_euler=(mid-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=max(hi-lo)*1.7;s.camera=c
 bpy.ops.object.light_add(type='AREA',location=mid+Vector((60,-140,200)));bpy.context.object.data.energy=1200000;bpy.context.object.data.size=180
 s.render.filepath=str(P/f'native/part-{k}.png');bpy.ops.render.render(write_still=True)
