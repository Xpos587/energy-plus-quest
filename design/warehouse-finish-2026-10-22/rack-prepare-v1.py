import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'forklift-combined-v3.blend'));s=bpy.context.scene;cam=bpy.data.objects['FullSourceOverscan'];s.camera=cam;W,H=1440,1000;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;dg=bpy.context.evaluated_depsgraph_get()
boards=[bpy.data.objects[n+' plaque']for n in ['А-Б','В-К']];letters=[bpy.data.objects['Plaque '+n]for n in ['А-Б','В-К']];rack=[o for o in bpy.data.objects if o.name.startswith(('Rack1','forklift-combined-v3 rack1'))];details=[o for o in bpy.data.objects if o.name.startswith(('Finish rack ','Finish package ','Finish label barcode')) and 1.45<=o.location.x<=3.35 and 3.45<=o.location.y<=4.75 and 0<=o.location.z<=2.7];rack+=details;selected=rack+boards+letters
original={o.name:([list(v.co)for v in o.data.vertices],[list(x)for x in o.matrix_world])for o in bpy.data.objects if o.type=='MESH'}
def px(v):
 p=world_to_camera_view(s,cam,v);return[p.x*W,(1-p.y)*H,p.z]
rows=[];points=[]
for o in selected:
 e=o.evaluated_get(dg);corners=[e.matrix_world@Vector(v)for v in e.bound_box];p=[px(v)for v in corners];points+=p;rows.append({'object':o.name,'world_bbox_corners':[list(v)for v in corners],'projected_bbox_corners_xy_depth':p})
bounds=[min(p[0]for p in points),min(p[1]for p in points),max(p[0]for p in points),max(p[1]for p in points)];crop=[math.floor(bounds[0])-45,math.floor(bounds[1])-40,math.ceil(bounds[2])+45,math.ceil(bounds[3])+45]
anchors=[]
for b,t in zip(boards,letters):
 anchors.append({'text':t.data.body,'board_world_center':list(b.location),'board_projected_center_xy_depth':px(b.matrix_world.translation),'letter_world_origin':list(t.location),'letter_projected_origin_xy_depth':px(t.matrix_world.translation),'font_size':t.data.size,'font_path':t.data.font.filepath,'board_geometry_unchanged':True})
# An open-racking candidate hides ONLY the solid top deck to camera. Original
# top-deck vertices, placement and shadow casting are retained; orange beams stay.
cap=bpy.data.objects['Rack1 deck.003'];cap.visible_camera=False
x0,y0,x1,y1=crop;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/W;s.render.border_max_x=x1/W;s.render.border_min_y=1-y1/H;s.render.border_max_y=1-y0/H;s.render.use_freestyle=False;s.cycles.samples=16;s.cycles.seed=0;s.render.filepath=str(R/'rack-geometry-open-cap-crop-native.png');start=time.perf_counter();bpy.ops.wm.save_as_mainfile(filepath=str(D/'rack-open-cap-preparation-v1.blend'));bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
errors=[]
for n,(v,m)in original.items():
 o=bpy.data.objects[n]
 if v!=[list(x.co)for x in o.data.vertices]or m!=[list(x)for x in o.matrix_world]:errors.append(n)
assert not errors
rec={'status':'first-rack geometry/style preparation only; no art acceptance','source_blend':'forklift-combined-v3.blend','source_dimensions':[W,H],'camera':cam.name,'camera_matrix':[list(v)for v in cam.matrix_world],'ortho_scale':cam.data.ortho_scale,'rack_physical_envelope':[[1.5,3.5,0],[3.3,4.7,2.7]],'projected_geometry_bounds_xyxy':bounds,'source_crop_xyxy':crop,'crop_dimensions':[x1-x0,y1-y0],'all_projected_corners':rows,'plaque_anchors':anchors,'all_six_exact_labels':['А-Б','В-К','Л-М','Н-У','Ф-Э','Ю-Я'],'camera_only_hidden_cap':'Rack1 deck.003','cap_shadow_preserved':True,'all_existing_meshes_checked':len(original),'coordinate_or_transform_changes':errors,'measured_crop_render_seconds':elapsed,'preserve_labels_method':'Hide only selected rack/stock from camera when replacing with sprite; retain both original 3D plaque boards/fonts. Put camera-facing card behind projected front plaque plane (depth farther from camera), so original board/text wins depth. Final protected paired composite restores exact source board/text pixels via plaque mask regardless of render-depth roundoff. Never accept generated labels. Other four original boards/fonts remain unchanged.','native_sprites_changed':False,'production_changed':False};(R/'rack-geometry-preparation-v1.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
# Occlusion-aware colour ID fallback: rack red, boards green, exact glyphs blue.
colors=[(0,0,0,1),(1,0,0,1),(0,1,0,1),(0,0,1,1)];mats=[]
for i,color in enumerate(colors):
 m=bpy.data.materials.new('rack ID '+str(i));m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=color;m.node_tree.links.new(em.outputs[0],out.inputs[0]);mats.append(m)
racknames={o.name for o in rack};bn={o.name for o in boards};tn={o.name for o in letters}
for o in list(bpy.data.objects):
 if o.type not in {'MESH','FONT','CURVE'}:continue
 i=3 if o.name in tn else 2 if o.name in bn else 1 if o.name in racknames else 0;o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(mats[i])
 for slot in o.material_slots:slot.material=mats[i]
 if o.type=='MESH':
  for p in o.data.polygons:p.material_index=0
 for modifier in o.modifiers:
  if hasattr(modifier,'material'):modifier.material=0
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND':n.inputs['Strength'].default_value=0
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.render.use_compositing=False;s.render.use_sequencer=False;s.cycles.samples=4;s.cycles.use_denoising=False;s.render.resolution_x=W*2;s.render.resolution_y=H*2;s.render.filepath=str(R/'rack-semantic-id-2x.png');bpy.ops.render.render(write_still=True);print('RACK_PREP_READY',json.dumps({'bounds':bounds,'crop':crop,'objects':len(selected)}))
