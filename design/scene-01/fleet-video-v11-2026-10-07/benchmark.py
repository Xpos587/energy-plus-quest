import bpy,time,json
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
print('GPU_DEVICES',[(d.name,d.type) for d in prefs.devices],flush=True)
for typ in ['OPTIX','CUDA']:
 try:
  prefs.compute_device_type=typ;prefs.get_devices();print('AVAILABLE',typ,[(d.name,d.type) for d in prefs.devices],flush=True)
  for d in prefs.devices:d.use=d.type!='CPU'
  if any(d.type!='CPU' for d in prefs.devices):break
 except Exception as e:print('DEVICE_ERROR',typ,str(e),flush=True)
s.cycles.device='GPU';s.cycles.samples=8;s.cycles.adaptive_threshold=.1;s.render.resolution_percentage=50
s.frame_set(1);s.render.filepath=str(P/'benchmark-shadow-0001.png');start=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-start
bpy.ops.wm.save_as_mainfile(filepath=str(P/'shadow-animation-source.blend'));(P/'benchmark.json').write_text(json.dumps({'engine':'CYCLES','device':typ,'samples':8,'resolution':[960,667],'first_frame_seconds':elapsed},indent=2));print('BENCHMARK_SECONDS',elapsed,flush=True)
