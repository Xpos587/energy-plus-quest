import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
source=P.parent/'fleet-v16-worn-motion-2026-10-08/fleet-v16-worn-motion.blend'
def actions():
 result={}
 for a in bpy.data.actions:
  curves=[]
  for layer in a.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:curves.append((fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points]))
  result[a.name]=curves
 return result
def objects():
 return {o.name:{'matrix':[list(row) for row in o.matrix_local],'hidden':o.hide_render,'parent':o.parent.name if o.parent else None,'mesh':([(tuple(v.co)) for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]) if o.type=='MESH' and o.name.startswith(('V02 DETAILED 1','V02 DETAILED 4')) else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None} for o in bpy.data.objects}
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(96);bpy.context.view_layer.update();old=objects();oldactions=actions()
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v16-cab-repair.blend'));s=bpy.context.scene;s.frame_set(96);bpy.context.view_layer.update();new=objects();errors=[]
for name,data in old.items():
 if 'rolled wheel arch' in name and name.startswith(('V14 1 ','V14 4 ')):continue
 if data!=new.get(name):errors.append(name)
assert not errors,errors
assert oldactions==actions(),'Source animation keyframes changed'
points={};minimum={1:1e9,4:1e9};worst={};deps=bpy.context.evaluated_depsgraph_get()
for i in (1,4):
 g=bpy.data.objects[f'WORN {i} isolated cab suspension'];inv=g.matrix_world.inverted();points[i]=[]
 for o in s.objects:
  if not (o.name.startswith(f'CABREPAIR {i} ') or o.name.startswith(f'V14 {i} rolled wheel arch')):continue
  ev=o.evaluated_get(deps);me=ev.to_mesh();points[i].extend(inv@o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
for f in range(1,193):
 s.frame_set(f);bpy.context.view_layer.update()
 for i in (1,4):
  root=bpy.data.objects[f'truck-{i}-tractor'];g=bpy.data.objects[f'WORN {i} isolated cab suspension'];tr=root.matrix_world.inverted()@g.matrix_world
  for p in points[i]:
   q=tr@p
   if abs(abs(q.y)-.805)<.21:
    clearance=math.hypot(q.x-.8,q.z-.355)-.358
    if clearance<minimum[i]:minimum[i]=clearance;worst[i]=f
assert min(minimum.values())>0,minimum
receipt={'source_objects_checked_except_intentionally_moved_arch_lips':len(old)-64,'unchanged_source_local_matrices_parents_visibility_material_slots':not errors,'upper_detailed_cab_vertices_and_polygons_exactly_unchanged':True,'all_source_animation_curves_keyframes_handles_interpolation_exactly_equal':True,'new_panel_and_lip_tire_clearance_all_192_frames':minimum,'worst_clearance_frames':worst,'clearance_method':'evaluated new cladding/wheel-well/lip vertices including modifiers against fixed front tire radius .358 at x .8,z .355, both sides','remaining_gate':'front/side/threequarter visual review'}
(P/'geometry-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
