import bpy,json
from pathlib import Path
from collections import deque
P=Path(__file__).resolve().parent
roots=[bpy.data.objects[f'truck-{i}-{p}']for i in range(1,5)for p in ('tractor','trailer')];fleet=set()
for r in roots:fleet.update(r.children_recursive)
mats={m for o in fleet if o.type=='MESH'and not o.hide_render for m in o.data.materials if m}
def has_normal(socket,seen=None):
 seen=set()if seen is None else seen
 for link in socket.links:
  n=link.from_node
  if n.type=='NEW_GEOMETRY'and link.from_socket.name=='Normal':return True
  if n.as_pointer()in seen:continue
  seen.add(n.as_pointer())
  if any(has_normal(i,seen)for i in n.inputs):return True
 return False
report=[]
for m in mats:
 if not m.use_nodes or 'windshield'in m.name.lower():continue
 l=m.node_tree.links
 for e in [n for n in m.node_tree.nodes if n.type=='EMISSION']:
  queue=deque([(e,0)]);seen=set();candidates=[]
  while queue:
   n,d=queue.popleft()
   if n.as_pointer()in seen:continue
   seen.add(n.as_pointer())
   if n.type=='MIX_RGB'and n.blend_type=='MULTIPLY'and has_normal(n.inputs[2]):candidates.append((d,n))
   for inp in n.inputs:
    for link in inp.links:queue.append((link.from_node,d+1))
  if len(candidates)>1:
   candidates.sort(key=lambda p:p[0]);removed=[]
   for _,n in candidates[1:]:
    if n.inputs[1].is_linked:src=n.inputs[1].links[0].from_socket
    else:
     rgb=m.node_tree.nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=n.inputs[1].default_value;src=rgb.outputs[0]
    for link in list(n.outputs[0].links):l.new(src,link.to_socket)
    removed.append(n.name)
   report.append({'material':m.name,'normal_multiply_responses_before':len(candidates),'removed_inner_responses':removed})
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v15-readable.blend'))
(P/'single-light-response.json').write_text(json.dumps({'method':'Remove redundant upstream Geometry-Normal multiply shading; preserve nearest response and image luminance/UV color masks','changed':report},indent=2))
