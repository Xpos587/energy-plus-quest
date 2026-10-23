import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene;c=[o for o in s.objects if 'PILOT' in o.name and 'reconstructed' in o.name];s.frame_set(1);bpy.context.view_layer.update()
base={o.name:[float(x) for row in o.matrix_local for x in row] for o in c};channels={o.name:list(o.location)+list(o.rotation_euler)+list(o.scale) for o in c};delta=0;changed=[]
for f in range(1,289):
 s.frame_set(f);bpy.context.view_layer.update()
 for o in c:
  vals=[float(x) for row in o.matrix_local for x in row];delta=max(delta,max(abs(a-b) for a,b in zip(vals,base[o.name])))
  if list(o.location)+list(o.rotation_euler)+list(o.scale)!=channels[o.name]:changed.append([f,o.name])
r={'reconstructed_cab_count':len(c),'cab_local_transform_channels_unchanged':not changed,'changed_channels':changed,'matrix_local_max_numeric_delta':delta,'rigid_relative_to_native_tractor':not changed and delta<.0001,'cause_of_prior_exact_matrix_false':'parent transform inversion float roundoff; replace exact matrix equality with channel equality plus measured matrix tolerance'}
(p/'local-transform-verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
