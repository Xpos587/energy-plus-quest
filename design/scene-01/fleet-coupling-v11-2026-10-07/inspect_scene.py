import bpy,json
from mathutils import Vector
s=bpy.context.scene;s.frame_set(1)
for i in [1]:
 for part in ['tractor','trailer']:
  r=bpy.data.objects[f'truck-{i}-{part}'];print('ROOT',r.name,list(r.location),list(r.rotation_euler),list(r.scale),dict(r.items()))
  inv=r.matrix_world.inverted()
  for o in r.children_recursive:
   if o.type=='MESH':
    pts=[inv@o.matrix_world@Vector(p) for p in o.bound_box]
    bounds=[[round(min(p[k] for p in pts),4),round(max(p[k] for p in pts),4)] for k in range(3)]
    print(o.name,'hidden',o.hide_render,'bounds',bounds)
print('CAM',s.camera.name,list(s.camera.location),list(s.camera.rotation_euler),s.camera.data.ortho_scale,'engine',s.render.engine)
