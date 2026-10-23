import bpy,json
from pathlib import Path
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out.parents[1]/'whole-map-v06-2026-10-06/fleet/fleet-textured-v07.blend'))
images=[]
for im in bpy.data.images:
 if im.type!='IMAGE':continue
 p=out/(bpy.path.clean_name(im.name)+'.png')
 im.save_render(str(p));images.append({'name':im.name,'path':str(p),'size':list(im.size),'packed':bool(im.packed_file)})
mats=[]
for m in bpy.data.materials:
 mats.append({'name':m.name,'diffuse':list(m.diffuse_color),'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value for i in n.inputs if hasattr(i,'default_value') and i.type in ['VALUE','RGBA','VECTOR']}} for n in m.node_tree.nodes] if m.node_tree else []})
objects=[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'location':list(o.location),'dimensions':list(o.dimensions),'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []} for o in bpy.context.scene.objects]
(out/'source-inventory.json').write_text(json.dumps({'images':images,'materials':mats,'objects':objects,'camera':bpy.context.scene.camera.name,'engine':bpy.context.scene.render.engine},indent=2))
print(json.dumps(images));print('inventory',len(objects),len(mats))
