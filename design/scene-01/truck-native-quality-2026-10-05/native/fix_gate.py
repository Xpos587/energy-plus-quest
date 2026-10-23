import bpy,pathlib
from mathutils import Vector
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05');O=P/'native'
bpy.ops.wm.open_mainfile(filepath=str(O/'scania-native-candidate.blend'))
s=bpy.context.scene
# body1 native Z-up, frontage +Y. Roof46 coordinates continue cab Y span91..125.
for name,k in [('SCANIA curved cab with embossed door panels',1),('SCANIA integrated curved high roof',46),('SCANIA open windshield and sidewindow frame',31)]:
 old=bpy.data.objects.get(name);bpy.data.objects.remove(old,do_unlink=True)
 f=next((P/'sources/scania-r730-paolo').glob(f'r730-{k}.stl'));bpy.ops.wm.stl_import(filepath=str(f));o=bpy.context.object;o.name=name
 for v in o.data.vertices:
  x,y,z=v.co
  if k==1:v.co=(x-55,50-y,z+42)
  elif k==46:v.co=(x-55,50-y,z+42)
  else:v.co=(x-53.35,50-y-77,z+88)
 o.data.materials.append(bpy.data.materials.get('Moderate sage green paint') if k!=31 else bpy.data.materials.get('Medium slate grille'))
 for p in o.data.polygons:p.use_smooth=True
# source frame rails replaced by real detailed native subassembly later; hide malformed kit rails for current shape focus
for o in bpy.data.objects:
 if 'frame rail' in o.name:o.hide_render=True
 if 'rear mudguard' in o.name:
  # original xlength, yheight? correctarcsourceY height, sourceZwidth; usexlength alongtruck.
  for v in o.data.vertices:
   x,y,z=v.co
   # prior (side*(39+y), x+100, z+23); swapouty andz bodyheight
   side=-1 if '-1' in o.name else 1
   origy=abs(x)-39;origz=z-23;v.co=(side*(39+origz),y,origy+23)
# light level softened, material greener darker
m=bpy.data.materials.get('Moderate sage green paint');m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.18,.33,.22,1)
for o in bpy.data.objects:
 if o.type=='LIGHT':o.data.energy*=.4
c=bpy.data.objects['shape-gate-front-three-quarter'];s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(O/'shape-gate-corrected.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-corrected-gate.blend'));bpy.ops.render.render(write_still=True)
