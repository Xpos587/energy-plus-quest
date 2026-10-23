"""Bake isolated candidate, reread native keys, verify and render requested preview."""
import bpy,json,sys,math
import numpy as np
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
p=Path(__file__).resolve().parent
s=bpy.context.scene
report=json.loads((p/'route-check.json').read_text());assert report['passed']
motion=np.load(p/'motion.npy')
roots=[s.objects[f'truck-{i}-{part}'] for i in range(1,5) for part in ('tractor','trailer')]
moving={o.name for root in roots for o in [root,*root.children_recursive]}
def snapshot():
 return {o.name:([tuple(v.co) for v in o.data.vertices],[tuple(r) for r in o.matrix_world]) for o in s.objects if o.type=='MESH' and o.name not in moving}
s.frame_set(1);original_static=snapshot();camera=(tuple(s.camera.location),tuple(s.camera.rotation_euler),s.camera.data.ortho_scale)
for o in roots:o.animation_data_clear()
for frame,poses in enumerate(motion,1):
 for o,pose in zip(roots,poses):
  o.location=pose[:3];o.rotation_euler.z=pose[3]
  o.keyframe_insert('location',frame=frame);o.keyframe_insert('rotation_euler',frame=frame)
for o in roots:
 for layer in o.animation_data.action.layers:
  for strip in layer.strips:
   bag=strip.channelbag(o.animation_data.action_slot)
   if bag:
    for c in bag.fcurves:
     for k in c.keyframe_points:k.interpolation='LINEAR'
for i in range(1,5):s.objects[f'vehicle {i} identification'].hide_render=True
s.frame_start=1;s.frame_end=1152;s.render.fps=24
s.render.resolution_x=1008;s.render.resolution_y=700;s.render.resolution_percentage=100
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=8
s.render.image_settings.file_format='PNG';s.frame_set(1)
assert snapshot()==original_static
assert camera==(tuple(s.camera.location),tuple(s.camera.rotation_euler),s.camera.data.ortho_scale)
bpy.ops.wm.save_as_mainfile(filepath=str(p/'controlled-straight-start.blend'))
bpy.ops.wm.open_mainfile(filepath=str(p/'controlled-straight-start.blend'));s=bpy.context.scene
roots=[s.objects[f'truck-{i}-{part}'] for i in range(1,5) for part in ('tractor','trailer')]
max_error=0.;tracks=[]
for frame,poses in enumerate(motion,1):
 s.frame_set(frame);row=[]
 for i,pose in enumerate(poses):
  o=s.objects[f'truck-{i//2+1}-'+('tractor' if i%2==0 else 'trailer')]
  max_error=max(max_error,float(np.abs(np.array([*o.location,o.rotation_euler.z])-pose).max()))
  q=world_to_camera_view(s,s.camera,o.matrix_world.translation);row.append([q.x,1-q.y])
 tracks.append(row)
assert max_error<.00002
assert snapshot()==original_static
(p/'tracking.json').write_text(json.dumps({'fps':24,'frames':1152,'endpoint_included':True,'order':[o.name for o in roots],'normalized_screen_origins':tracks}))
sys.path.insert(0,'/home/michael/.local/state/energy-plus-quest/research/2026-09-22-city-polish')
from validate_visibility import templates,build,coverage,semantic_groups
groups=semantic_groups(s);all_templates=templates(s)
dynamic_names=set().union(*(groups[f'truck-{i}'] for i in range(1,5)))
static=build(s,[t for t in all_templates if t[0] not in dynamic_names])
warehouse=build(s,[t for t in all_templates if t[0] in groups['warehouse']])
warehouse_visibility=coverage(warehouse,[static],s.camera,s,48)
records=[]
for frame in list(range(1,1153,24))+[1153]:
 s.frame_set(frame);bpy.context.view_layer.update();dynamic=build(s,[t for t in all_templates if t[0] in dynamic_names]);row=[]
 for i in range(1,5):
  group=build(s,[t for t in all_templates if t[0] in groups[f'truck-{i}']]);row.append(coverage(group,[static,dynamic],s.camera,s,32))
 records.append({'frame':frame,'trucks':row})
 if len(records)%10==0:print('VISIBILITY',len(records),flush=True)
minimum=[min(row['trucks'][i]['visible'] for row in records) for i in range(4)]
check={'saved_pose_max_error':max_error,'camera_preserved':True,'static_meshes_preserved':len(original_static),'number_roofs_hidden':all(s.objects[f'vehicle {i} identification'].hide_render for i in range(1,5)),'warehouse_visibility':warehouse_visibility,'truck_visibility_minimum':minimum,'visibility_samples':records,'limitation':'Visibility sampled every1second with32x32 projected silhouette rays; not a full-frame visual guarantee. Full swept collision verification is in route-check.json.','passed':min(minimum)>.5 and warehouse_visibility['visible']>.8}
(p/'scene-check.json').write_text(json.dumps(check,indent=2));print('SCENE CHECK',max_error,minimum,flush=True)
assert check['passed']
s.frame_set(1);s.render.filepath=str(p/'first-frame.png');bpy.ops.render.render(write_still=True)
s.render.resolution_x=720;s.render.resolution_y=500;s.frame_end=120
(p/'preview-frames').mkdir(exist_ok=True)
s.render.filepath=str(p/'preview-frames/####');bpy.ops.render.render(animation=True)
