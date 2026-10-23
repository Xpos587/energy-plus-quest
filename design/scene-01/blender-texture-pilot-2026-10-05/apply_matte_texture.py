import bpy,json,time,math
from pathlib import Path
O=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(769)
cab=bpy.data.objects['UV PILOT green cab'];img=next(n.image for n in cab.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');img.filepath=str(O/'green-cab-uv-atlas.png');img.unpack(method='REMOVE');img.reload();img.pack()
root=bpy.data.objects['truck-3-tractor'];mat=bpy.data.materials['UV v2 soft blue-gray rubber']
for sign in (-1,1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.022,depth=.18)
    o=bpy.context.object;o.name=f'UV final mirror arm {sign}';o.parent=root;o.location=(.85,sign*.865,2.03);o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(mat)
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');objs=[]
for rt in [o for o in s.objects if o.name.startswith('truck-')]:objs.extend(o for o in rt.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
crypto.matte_id=', '.join(o.name for o in objs)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-uv-material-v1.blend'))
s.render.filepath=str(O/'map-vehicles-final.png');t=time.monotonic();bpy.ops.render.render(write_still=True)
r=json.loads((O/'receipt-final.json').read_text());r.update({'candidate':'green-uv-material-v1.blend','matte_texture_map_render_seconds':round(time.monotonic()-t,3),'texture_finish':'matte apple green; generated removal of baked glossy patches; colored soft seams','mirror_arms':'modeled two connecting arms','source_texture_resolution':list(img.size)});(O/'receipt-final.json').write_text(json.dumps(r,indent=2))
# Reuse authored isolated diagnostic camera script; this does not save or alter the master camera.
exec(compile((O/'render_detail.py').read_text(),str(O/'render_detail.py'),'exec'))
