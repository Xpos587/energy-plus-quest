"""Read-only rendered-surface raycast; no texture edits or saved scene changes."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import barycentric_transform
p=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(769);s.render.resolution_x=3840;s.render.resolution_y=2667
for o in s.objects:
 if o.hide_render:o.hide_viewport=True
bpy.context.view_layer.update();cam=s.camera;fr=cam.data.view_frame(scene=s);xmin=min(v.x for v in fr);xmax=max(v.x for v in fr);ymin=min(v.y for v in fr);ymax=max(v.y for v in fr);di=cam.matrix_world.to_3x3()@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get();found=[]
regions={'source_left_head':[155,181,413,442],'source_right_head':[215,243,459,490]}
for y in range(370,471,2):
 for x in range(1334,1441,2):
  origin=cam.matrix_world@Vector((xmin+(x+.5)/3840*(xmax-xmin),ymin+(2667-y-.5)/2667*(ymax-ymin),0));ok,hit,normal,idx,obj,matrix=s.ray_cast(dg,origin,di)
  if not ok or 'PILOT 2 reconstructed' not in obj.name:continue
  face=obj.data.polygons[idx];mat=obj.data.materials[face.material_index];tex=next(q for q in mat.node_tree.nodes if q.type=='TEX_IMAGE')
  if tex.image.name!='crew-cab-paint-0.png':continue
  uv=obj.data.uv_layers['PaintedCamera'];loops=list(face.loop_indices)[:3];verts=[obj.data.vertices[obj.data.loops[k].vertex_index].co for k in loops];uvs=[Vector((*uv.data[k].uv,0)) for k in loops];v=barycentric_transform(obj.matrix_world.inverted()@hit,*verts,*uvs);sourcepixel=[v.x*800,(1-v.y)*800]
  for label,(x0,x1,y0,y1) in regions.items():
   if x0<=sourcepixel[0]<=x1 and y0<=sourcepixel[1]<=y1:found.append({'source_head_region':label,'render_pixel':[x,y],'face_index':idx,'material_slot':face.material_index,'material':mat.name,'texture':tex.image.name,'source_pixel':sourcepixel})
r={'frame':769,'resolution':[3840,2667],'source_head_regions_xyxy':regions,'visible_blue_mesh_points_sampling_original_crew_heads':found,'interpretation':'Hits are rendered-visible mesh faces, after viewport-only hiding of render-hidden duplicates. Original crew head texture remains on these specific projected surfaces.' if found else 'No sampled blue mesh surface landed inside either original crew head region at this view; source-view head bounds and sampling do not certify other views.'};(p/'blue-human-material-points.json').write_text(json.dumps(r,indent=2));print('VISIBLE ORIGINAL HEAD HIT COUNT',len(found));print('SAMPLES',found[:12])
