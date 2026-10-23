import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
flat=bpy.data.materials.new('V14 continuous chassis finish');flat.use_nodes=True;n=flat.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(.115,.165,.195,1);out=n.new('ShaderNodeOutputMaterial');flat.node_tree.links.new(e.outputs[0],out.inputs[0])
source=P.parent/'fleet-clean-v13-2026-10-07/fleet-v13-clean.blend'
with bpy.data.libraries.load(str(source),link=False) as (a,b):b.objects=[f'V02 DETAILED {i} complete tractor'for i in (2,3)]
loaded=list(b.objects)
for i,src in zip((2,3),loaded):
 dst=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];dst.data=src.data.copy();t=dst.parent.matrix_world.inverted()@dst.matrix_world;inv=t.inverted()
 # Keep image-space semantic glazing/grille boundaries; do not classify large triangles by their centroids.
 for m in dst.data.materials:
  if not m or 'windshield' in m.name.lower():continue
  m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
  for e in list(n):
   if e.type!='EMISSION':continue
   socket=e.inputs[0].links[0].from_socket if e.inputs[0].is_linked else None;base=e.inputs[0].default_value[:]
   g=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=Vector((-40,35,70)).normalized();l.new(g.outputs['Normal'],dot.inputs[0]);r=n.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=-1;r.inputs['To Min'].default_value=.68;r.inputs['To Max'].default_value=1.1;l.new(dot.outputs['Value'],r.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=base
   if socket:l.new(socket,mix.inputs[1])
   l.new(r.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],e.inputs[0])
 if i==2:
  for v in dst.data.vertices:
   p=t@v.co
   if p.z>2.11:p.z=2.11+(p.z-2.11)*.60;v.co=inv@p
 bpy.data.objects.remove(src,do_unlink=True)
for i in range(1,5):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];t=o.parent.matrix_world.inverted()@o.matrix_world;idx=len(o.data.materials);o.data.materials.append(flat)
 bm=bmesh.new();bm.from_mesh(o.data);delete=[]
 for f in bm.faces:
  if f.material_index==1:continue
  p=sum((t@v.co for v in f.verts),Vector())/len(f.verts);x,y,z=p;rad=min(math.hypot(x-c,z-.35)for c in (.80,-1.35,-2.20))
  if rad<.43 and abs(y)>.34 and z<.84:delete.append(f)
  elif i in (1,4) or (x<.05 and z<1.2):f.material_index=idx
 bmesh.ops.delete(bm,geom=delete,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
