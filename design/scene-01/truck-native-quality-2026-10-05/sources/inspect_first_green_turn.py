import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;tractor=bpy.data.objects['truck-3-tractor'];trailer=bpy.data.objects['truck-3-trailer'];cam=s.camera
start,end=2,57
pts=[];projected=[];samples={};angles=[]
for f in range(start,end+1):
 s.frame_set(f);angles.append((abs(tractor.rotation_euler.z-3*math.pi/4),f))
 for o in s.objects:
  if o.type=='MESH' and o.parent in (tractor,trailer) and not o.hide_render:
   for b in o.bound_box:
    p=o.matrix_world@Vector(b);pts.append(p);projected.append(world_to_camera_view(s,cam,p))
for label,f in [('entry',start),('apex',min(angles)[1]),('exit',end)]:
 s.frame_set(f);samples[label]={'frame':f}
 for o in [tractor,trailer]:samples[label][o.name]={'xyz':list(o.location),'rotation_z_radians_unwrapped':o.rotation_euler.z,'rotation_z_degrees_mod360':math.degrees(o.rotation_euler.z) %360}
lo=[min(p[a] for p in pts) for a in range(3)];hi=[max(p[a] for p in pts) for a in range(3)]
nlo=[min(p[a] for p in projected) for a in range(2)];nhi=[max(p[a] for p in projected) for a in range(2)]
out={'source_blend':bpy.data.filepath,'fps':s.render.fps,'tractor_corner_frames_inclusive':[start,end],'straight_confirmation_frames':[1,58],'samples':samples,'bounds_world_xyz':{'min':lo,'max':hi},'world_xy_target_rectangle':{'xmin':lo[0],'xmax':hi[0],'ymin':lo[1],'ymax':hi[1]},'world_xy_rectangle_with_1_unit_margin':{'xmin':lo[0]-1,'xmax':hi[0]+1,'ymin':lo[1]-1,'ymax':hi[1]+1},'existing_camera':cam.name,'existing_camera_normalized_crop':{'left':nlo[0],'right':nhi[0],'bottom':nlo[1],'top':nhi[1]},'render_resolution':[s.render.resolution_x,s.render.resolution_y],'notes':['Tractor is straight at frames 1-2, turns during 3-57, straight again at 57-99. Corner interval measured as last entry-heading frame to first exit-heading frame.','Trailer is independently baked and lags: it is not aligned with exit straight at frame 57. There is no fully articulated rig straight-to-straight 90-degree interval before next tractor corner starts at frame 100.','Bounds include every visible-render mesh directly parented to tractor or trailer, including cab accessories, wheels and crew; evaluated every integer frame 2-57. Camera crop is normalized projection of all 3D bounding corners under existing camera; bottom-origin coordinates.','No render, file save, or runtime modification performed.']}
p=Path('design/scene-01/truck-native-quality-2026-10-05/sources/GREEN-TURN-INTERVAL.json');p.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
