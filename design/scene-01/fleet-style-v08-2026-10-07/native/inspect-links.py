import bpy
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O.parents[1]/'whole-map-v06-2026-10-06/fleet/fleet-textured-v07.blend'))
m=bpy.data.objects['V02 DETAILED 1 complete tractor'].data.materials[0]
for l in m.node_tree.links:print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
print('scales',[(bpy.data.objects[n].name,list(bpy.data.objects[n].scale)) for n in ['truck-1-tractor','truck-1-trailer','1 long semitrailer']])
for m in bpy.data.materials:
 if m.name in ['1 clay cargo','2 clay cargo','1 metal form','1 rubber form']:
  print('MAT',m.name,[(n.name,n.type,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value') and i.type=='RGBA']) for n in m.node_tree.nodes])
print('lights',[(o.name,o.data.type,o.data.energy) for o in bpy.context.scene.objects if o.type=='LIGHT'])
