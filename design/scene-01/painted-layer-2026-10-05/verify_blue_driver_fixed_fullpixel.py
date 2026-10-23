"""Geometry ray verification of known original two-person texture regions in both requested views."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import barycentric_transform
p=Path(__file__).resolve().parent;s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2667
for o in s.objects:
 if o.hide_render:o.hide_viewport=True
regions={'crew-cab-paint-0.png':[(155,181,413,442),(215,243,459,490)],'crew-cab-paint-1.png':[(570,602,460,490),(628,655,410,445)]}
result={}
for f,(x0,x1,y0,y1) in {1:(980,1170,1200,1370),769:(1334,1440,370,470)}.items():
 s.frame_set(f);bpy.context.view_layer.update();cam=s.camera;fr=cam.data.view_frame(scene=s);xmin=min(v.x for v in fr);xmax=max(v.x for v in fr);ymin=min(v.y for v in fr);ymax=max(v.y for v in fr);di=cam.matrix_world.to_3x3()@Vector((0,0,-1));dg=bpy.context.evaluated_depsgraph_get();hits=[];figure_pixels=0;glass_pixels=0
 for y in range(y0,y1+1,1):
  for x in range(x0,x1+1,1):
   origin=cam.matrix_world@Vector((xmin+(x+.5)/3840*(xmax-xmin),ymin+(2667-y-.5)/2667*(ymax-ymin),0));ok,hit,normal,idx,obj,matrix=s.ray_cast(dg,origin,di)
   if not ok:continue
   if obj.name=='PILOT 2 driver head':figure_pixels+=1
   if obj.name=='2 windshield':glass_pixels+=1
   if 'PILOT 2 reconstructed' not in obj.name:continue
   face=obj.data.polygons[idx];mat=obj.data.materials[face.material_index];tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
   if tex.image.name not in regions:continue
   uv=obj.data.uv_layers['PaintedCamera'];loops=list(face.loop_indices)[:3];vv=[obj.data.vertices[obj.data.loops[k].vertex_index].co for k in loops];uvs=[Vector((*uv.data[k].uv,0)) for k in loops];v=barycentric_transform(obj.matrix_world.inverted()@hit,*vv,*uvs);sx,sy=v.x*800,(1-v.y)*800
   if any(a<=sx<=b and c<=sy<=d for a,b,c,d in regions[tex.image.name]):hits.append({'render_pixel':[x,y],'face':idx,'texture':tex.image.name,'source_pixel':[sx,sy]})
 result[str(f)]={'sampled_visible_original_painted_head_points':hits,'single_existing_relief_head_sampled_points':figure_pixels,'opaque_fitted_glass_sampled_points':glass_pixels}
r={'native_dimensions':[3840,2667],'sample_step_pixels':1,'known_source_head_regions':regions,'views':result,'textures_edited':False,'claim_scope':'Two rendered views only; no full-loop human-visibility certification.'};(p/'blue-driver-fixed-fullpixel-verification.json').write_text(json.dumps(r,indent=2));print('VIEW RESULTS',result)
