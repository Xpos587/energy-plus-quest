import bpy, math, pathlib
from mathutils import Vector
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=2200;s.render.resolution_y=2200;s.render.resolution_percentage=100
s.world.color=(.5,.5,.5)
mat=bpy.data.materials.new('gray');mat.diffuse_color=(.46,.59,.5,1)
for i,f in enumerate(sorted((P/'sources/scania-r730-paolo').glob('*.stl'),key=lambda f:int(f.stem.split('-')[1]))):
 bpy.ops.wm.stl_import(filepath=str(f));o=bpy.context.object;o.name=f.stem
 vs=[Vector(v) for v in o.bound_box];lo=Vector(tuple(min(v[j] for v in vs) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vs) for j in range(3)));d=hi-lo;scale=2.4/max(d)
 for v in o.data.vertices:v.co=(v.co-(lo+hi)/2)*scale
 x=(i%8)*3.5;y=-(i//8)*3.5;o.location=(x,y,1.3);o.data.materials.append(mat)
 bpy.ops.object.text_add(location=(x-1.3,y-1.5,.1));t=bpy.context.object;t.data.body=f.stem;t.data.size=.32
bpy.ops.object.camera_add(location=(12,-12,60));c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=29;c.rotation_euler=(0,0,0);s.camera=c
bpy.ops.object.light_add(type='AREA',location=(8,-6,30));bpy.context.object.data.energy=16000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=20
s.render.filepath=str(P/'native/import-sheet.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/import-sheet.blend'));bpy.ops.render.render(write_still=True)
