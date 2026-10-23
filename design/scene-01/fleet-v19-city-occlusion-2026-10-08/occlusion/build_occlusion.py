import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;s=bpy.context.scene
old=json.loads((P/'original-visibility.json').read_text())
roots=[bpy.data.objects[f'truck-{i}-{p}'] for i in range(1,5) for p in ('tractor','trailer')]
fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
smoke=set(bpy.data.collections['V16 smoke worldspace exhaust puffs'].objects)
city=[o for o in s.objects if o not in fleet and o not in smoke and o.type=='MESH' and o.name in old and not old[o.name]]
before={}
for f in range(1,193):
 s.frame_set(f);before[f]=[[list(row) for row in r.matrix_world] for r in roots]
s.frame_set(1)
mat=bpy.data.materials.new('CITY depth-only holdout');mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear();h=ns.new('ShaderNodeHoldout');out=ns.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(h.outputs[0],out.inputs['Surface'])
verts=[];faces=[]
for o in city:
 o.hide_render=False
 off=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend([off+i for i in p.vertices] for p in o.data.polygons)
 o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(mat)
bvh=BVHTree.FromPolygons(verts,faces)
direction=s.camera.matrix_world.to_quaternion()@Vector((0,0,-1));rows=[]
for f in range(1,193):
 s.frame_set(f);hits=0;tested=0
 for r in roots:
  for o in r.children_recursive:
   if o.type!='MESH' or o.hide_render:continue
   for v in o.bound_box:
    p=o.matrix_world@Vector(v);origin=p-direction*250;loc,normal,index,dist=bvh.ray_cast(origin,direction,250)
    tested+=1;hits+=loc is not None
 rows.append({'frame':f,'hidden_samples':hits,'tested':tested})
 assert before[f]==[[list(row) for row in r.matrix_world] for r in roots]
chosen=[]
for row in sorted(rows,key=lambda x:x['hidden_samples'],reverse=True):
 if all(abs(row['frame']-f)>15 for f in chosen):chosen.append(row['frame'])
 if len(chosen)==3:break
s.render.use_compositing=False;s.render.film_transparent=True
s.frame_set(chosen[0]);bpy.ops.wm.save_as_mainfile(filepath=str(P/'city-occlusion.blend'))
(P/'build-receipt.json').write_text(json.dumps({'city_objects':len(city),'city_names':[o.name for o in city],'camera':[list(row) for row in s.camera.matrix_world],'root_matrices_192_frames_equal':True,'pilot_frames':chosen,'scan':rows,'method':'original visible city meshes restored with Holdout shader; source fleet and smoke preserved'},indent=2))
print('OCCLUSION_PILOTS',chosen)
