"""Read-only: stable chassis anchors and constant world windows; never edit scene."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
w,h=map(int,args[:2]) if len(args)>=2 else (960,667)
frames=list(range(97,193));centers={};bounds={1:[],3:[],4:[]};camera_records=[];landmarks=[]
for f in frames:
 s.frame_set(f);bpy.context.view_layer.update();centers[f]={};camera_records.append(([list(r) for r in s.camera.matrix_world],s.camera.data.type,s.camera.data.ortho_scale))
 lm=world_to_camera_view(s,s.camera,Vector((0,0,0)));landmarks.append([lm.x*w,lm.y*h])
 for i in (1,3,4):
  root=bpy.data.objects[f'truck-{i}-tractor'];q=world_to_camera_view(s,s.camera,root.matrix_world@Vector((.8,0,1.25)));centers[f][i]=[q.x*w,(1-q.y)*h]
  for o in root.children_recursive:
   if o.type=='MESH' and not o.hide_render:
    for v in o.bound_box:
     q=world_to_camera_view(s,s.camera,o.matrix_world@Vector(v));bounds[i].append((q.x*w,(1-q.y)*h))
assert all(v==camera_records[0] for v in camera_records),'Camera transform/intrinsics changed'
assert all(v==landmarks[0] for v in landmarks),'Fixed world landmark moved on map'
fixed={}
for i,xy in bounds.items():
 # One rectangle for the ENTIRE sequence. No per-frame pan, rotate, or resize.
 left=min(x for x,y in xy)-24;right=max(x for x,y in xy)+24;top=min(y for x,y in xy)-24;bottom=max(y for x,y in xy)+24
 cx=(left+right)/2;cy=(top+bottom)/2;cw=max(right-left,(bottom-top)*4/3);ch=cw*3/4
 fixed[i]=[cx-cw/2,cy-ch/2,cw,ch]
out={'source_blend':bpy.data.filepath,'source_pixels':[w,h],'frames':frames,'fps':24,'chassis_anchor_local':[.8,0,1.25],'follow_centers':centers,'fixed_world_rectangles':fixed,'camera_records_identical':True,'fixed_world_landmark_projection_identical':True,'tracking_orientation':'fixed source-map orientation, translation only; no framewise rotation/scale','resampling':'one affine BICUBIC operation at floating-point origin; no round/floor of tracking centers'}
(P/'crop-anchors.json').write_text(json.dumps(out,indent=2));print(json.dumps({'camera_fixed':True,'landmark_fixed':True,'fixed_rectangles':fixed}))
