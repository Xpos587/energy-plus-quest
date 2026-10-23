import bpy
s=bpy.context.scene;s.frame_set(1)
for o in s.objects:
 if any(w in o.name.lower() for w in ('smoke','exhaust','fume','plume')):
  print(o.name,o.type,'parent',o.parent.name if o.parent else None,'loc',list(o.location),'world',list(o.matrix_world.translation),'dimensions',list(o.dimensions),'hide',o.hide_render,'mats',[m.name for m in o.data.materials] if hasattr(o.data,'materials') else None)
for m in bpy.data.materials:
 if any(w in m.name.lower() for w in ('smoke','exhaust','aged','old','cab','blue','green')):
  print('MAT',m.name,'rgba',list(m.diffuse_color),'nodes',[(n.name,n.type) for n in m.node_tree.nodes] if m.use_nodes else None)
