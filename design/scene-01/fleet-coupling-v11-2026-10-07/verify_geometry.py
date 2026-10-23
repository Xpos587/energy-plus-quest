import bpy,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from pathlib import Path
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
static={};bodies={};axles={}
for i in range(1,5):
 r=bpy.data.objects[f'truck-{i}-tractor'];t=bpy.data.objects[f'truck-{i}-trailer'];o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];m=r.matrix_world.inverted()@o.matrix_world;verts=[m@v.co for v in o.data.vertices];polys=[list(p.vertices) for p in o.data.polygons];static[i]=BVHTree.FromPolygons(verts,polys)
 axle=[]
 for lo,hi in [(-2.6,-1.8),(-1.75,-.99)]:
  ps=[p for p in verts if lo<p.x<hi and abs(p.y)>.65 and p.z<.015];xs=[p.x for p in ps];axle.append({'contact_patch_x_bounds':[min(xs),max(xs)],'axle_x_from_ground_contact_midpoint':(min(xs)+max(xs))/2})
 axles[i]=axle
 # Actual trailer cargo and chassis meshes, excluding intentional saddle-contact chassis below z1.01.
 vs=[];fs=[]
 for o in t.children_recursive:
  if o.type!='MESH' or o.hide_render or not ('long semitrailer' in o.name):continue
  m=t.matrix_world.inverted()@o.matrix_world;offset=len(vs);vs.extend(m@v.co for v in o.data.vertices);fs.extend([offset+v for v in p.vertices] for p in o.data.polygons)
 bodies[i]=(vs,fs)
collisions=[];exhaustcollisions=[]
for f in range(1,1153):
 s.frame_set(f)
 for i in range(1,5):
  r=bpy.data.objects[f'truck-{i}-tractor'];t=bpy.data.objects[f'truck-{i}-trailer'];m=r.matrix_world.inverted()@t.matrix_world;vs,fs=bodies[i];body=BVHTree.FromPolygons([m@v for v in vs],fs)
  ov=static[i].overlap(body)
  if ov:collisions.append({'frame':f,'truck':i,'intersecting_triangles':len(ov)})
  for o in r.children_recursive:
   if o.hide_render or 'exhaust stack' not in o.name:continue
   em=r.matrix_world.inverted()@o.matrix_world;eb=BVHTree.FromPolygons([em@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]);ov=eb.overlap(body)
   if ov:exhaustcollisions.append({'frame':f,'truck':i,'intersecting_triangles':len(ov)})
receipt={'frames':1152,'truck_frames':4608,'actual_mesh_surface_intersections':collisions,'actual_exhaust_surface_intersections':exhaustcollisions,'axles':axles,'method':'BVHTree triangle overlap of full actual visible imported tractor mesh and actual long semitrailer body mesh transformed into tractor space for each frame; separate actual relocated exhaust mesh; supporting whole-body separating-plane proof in coupling-receipt.json','limitations':'contact patch midpoint is measured mesh-derived axle-center proxy, not labeled CAD joint; trailer chassis bearing contact intentionally excluded from body collision test'}
(P/'actual-geometry-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
assert not collisions and not exhaustcollisions
