import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(769);bpy.context.view_layer.update();cam=s.camera;s.render.resolution_x=3840;s.render.resolution_y=2667
for o in s.objects:
 if o.hide_render:o.hide_viewport=True
bpy.context.view_layer.update()
frame=cam.data.view_frame(scene=s);xmin=min(v.x for v in frame);xmax=max(v.x for v in frame);ymin=min(v.y for v in frame);ymax=max(v.y for v in frame);direction=cam.matrix_world.to_3x3()@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get();hits=[]
for y in range(378,427,6):
 for x in range(1350,1441,6):
  origin=cam.matrix_world@Vector((xmin+(x+.5)/3840*(xmax-xmin),ymin+(2667-y-.5)/2667*(ymax-ymin),0))
  ok,loc,normal,index,obj,matrix=s.ray_cast(dg,origin,direction)
  if not ok or 'PILOT 2 reconstructed' not in obj.name:continue
  face=obj.data.polygons[index];slot=face.material_index;material=obj.data.materials[slot];uv=obj.data.uv_layers.get('PaintedCamera');points=[list(uv.data[k].uv) for k in face.loop_indices] if uv else []
  hits.append({'render_pixel':[x,y],'mesh':obj.name,'face_index':index,'slot':slot,'material':material.name,'texture_names':[n.image.name for n in material.node_tree.nodes if n.type=='TEX_IMAGE'],'projected_uv_triangle':points})
(p/'blue-material-probe.json').write_text(json.dumps({'frame':769,'resolution':[3840,2667],'raycast_hits':hits},indent=2));print('MATERIALS',sorted(set((h['slot'],h['material'],tuple(h['texture_names'])) for h in hits)));print('HITS',len(hits));print('SAMPLES',hits[::max(1,len(hits)//6)])
