"""Reversible peripheral city expansion; never modifies source or production assets."""
import json
import time
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

OUT = Path('/home/michael/.local/state/energy-plus-quest/research/2026-09-28-expanded-zoom-city')
SOURCE = Path('/home/michael/.local/state/energy-plus-quest/research/2026-09-27-numberless-map-render/separated-city-without-numbers.blend')
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
s.frame_set(1)
original = list(s.objects)
roots = [s.objects[f'truck-{i}-{part}'] for i in range(1, 5) for part in ('tractor', 'trailer')]
def poses():
    result=[]
    for frame in range(1,1153):
        s.frame_set(frame)
        result.append([[list(row) for row in o.matrix_world] for o in roots])
    return result
before_poses=poses()
s.frame_set(1)
static={o.name: ([list(v.co) for v in o.data.vertices], [list(row) for row in o.matrix_world]) for o in original if o.type=='MESH'}
old_camera={'location':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'ortho_scale':s.camera.data.ortho_scale}
collection=bpy.data.collections.new('2026-09-28 peripheral neighbourhoods')
s.collection.children.link(collection)
added=[]
def duplicate_group(prefix, offset, label):
    for o in original:
        if o.name.startswith(prefix):
            c=o.copy();c.name='EXP28 '+label+' '+o.name;collection.objects.link(c)
            c.location+=Vector(offset);added.append(c.name)
# Complete source facade groups, beyond the existing outer residential rows.
for side in (-1,1):
    for j in (0,1,3,4):
        duplicate_group(f'EXT outer row {side} {j} /', (side*21,0,0),f'{side} {j}')
# Northern and southern neighbourhoods preserve every existing street and route.
for x in (-17,-8.4,8.4,17):
    duplicate_group(f'city block {x} 42 ',(0,40,0),f'north {x}')
    duplicate_group(f'city block {x} -41 ',(0,-40,0),f'south {x}')
# Asphalt cross streets stitch the peripheral blocks into the existing street grid.
road=s.objects['continuous street and private yard']
def face(name,x0,x1,y0,y1,z,material_source):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[],[(0,1,2,3)])
    for slot in material_source.material_slots:mesh.materials.append(slot.material)
    o=bpy.data.objects.new('EXP28 '+name,mesh);collection.objects.link(o);added.append(o.name)
for sign in (-1,1):
    face(f'peripheral boulevard {sign}',sign*67-3.95,sign*67+3.95,-85,85,.17,road)
    face(f'cross avenue {sign}',-85,85,sign*72-3.95,sign*72+3.95,.171,road)
# Cover historical coplanar street-extension seams without editing source meshes.
import bmesh
for o in original:
    if o.name.startswith('EXT street continuation'):
        c=o.copy();c.data=o.data.copy();c.name='EXP28 road seam '+o.name
        collection.objects.link(c);added.append(c.name)
        c.material_slots[0].material=road.material_slots[0].material
        for v in c.data.vertices:v.co.z=.025
        bm=bmesh.new();bm.from_mesh(c.data)
        for f in bm.faces:
            if f.normal.z<0:f.normal_flip()
        bm.to_mesh(c.data);bm.free()
s.camera.data.ortho_scale=180
s.render.resolution_x=2016;s.render.resolution_y=1400;s.render.resolution_percentage=100
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16
s.render.image_settings.file_format='PNG'
assert before_poses==poses(), 'Vehicle animation changed'
s.frame_set(1)
assert all(static[o.name]==([list(v.co) for v in o.data.vertices],[list(row) for row in o.matrix_world]) for o in original if o.type=='MESH')
tracks=[]
visibility=[]
for frame in range(1,1153):
    s.frame_set(frame)
    points=[]
    for i in range(1,5):
        p=world_to_camera_view(s,s.camera,s.objects[f'vehicle {i} identification'].matrix_world.translation)
        points.append([p.x,1-p.y])
    tracks.append(points)
    if (frame-1)%12==0:
        deps=bpy.context.evaluated_depsgraph_get();fractions=[]
        for i in range(1,5):
            target=s.objects[f'vehicle {i} identification'].matrix_world.translation
            direction=s.camera.matrix_world.to_quaternion()@Vector((0,0,-1))
            origin=target-direction*300
            hit,loc,normal,index,obj,matrix=s.ray_cast(deps,origin,direction,distance=301)
            fractions.append({'truck':i,'roof_center_clear':not hit or (loc-target).length<.6,'hit':obj.name if obj else None})
        visibility.append({'frame':frame,'rays':fractions})
(OUT/'tracking.json').write_text(json.dumps({'fps':24,'frames':1152,'projected_roof_centers':tracks}))
s.frame_set(1)
s.render.filepath=str(OUT/'frames'/'####')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'expanded-city.blend'))
report={'source':str(SOURCE),'camera_before':old_camera,'camera_after':{'location':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'ortho_scale':s.camera.data.ortho_scale},'resolution':[2016,1400],'engine':s.render.engine,'samples':16,'original_meshes_preserved':len(static),'all_1152_route_poses_identical':True,'added_objects':added,'visibility_center_rays':visibility,'timings_seconds':{}}
(OUT/'expansion-report.json').write_text(json.dumps(report,indent=2))
for frame in (1,385,769):
    s.frame_set(frame);s.render.filepath=str(OUT/f'preview-{frame}.png')
    start=time.monotonic();bpy.ops.render.render(write_still=True)
    report['timings_seconds'][str(frame)]=time.monotonic()-start
    (OUT/'expansion-report.json').write_text(json.dumps(report,indent=2))
print('CANDIDATE_READY',str(OUT),report['timings_seconds'],flush=True)
