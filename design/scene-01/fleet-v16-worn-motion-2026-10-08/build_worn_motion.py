import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Euler
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
roots={i:bpy.data.objects[f'truck-{i}-tractor'] for i in (1,4)}
affected={i:[bpy.data.objects[f'V02 DETAILED {i} complete tractor'],bpy.data.objects[f'V14 {i} seated lower windshield gasket']] for i in (1,4)}
all_affected=set()
for values in affected.values():
 for o in values:all_affected.add(o);all_affected.update(o.children_recursive)
protected=[o for o in s.objects if o not in all_affected and (not o.hide_render or o.type=='CAMERA')]
base_world={};root_world={};cab_local={};roof_points={}
for i,root in roots.items():
 cab=affected[i][0];local=root.matrix_world.inverted()@cab.matrix_world;cab_local[i]=local
 points=[local@v.co for v in cab.data.vertices];top=max(v.z for v in points);pts=[v for v in points if v.z>top-.03]
 roof_points[i]=sum(pts,Vector())/len(pts)
for f in range(1,193):
 s.frame_set(f);bpy.context.view_layer.update();base_world[f]={o.name:o.matrix_world.copy() for o in protected};root_world[f]={i:r.matrix_world.copy() for i,r in roots.items()}
pivot=Vector((.8,0,.9))
def motion(i,f,heave,roll):
 t=(f-1)/24;hz=2.2 if i==1 else 2.6;phase=.0 if i==1 else 1.15;w=2*math.pi*hz*t+phase
 z=heave*(.78*math.sin(w)+.22*math.sin(1.71*w+.6))
 rx=math.radians(roll)*(.80*math.sin(w+.45)+.20*math.sin(1.43*w+1.1))
 if i==4:rx=-rx
 ry=math.radians(.25)*math.sin(w+.9)
 return z,rx,ry
def measure(heave,roll):
 out={}
 for i in (1,4):
  offsets=[]
  for f in range(1,193):
   z,rx,ry=motion(i,f,heave,roll);M=Matrix.Translation(pivot+Vector((0,0,z)))@Euler((rx,ry,0),'XYZ').to_matrix().to_4x4()@Matrix.Translation(-pivot)
   base=root_world[f][i]@roof_points[i];now=root_world[f][i]@M@roof_points[i];a=world_to_camera_view(s,s.camera,base);b=world_to_camera_view(s,s.camera,now);offsets.append(((b.x-a.x)*960,(b.y-a.y)*667))
  out[i]={'peak_to_peak_x_px_960':max(x for x,y in offsets)-min(x for x,y in offsets),'peak_to_peak_y_px_960':max(y for x,y in offsets)-min(y for x,y in offsets),'max_offset_px_960':max(math.hypot(x,y) for x,y in offsets)}
 return out
initial=measure(.035,1.0);heave=.07;roll=1.3;final=measure(heave,roll)
s.frame_set(1);bpy.context.view_layer.update();groups={}
for i,root in roots.items():
 group=bpy.data.objects.new(f'WORN {i} isolated cab suspension',None);s.collection.objects.link(group);group.parent=root;group.location=pivot;bpy.context.view_layer.update();groups[i]=group
 for o in affected[i]:
  world=o.matrix_world.copy();o.parent=group;o.matrix_world=world
 for f in range(1,193):
  z,rx,ry=motion(i,f,heave,roll);group.location=pivot+Vector((0,0,z));group.rotation_euler=(rx,ry,0);group.keyframe_insert('location',frame=f);group.keyframe_insert('rotation_euler',frame=f)
# Read back every protected object through all192 source animation frames.
max_protected_error=0;limits={i:{'max_heave_local':0,'max_roll_degrees':0,'max_pitch_degrees':0,'max_roof_displacement_world':0} for i in (1,4)}
for f in range(1,193):
 s.frame_set(f);bpy.context.view_layer.update()
 for o in protected:
  error=max(abs(a-b) for rowa,rowb in zip(o.matrix_world,base_world[f][o.name]) for a,b in zip(rowa,rowb));max_protected_error=max(max_protected_error,error);assert error<1e-6,(o.name,f,error)
 for i,group in groups.items():
  v=limits[i];v['max_heave_local']=max(v['max_heave_local'],abs(group.location.z-.9));v['max_roll_degrees']=max(v['max_roll_degrees'],abs(math.degrees(group.rotation_euler.x)));v['max_pitch_degrees']=max(v['max_pitch_degrees'],abs(math.degrees(group.rotation_euler.y)))
  current=group.matrix_world@Matrix.Translation(-pivot)@roof_points[i];baseline=root_world[f][i]@roof_points[i];v['max_roof_displacement_world']=max(v['max_roof_displacement_world'],(current-baseline).length)
s.frame_set(96);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v16-worn-motion.blend'))
receipt={'source':'../fleet-v16-smoke-2026-10-08/fleet-v16-smoke.blend','affected_top_level':{i:[o.name for o in objects] for i,objects in affected.items()},'affected_with_descendants':sorted(o.name for o in all_affected),'pivot_root_local':list(pivot),'initial_screen_measurement':initial,'final_screen_measurement':final,'measured_limits':limits,'protected_object_count':len(protected),'protected_frames_checked':192,'max_protected_world_matrix_error':max_protected_error,'protected_includes':'all wheels/chassis/front arch trim/hitches/trailers, all green+blue, all stacks+smoke, camera; exact source world matrices','stack_policy':'unchanged chassis-mounted stack and unchanged final smoke emission'}
(P/'worn-motion-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
