"""Export real projected geometry; the browser fits the full loop, not one frame."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]
source=Path(args[0]);dest=Path(args[1])
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
rigs=[[bpy.data.objects[f'truck-{n}-{role}'] for role in ('tractor','trailer')] for n in range(1,5)]
local={}
for pair in rigs:
    for rig in pair:
        points=[o.matrix_local@Vector(v) for o in rig.children if o.type=='MESH' for v in o.bound_box]
        bounds=[(min(v[i] for v in points),max(v[i] for v in points)) for i in range(3)]
        local[rig.name]=[Vector((x,y,z)) for x in bounds[0] for y in bounds[1] for z in bounds[2]]
result={'fps':24,'frames':768,'views':{}}
for name,w,h in [('mobile',720,1024),('desktop',1440,1000)]:
    cam=bpy.data.objects[name];s.camera=cam;s.render.resolution_x=w;s.render.resolution_y=h
    def project(p):
        v=world_to_camera_view(s,cam,p)
        return [round(v.x*w,4),round((1-v.y)*h,4)]
    def bounds(points):
        return [min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
    warehouse=[o for o in s.objects if o.name=='warehouse body']
    landmark=bounds([project(o.matrix_world@Vector(v)) for o in warehouse for v in o.bound_box])
    tracks=[];union=[landmark[:2],landmark[2:]]
    for f in range(1,769):
        s.frame_set(f);row=[]
        for n,pair in enumerate(rigs,1):
            points=[project(rig.matrix_world@v) for rig in pair for v in local[rig.name]]
            bbox=bounds(points)
            label=bpy.data.objects[f'vehicle {n} identification']
            marker=project(label.matrix_world.translation)
            row.append({'bounds':bbox,'marker':marker})
            union.extend([bbox[:2],bbox[2:]])
        tracks.append(row)
    result['views'][name]={'width':w,'height':h,'bounds':bounds(union),'warehouse':landmark,'tracks':tracks}
    print(name,result['views'][name]['bounds'],flush=True)
dest.write_text(json.dumps(result,separators=(',',':'))+'\n')
