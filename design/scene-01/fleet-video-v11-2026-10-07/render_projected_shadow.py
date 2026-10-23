import bpy,numpy as np,time,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
frames=[int(v) for v in args] if args else list(range(1,1153))
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
casters=[o for o in fleet if o.type=='MESH' and not o.hide_render and 'light exhaust' not in o.name]
parts=[];polys=[];offset=0
for o in casters:
 xyz=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',xyz);xyz=xyz.reshape(-1,3);parts.append((o,xyz,offset));polys.extend([offset+v for v in p.vertices] for p in o.data.polygons);offset+=len(xyz)
mesh=bpy.data.meshes.new('v11 actual mesh projected ground silhouette');mesh.from_pydata(np.zeros((offset,3),dtype=np.float32).tolist(),[],polys);mesh.update();shadow=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(shadow)
mat=bpy.data.materials.new('opaque geometric shadow coverage');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();e=nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(0,0,0,1);out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(e.outputs[0],out.inputs['Surface']);mesh.materials.append(mat)
for o in s.objects:
 if o.type not in ('CAMERA','LIGHT') and o!=shadow:o.hide_render=True
s.render.engine='BLENDER_EEVEE';s.render.use_compositing=False;s.render.film_transparent=True;s.render.resolution_percentage=50;s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='Standard';s.view_settings.look='None'
coords=np.empty((offset,3),dtype=np.float32);dest=P/'projected-shadow';dest.mkdir(exist_ok=True);timings=[]
for f in frames:
 output=dest/f'{f:04}.png'
 if output.exists():continue
 start=time.monotonic();s.frame_set(f)
 for o,xyz,off in parts:
  m=np.array(o.matrix_world,dtype=np.float32);p=xyz@m[:3,:3].T+m[:3,3];p[:,0]+=p[:,2]*(40/70);p[:,1]-=p[:,2]*(35/70);p[:,2]=-.002;coords[off:off+len(xyz)]=p
 mesh.vertices.foreach_set('co',coords.ravel());mesh.update();s.render.filepath=str(output);bpy.ops.render.render(write_still=True);dt=time.monotonic()-start;timings.append({'frame':f,'seconds':dt});print('PROGRESS_SHADOW',f,round(dt,3),flush=True)
 if f%24==0 or len(frames)<10:(P/'projected-progress.json').write_text(json.dumps({'last_frame':f,'timings':timings[-24:]},indent=2))
(P/'projected-shadow-receipt.json').write_text(json.dumps({'method':'actual visible animated mesh ground projection along approved SUN direction; no generic proxy shapes; translucent smoke excluded','source':'fleet-v11-video.blend','light_position':[-40,35,70],'projection_z':-.002,'render_resolution':[960,667],'frames_requested':frames,'timings':timings},indent=2))
