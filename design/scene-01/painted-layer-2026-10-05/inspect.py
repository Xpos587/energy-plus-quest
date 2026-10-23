import bpy,json
s=bpy.context.scene
roots=[o for o in s.objects if o.name.startswith('truck-')]
print('CONFIG',s.render.engine,s.render.resolution_x,s.render.resolution_y,s.camera.name,s.frame_end)
print('ROOTS',[(o.name,o.type,len(o.children_recursive)) for o in roots])
for root in roots:
 print('OBJECTS',root.name,[(o.name,o.type,[m.name for m in o.data.materials] if o.type=='MESH' else '') for o in root.children_recursive][:140])
print('MATERIALS',[(m.name,[(n.type,tuple(n.inputs['Base Color'].default_value) if 'Base Color' in n.inputs else tuple(n.inputs['Color'].default_value) if 'Color' in n.inputs else '') for n in m.node_tree.nodes] if m.use_nodes else '') for m in bpy.data.materials])
print('IMAGES',[(i.name,i.filepath) for i in bpy.data.images])
print('COMPOSITOR',s.use_nodes,s.compositing_node_group if hasattr(s,'compositing_node_group') else '')
