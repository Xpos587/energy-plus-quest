import bpy,time,json
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.render.use_persistent_data=True
result=[]
for f in [1,2,3,385]:
 s.frame_set(f);s.render.filepath=str(P/f'benchmark-shadow-{f:04}.png');t=time.monotonic();bpy.ops.render.render(write_still=True);dt=time.monotonic()-t;result.append({'frame':f,'seconds':dt});print('WARM_BENCHMARK',result[-1],flush=True)
(P/'benchmark-warm.json').write_text(json.dumps(result,indent=2))
