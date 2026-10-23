import bpy,json,time
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(769)
root=bpy.data.objects['truck-3-tractor'];trailer=bpy.data.objects['truck-3-trailer']
keep={root,trailer,*root.children_recursive,*trailer.children_recursive}
for o in s.objects:
    if o.type in ('MESH','FONT','CURVE') and o not in keep:o.hide_render=True
cam=s.camera;target=root.matrix_world@Vector((.1,0,1.65));pos=root.matrix_world@Vector((7,-4.2,5.4))
cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=4.8
s.render.resolution_x=1200;s.render.resolution_y=1200
# Direct RGBA removes irrelevant city colour bleeding in this isolated diagnostic.
tree=s.compositing_node_group;output=next(n for n in tree.nodes if n.type=='GROUP_OUTPUT');rl=next(n for n in tree.nodes if n.type=='R_LAYERS');tree.links.new(rl.outputs['Image'],output.inputs['Image'])
s.render.filepath=str(O/'green-three-quarter-isolated.png');t=time.monotonic();bpy.ops.render.render(write_still=True)
(O/'detail-receipt.json').write_text(json.dumps({'dimensions':[1200,1200],'seconds':round(time.monotonic()-t,3),'diagnostic_camera_only':True,'city_hidden_for_closeup':True,'production_unchanged':True},indent=2))
