import bpy,json
from mathutils import Vector
s=bpy.context.scene
print('SCENE',s.render.engine,s.cycles.samples,s.camera.name,tuple(s.camera.location),tuple(s.camera.rotation_euler),s.camera.data.type,s.camera.data.ortho_scale)
print('WORLD',[(n.type,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in s.world.node_tree.nodes] if s.world else None)
print('LIGHTS',[(o.name,tuple(o.location),tuple(o.rotation_euler),o.data.type,o.data.energy,getattr(o.data,'angle',None),getattr(o.data,'size',None)) for o in s.objects if o.type=='LIGHT'])
print('COMPOSITOR',[(n.name,n.type) for n in s.compositing_node_group.nodes]);print('LINKS',[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in s.compositing_node_group.links])
print('GROUND',[(o.name,tuple(o.location),tuple(o.dimensions),o.hide_render) for o in s.objects if any(w in o.name.lower() for w in ['ground','road','plane','backdrop'])])
s.frame_set(1)
for i in range(1,5):
 for part in ('tractor','trailer'):
  o=bpy.data.objects[f'truck-{i}-{part}'];pts=[ch.matrix_world@Vector(c) for ch in o.children_recursive if ch.type=='MESH' for c in ch.bound_box]
  print(o.name,tuple(o.location),'BOUNDS',tuple(min(p[j] for p in pts) for j in range(3)),tuple(max(p[j] for p in pts) for j in range(3)))
