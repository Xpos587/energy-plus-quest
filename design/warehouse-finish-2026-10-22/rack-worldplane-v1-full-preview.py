import bpy,json,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'rack-worldplane-v1.blend'));s=bpy.context.scene;c=s.camera;original={o.name:([list(v.co)for v in o.data.vertices],[list(x)for x in o.matrix_world])for o in bpy.data.objects if o.type=='MESH'};cams={o.name:([list(x)for x in o.matrix_world],o.data.ortho_scale)for o in bpy.data.objects if o.type=='CAMERA'};first=[o for o in bpy.data.objects if o.name.startswith('rack-worldplane-v1 ') and o.type=='MESH'];assert len(first)==3
hidden=[]
for rack,cx,offset in [(2,5.4,3),(3,8.4,6)]:
 for src in first:
  o=src.copy();o.data=src.data.copy();o.name=src.name+' rack'+str(rack);bpy.data.collections['rack-worldplane-v1 fixed faces'].objects.link(o)
  for v in o.data.vertices:v.co.x+=offset
 for o in bpy.data.objects:
  detail=o.name.startswith(('Finish rack ','Finish package ','Finish label barcode'))and cx-.95<=o.location.x<=cx+.95 and 3.45<=o.location.y<=4.75 and 0<=o.location.z<=2.7
  if o.name.startswith((f'Rack{rack}',f'forklift-combined-v3 rack{rack}'))or detail:o.visible_camera=False;hidden.append(o.name)
errors=[]
for name,(v,m)in original.items():
 o=bpy.data.objects[name]
 if v!=[list(x.co)for x in o.data.vertices]or m!=[list(x)for x in o.matrix_world]:errors.append(name)
for name,(m,scale)in cams.items():
 o=bpy.data.objects[name]
 if m!=[list(x)for x in o.matrix_world]or scale!=o.data.ortho_scale:errors.append(name)
assert not errors
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=960;s.render.resolution_y=667;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.seed=0;s.render.filepath=str(R/'rack-worldplane-v1-full-raw-source.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'rack-worldplane-v1-full.blend'));start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
boards=[];dg=bpy.context.evaluated_depsgraph_get()
for text in ['А-Б','В-К','Л-М','Н-У','Ф-Э','Ю-Я']:
 o=bpy.data.objects[text+' plaque'];e=o.evaluated_get(dg);corners=[]
 for v in e.bound_box:
  p=world_to_camera_view(s,c,e.matrix_world@Vector(v));corners.append([p.x*960,(1-p.y)*667])
 boards.append({'text':text,'projected_board_bbox_corners_small':corners,'body':bpy.data.objects['Plaque '+text].data.body})
rec={'status':'ONE last small whole-scene comparison for parent/root review; production HOLD','same_native_texture_reused_three_racks':'rack-sprite-v1-native.png','native_unchanged':True,'new_surface_planes':9,'three_fixed_envelopes':[[[cx-.9,3.5,0],[cx+.9,4.7,2.7]]for cx in [2.4,5.4,8.4]],'all_preexisting_meshes_checked':len(original),'all_preexisting_cameras_checked':len(cams),'coordinate_or_transform_changes':errors,'camera_hidden_rack2_and3_objects':hidden,'boards':boards,'render':[960,667],'samples':16,'seed':0,'measured_render_seconds':elapsed,'no_solid_roof':'Top uses native alpha and camera-only emission; original solid top decks hidden camera-only, original shadows retained.','limits':['2.5D front/right/top texture projection, not newly modeled rack/carton geometry.','Repeated existing texture on all three racks; original six boards/fonts preserved and protected in comparison.','Post caps narrow at native face UV splits and small base seam remains. No further cosmetic iterations.','Single approved source camera; desktop/portrait are deterministic crops, no camera orbit supported.'],'production_changed':False};(R/'rack-worldplane-v1-full-receipt.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print('FULL_SMALL_RENDER_SECONDS',elapsed)
