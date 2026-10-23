"""Finish frozen technical 48-second rig without material, geometry or route edits."""
import bpy,json,time
from pathlib import Path
O=Path(__file__).resolve().parent;P=O/'pilot-frames';s=bpy.context.scene
assert (s.render.resolution_x,s.render.resolution_y)==(1280,889)
assert s.eevee.taa_render_samples==8 and s.render.fps==24
start=time.monotonic();failures=[];rendered=[];existing=[]
for frame in range(289,1153):
 target=P/f'{frame:04}.png'
 if target.exists():existing.append(frame);continue
 try:
  s.frame_set(frame);s.render.filepath=str(target);bpy.ops.render.render(write_still=True)
  assert target.exists();rendered.append(frame)
 except Exception as exc:
  failures.append({'frame':frame,'error':str(exc)});print('FRAME FAILURE',frame,str(exc),flush=True)
 if frame%48==0:
  status={'last_frame':frame,'rendered_this_run':len(rendered),'elapsed_seconds':round(time.monotonic()-start,3),'failures':failures}
  (O/'full-render-progress.json').write_text(json.dumps(status,indent=2));print('FULL LOOP PROGRESS',status,flush=True)
missing=[f for f in range(1,1153) if not (P/f'{f:04}.png').exists()]
r={'source_blend':'painted-vehicles-bright-12sec.blend','frame_count':1152,'fps':24,'duration_seconds':48,'dimensions':[1280,889],'samples':8,'threads':4,'rendered_this_run':len(rendered),'reused_initial_frames':288,'existing_remaining_frames':existing,'measured_remaining_render_elapsed_seconds':round(time.monotonic()-start,3),'failures':failures,'missing_frames':missing,'complete':not failures and not missing,'mutations':'render filepath and current frame only; no material, geometry, route or camera edits'}
(O/'full-loop-receipt.json').write_text(json.dumps(r,indent=2));print('FULL LOOP COMPLETE',r,flush=True)
