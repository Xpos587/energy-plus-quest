import bpy, json
from pathlib import Path
s=bpy.context.scene
s.frame_set(769)
root=bpy.data.objects['truck-3-tractor']
items=[]
for o in root.children_recursive:
    if o.type!='MESH' or o.hide_render: continue
    corners=[o.matrix_world.inverted() @ (o.matrix_world @ v.co) for v in o.data.vertices]
    bounds=[[min(v[a] for v in corners),max(v[a] for v in corners)] for a in range(3)]
    items.append({'name':o.name,'location':list(o.location),'bounds':bounds,'materials':[m.name for m in o.data.materials]})
r={'frame':769,'camera':s.camera.name,'root_matrix':[list(x) for x in root.matrix_world],'visible_green_meshes':items,'resolution':[s.render.resolution_x,s.render.resolution_y],'engine':s.render.engine,'compositor':[n.type for n in s.compositing_node_group.nodes]}
Path(__file__).with_name('source-inspection.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
