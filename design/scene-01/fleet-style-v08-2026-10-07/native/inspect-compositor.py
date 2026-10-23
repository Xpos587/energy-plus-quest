import bpy
from pathlib import Path
O=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'fleet-illustrated-v08.blend'));s=bpy.context.scene
print('FILM',s.render.film_transparent,'use_compositing',s.render.use_compositing)
for n in s.compositing_node_group.nodes:print(n.name,n.type,[x.name for x in n.inputs],[x.name for x in n.outputs])
for l in s.compositing_node_group.links:print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
