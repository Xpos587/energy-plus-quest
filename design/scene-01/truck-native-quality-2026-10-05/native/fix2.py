import bpy,pathlib
from mathutils import Vector
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05');O=P/'native';bpy.ops.wm.open_mainfile(filepath=str(O/'scania-corrected-gate.blend'));s=bpy.context.scene
old=bpy.data.objects['SCANIA integrated curved high roof'];bpy.data.objects.remove(old,do_unlink=True);bpy.ops.wm.stl_import(filepath=str(P/'sources/scania-r730-paolo/r730-46.stl'));o=bpy.context.object;o.name='SCANIA integrated curved high roof'
for v in o.data.vertices:x,y,z=v.co;v.co=(x-55+.7,50-z,y+53)
o.data.materials.append(bpy.data.materials['Moderate sage green paint'])
for p in o.data.polygons:p.use_smooth=True
for yi in [130,182]:
 for side in [-1,1]:
  old=bpy.data.objects.get(f'Detailed tread tire {yi} {side}');bpy.data.objects.remove(old,do_unlink=True)
  src=bpy.data.objects[f'Detailed tread tire 8 {side}'];o=src.copy();o.data=src.data.copy();bpy.context.collection.objects.link(o);o.name=f'Detailed tread tire {yi} {side}';o.location.y=yi-8
# Hide all unmapped wheel rim20 source support bodies, replace with workingfront18.
for yi in [130,182]:
 for side in [-1,1]:
  old=bpy.data.objects.get(f'Embossed wheel rim {yi} {side}');bpy.data.objects.remove(old,do_unlink=True)
  src=bpy.data.objects[f'Embossed wheel rim 8 {side}'];o=src.copy();o.data=src.data.copy();bpy.context.collection.objects.link(o);o.name=f'Embossed wheel rim {yi} {side}';o.location.y=yi-8
c=bpy.data.objects['shape-gate-front-three-quarter'];s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(O/'shape-gate-assembled-v2.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-assembled-v2.blend'));bpy.ops.render.render(write_still=True)
