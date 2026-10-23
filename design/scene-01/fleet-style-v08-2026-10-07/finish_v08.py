import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
single=bpy.data.images.load(str(P/'textures/single-illustrated-shared-driver.png'));single.pack()
crew=bpy.data.images.load(str(P/'textures/crew-illustrated.png'));crew.pack()
for i in range(1,5):
    ob=bpy.data.objects[f'V02 DETAILED {i} complete tractor']
    for n in ob.data.materials[1].node_tree.nodes:
        if n.type=='TEX_IMAGE':n.image=crew if i==3 else single
s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v08-finished.blend'))
for f in [1,385,769]:
    s.frame_set(f);s.render.filepath=str(P/f'vehicles-{f:04}.png');bpy.ops.render.render(write_still=True)
flags={o.name:o.hide_render for o in s.objects}
roots=[o for o in s.objects if o.name.startswith('truck-')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
for o in s.objects:
    if o.type in ['MESH','FONT','CURVE'] and o not in fleet:o.hide_render=True
s.frame_set(769);cam=s.camera;s.render.resolution_x=1200;s.render.resolution_y=1200
for i in range(1,5):
    for o in s.objects:o.hide_render=flags[o.name] if o in fleet or o.type not in ['MESH','FONT','CURVE'] else True
    tractor=bpy.data.objects[f'truck-{i}-tractor'];trailer=bpy.data.objects[f'truck-{i}-trailer']
    own={tractor,trailer};own.update(tractor.children_recursive);own.update(trailer.children_recursive)
    for o in fleet:
        if o.type in ['MESH','FONT','CURVE'] and o not in own:o.hide_render=True
    center=tractor.matrix_world@Vector((.25,0,1.65));cam.location=tractor.matrix_world@Vector((11,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.5
    s.render.filepath=str(P/f'front-{i}.png');bpy.ops.render.render(write_still=True)
print('FINISHED V08 PILOTS')
