import bpy,json
from mathutils import Vector
s=bpy.context.scene
for f in (133,169):
 s.frame_set(f);bpy.context.view_layer.update();print('FRAME',f)
 for i in (1,3,4):
  root=bpy.data.objects[f'truck-{i}-tractor'];tr=bpy.data.objects[f'truck-{i}-trailer']
  print('ROOT',i,'tractor',list(root.location),list(root.rotation_euler),'trailer',list(tr.location),list(tr.rotation_euler))
  for o in list(root.children_recursive)+list(tr.children_recursive):
   if o.name in (f'{i} ladder frame',f'{i} fifth wheel',f'{i} trailer chassis',f'{i} long semitrailer') or 'PILOT '+str(i)+' reconstructed' in o.name:
    coords=[root.matrix_world.inverted()@(o.matrix_world@Vector(v)) for v in o.bound_box]
    print('OBJ',o.name,'hidden',o.hide_render,'local_location',list(o.location),'bounds_in_tractor',[(min(v[a] for v in coords),max(v[a] for v in coords)) for a in range(3)])
