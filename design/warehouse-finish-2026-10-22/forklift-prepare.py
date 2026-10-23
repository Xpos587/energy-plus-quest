import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish'
bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-finish-v3.blend'));s=bpy.context.scene;cam=s.camera;W,H=1440,1000
objects=[o for o in bpy.data.objects if 'forklift' in o.name.lower() or o.name.startswith(('Finish driver ','Finish overhead guard ','Finish steering '))];dg=bpy.context.evaluated_depsgraph_get()
def project(v):
 p=world_to_camera_view(s,cam,v);return [p.x*W,(1-p.y)*H,p.z]
rows=[];allpts=[];world=[]
for o in objects:
 e=o.evaluated_get(dg);corners=[e.matrix_world@Vector(v) for v in e.bound_box];pts=[project(v) for v in corners];allpts+=pts;world+=corners
 rows.append({'object':o.name,'world_bbox_corners':[list(v) for v in corners],'projected_bbox_corners_xy_depth':pts,'world_origin':list(o.matrix_world.translation)})
b=[min(p[0] for p in allpts),min(p[1] for p in allpts),max(p[0] for p in allpts),max(p[1] for p in allpts)]
# Generous context extends below/behind exact geometry for contact shadow; no assertion that bbox proves shadow.
crop=[max(0,math.floor(b[0])-60),max(0,math.floor(b[1])-45),min(W,math.ceil(b[2])+85),min(H,math.ceil(b[3])+90)]
rec={'source':'source-v3-clean.png','immutable_blend':'warehouse-finish-v3.blend','source_dimensions':[W,H],'camera':cam.name,'camera_matrix':[list(v) for v in cam.matrix_world],'ortho_scale':cam.data.ortho_scale,'projected_geometry_bounds_xyxy':b,'source_crop_xyxy':crop,'mask_scale':2,'selection_policy':'Every existing object whose name contains forklift plus Finish driver prefix; all four wheels, both forks, mast, roof, seat, driver and beacon.','objects':rows,'world_bounds_xyz':[[min(v[a] for v in world) for a in range(3)],[max(v[a] for v in world) for a in range(3)]],'shadow_policy':'Source native crop retains original full-scene contact shadow. Shadow footprint is prepared separately as paired on/off regional render difference, not inferred from bounding box.'}
(R/'forklift-geometry-receipt.json').write_text(json.dumps(rec,indent=2))
s.render.resolution_x=W*2;s.render.resolution_y=H*2;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=crop[0]/W;s.render.border_max_x=crop[2]/W;s.render.border_min_y=1-crop[3]/H;s.render.border_max_y=1-crop[1]/H
# Emissive object ID fallback, preserving scene occlusion.
ms=[]
for value in [0,1]:
 m=bpy.data.materials.new('forklift semantic '+str(value));m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(value,value,value,1);m.node_tree.links.new(em.outputs[0],out.inputs[0]);ms.append(m)
selected_names={q.name for q in objects}
for o in list(bpy.data.objects):
 if o.type in {'MESH','FONT','CURVE'}:
  o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(ms[int(o.name in selected_names)])
  for slot in o.material_slots:slot.material=ms[int(o.name in selected_names)]
  if o.type=='MESH':
   for polygon in o.data.polygons:polygon.material_index=0
  for modifier in o.modifiers:
   if hasattr(modifier,'material'):modifier.material=0
print('MASKDEBUG',[(o.name,o.active_material.name) for o in objects]);
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Strength'].default_value=0
s.render.use_compositing=False;s.render.use_sequencer=False;s.render.engine='CYCLES';s.view_settings.view_transform='Standard';s.view_settings.look='None';s.cycles.samples=4;s.cycles.use_denoising=False;s.render.image_settings.color_mode='RGB';s.render.filepath=str(R/'forklift-semantic-mask-2x.png');bpy.ops.render.render(write_still=True)
print('FORKLIFT_RECEIPT',json.dumps({'crop':crop,'bounds':b,'objects':len(objects)}))
