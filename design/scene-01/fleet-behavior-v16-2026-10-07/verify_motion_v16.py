import bpy,json
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parent
s=bpy.context.scene
rates={1:1.,2:.45,3:1.,4:.6}
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v16.blend'))
s=bpy.context.scene;s.frame_set(1)
expected={}
for i,rate in rates.items():
 for part in ('tractor','trailer'):
  name=f'truck-{i}-{part}';o=bpy.data.objects[name];ad=o.animation_data
  curves=list(ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves)
  expected[name]=[]
  for f in range(193):
   loc=o.location.copy();rot=o.rotation_euler.copy()
   for c in curves:(loc if c.data_path=='location' else rot)[c.array_index]=c.evaluate(1+f*rate)
   expected[name].append(Matrix.LocRotScale(loc,rot.to_quaternion(),o.scale))
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v16-motion.blend'))
s=bpy.context.scene;error=0.;hitch_error=0.;distance={i:0. for i in rates};previous={}
for f in range(1,194):
 s.frame_set(f)
 for i in rates:
  names=[f'truck-{i}-{part}'for part in ('tractor','trailer')]
  actual=[bpy.data.objects[n].matrix_world.copy()for n in names]
  ex=[expected[n][f-1]for n in names]
  for x,y in zip(actual,ex):error=max(error,max(abs(x[r][c]-y[r][c])for r in range(4)for c in range(4)))
  rel=actual[0].inverted()@actual[1];erel=ex[0].inverted()@ex[1]
  hitch_error=max(hitch_error,max(abs(rel[r][c]-erel[r][c])for r in range(4)for c in range(4)))
  pos=actual[0].translation
  if i in previous:distance[i]+=(pos-previous[i]).length
  previous[i]=pos.copy()
assert error<1e-5,(error,hitch_error)
assert hitch_error<3e-5,hitch_error
result={'reopened_blend':bpy.data.filepath,'checked_samples':193,'root_matrix_max_absolute_error_vs_paired_source':error,'relative_tractor_trailer_matrix_max_error':hitch_error,'distance_8_seconds_scene_units':distance,'mean_scene_units_per_second':{i:d/8 for i,d in distance.items()},'render_range':[s.frame_start,s.frame_end],'note':'Frame193 is the endpoint needed to measure exactly8seconds; frames1..192 are the24fps proof images.'}
(P/'motion-readback.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
