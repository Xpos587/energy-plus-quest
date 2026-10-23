import bpy, json, time
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;s=bpy.context.scene
cab=bpy.data.objects['UV PILOT green cab'];uv=cab.data.uv_layers.active
img=next(n.image for n in cab.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
img.filepath=str(O/'green-cab-uv-atlas.png');img.unpack(method='REMOVE');img.reload();img.pack()
for k,p in enumerate(cab.data.polygons):
    for li in p.loop_indices:
        u,v=uv.data[li].uv
        if k in (0,3,6):
            t=(u-.003)/.494;u=.003+.494*(.08+.84*(1-t))
        elif k in (1,4,7):
            t=(u-.503)/.494;u=.503+.494*(.13+.87*t)
        elif k in (2,5,8):
            t=(u-.503)/.494;u=.503+.494*(.87*t)
        uv.data[li].uv=(u,v)
s.frame_set(769);bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-uv-candidate-v1.blend'))
times={}
def render(name):
    s.render.filepath=str(O/name);t=time.monotonic();bpy.ops.render.render(write_still=True);times[name]=round(time.monotonic()-t,3)
render('map-vehicles-0769-v1.png')
cam=s.camera;orig=cam.matrix_world.copy();scale=cam.data.ortho_scale
root=bpy.data.objects['truck-3-tractor']
target=root.matrix_world@Vector((.1,0,1.85));pos=root.matrix_world@Vector((7,-4.2,5.4))
cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=4.8
s.render.resolution_x=1200;s.render.resolution_y=1200
render('green-three-quarter-detail.png')
cam.matrix_world=orig;cam.data.ortho_scale=scale
r=json.loads((O/'receipt.json').read_text());r.update({'candidate':'green-uv-candidate-v1.blend','texture_resolution':list(img.size),'render_seconds_by_image':times,'texture_finish':'softened colored panel seams; no near-black outlines on green paint','UV_trim':'mirror artwork trimmed; separate geometry mirrors retained','detail_render':'native 1200x1200 isolated camera; not the map zoom view','runtime_changed':False})
(O/'receipt-v1.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
