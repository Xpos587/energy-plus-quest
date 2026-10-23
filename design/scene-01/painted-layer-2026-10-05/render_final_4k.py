"""Native 48-second fallback candidate only. No production, geometry, material or rig edits."""
import bpy,json,time,shutil
from pathlib import Path
p=Path(__file__).resolve().parent;out=p/'final-4k-frames';out.mkdir(exist_ok=True);s=bpy.context.scene
assert (s.render.resolution_x,s.render.resolution_y)==(3840,2667) and s.eevee.taa_render_samples==8 and s.render.fps==24
baseline=json.loads((p/'final-frozen-root-baseline.json').read_text());roots=[o for o in s.objects if o.name.startswith('truck-')]
# Only exact driver-fixed stills produced by this same source blend and treatment are reused.
reused=[]
for f in (1,769):
 target=out/f'{f:04}.png'
 if not target.exists():shutil.copyfile(p/'repaired-stills'/f'4k-driver-fixed-{f:04}.png',target)
 reused.append(f)
drivers=[o for o in s.objects if o.type=='MESH' and ('driver' in o.name.lower() or o.name.startswith('BLUE empty passenger'))]
def channel(o):return list(o.location)+list(o.rotation_euler)+list(o.scale)
initial_driver_channels={o.name:channel(o) for o in drivers};initial_driver_vertices={o.name:[list(v.co) for v in o.data.vertices] for o in drivers}
start=time.monotonic();rendered=[];existing=[];failures=[];root_mismatches=[];driver_channel_mismatches=[];stopped=False;last_checked=0
for frame in range(1,1153):
 if (p/'STOP_FINAL_4K_RENDER').exists():stopped=True;break
 s.frame_set(frame);actual={o.name:[list(o.location),list(o.rotation_euler)] for o in roots}
 if actual!=baseline[str(frame)]:root_mismatches.append(frame)
 for o in drivers:
  if channel(o)!=initial_driver_channels[o.name]:driver_channel_mismatches.append([frame,o.name])
 last_checked=frame;target=out/f'{frame:04}.png'
 if target.exists():existing.append(frame)
 else:
  try:
   s.render.filepath=str(target);bpy.ops.render.render(write_still=True);assert target.exists();rendered.append(frame)
  except BaseException as exc:
   failures.append({'frame':frame,'exception_type':type(exc).__name__,'error':str(exc)});stopped=True;break
 if frame%24==0 or frame in (1,769):
  progress={'status':'rendering','last_checked_frame':frame,'completed_frame_count':len(rendered)+len(existing),'newly_rendered':len(rendered),'reused_exact_stills':reused,'elapsed_seconds':round(time.monotonic()-start,3),'root_pose_mismatches':root_mismatches,'driver_channel_mismatches':driver_channel_mismatches,'failures':failures,'candidate_only':True,'style_accepted':False}
  (p/'final-4k-progress.json').write_text(json.dumps(progress,indent=2));print('FINAL 4K PROGRESS',progress,flush=True)
s.frame_set(1153);boundary={o.name:[list(o.location),list(o.rotation_euler)] for o in roots};boundary_match=boundary==baseline['1153']
vertices_unchanged=all([list(v.co) for v in o.data.vertices]==initial_driver_vertices[o.name] for o in drivers)
missing=[f for f in range(1,1153) if not (out/f'{f:04}.png').exists()]
r={'status':'interrupted' if stopped else 'complete','source_blend':'painted-vehicles-driver-fixed-optimized.blend','candidate_only':True,'style_accepted':False,'required_frame_count':1152,'completed_frame_count':1152-len(missing),'fps':24,'duration_seconds':48,'dimensions':[3840,2667],'samples':8,'threads':4,'measured_render_elapsed_seconds':round(time.monotonic()-start,3),'new_frames_rendered':len(rendered),'reused_exact_driver_fixed_stills':reused,'preexisting_frames':existing,'last_checked_frame':last_checked,'native_root_pose_mismatch_frames':root_mismatches,'boundary_frame_1153_matches_frozen_source':boundary_match,'driver_local_transform_mismatches':driver_channel_mismatches,'driver_mesh_vertices_unchanged':vertices_unchanged,'failures':failures,'missing_frames':missing,'full_loop_verified':not stopped and not missing and not failures and not root_mismatches and not driver_channel_mismatches and vertices_unchanged and boundary_match,'mutations':'current frame and render output filepath only'}
(p/'final-4k-completion-receipt.json').write_text(json.dumps(r,indent=2));print('FINAL 4K END',r,flush=True)
