import bpy,json,math
from mathutils import Vector
s=bpy.context.scene;s.frame_set(1)
for i in range(1,5):
 r=bpy.data.objects[f'truck-{i}-tractor'];o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];m=r.matrix_world.inverted()@o.matrix_world
 print('TRACTOR',i)
 for idx,slot in enumerate(o.material_slots):
  verts={v for p in o.data.polygons if p.material_index==idx for v in p.vertices};pts=[m@o.data.vertices[v].co for v in verts]
  if pts:print(slot.name,len(pts),[[round(min(p[k] for p in pts),4),round(max(p[k] for p in pts),4)] for k in range(3)])
 # connected mesh islands
 links=[[] for v in o.data.vertices]
 for e in o.data.edges:a,b=e.vertices;links[a].append(b);links[b].append(a)
 seen=set();islands=[]
 for v in range(len(links)):
  if v in seen:continue
  todo=[v];seen.add(v);ids=[]
  while todo:
   a=todo.pop();ids.append(a)
   for b in links[a]:
    if b not in seen:seen.add(b);todo.append(b)
  pts=[m@o.data.vertices[v].co for v in ids];bounds=[[round(min(p[k] for p in pts),4),round(max(p[k] for p in pts),4)] for k in range(3)]
  if len(ids)>50:islands.append((len(ids),bounds))
 print('ISLANDS',islands)
angles={i:[] for i in range(1,5)}
for f in range(1,1153):
 s.frame_set(f)
 for i in angles:
  r=bpy.data.objects[f'truck-{i}-tractor'];t=bpy.data.objects[f'truck-{i}-trailer'];a=math.atan2(math.sin(t.rotation_euler.z-r.rotation_euler.z),math.cos(t.rotation_euler.z-r.rotation_euler.z));angles[i].append((abs(a),f,a))
for i,a in angles.items():print('MAXANGLE',i,max(a),'HITCH',list(bpy.data.objects[f'truck-{i}-tractor'].matrix_world.inverted()@bpy.data.objects[f'truck-{i}-trailer'].matrix_world.translation))
