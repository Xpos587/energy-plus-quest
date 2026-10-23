import bpy,json
from pathlib import Path
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-finish-2026-10-22';R=ROOT/'docs/reviews/inventory-2026-10-22-finish'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'design/warehouse-blockout-2026-10-21/warehouse-blockout-v4.blend'))
original={o.name:([list(v.co) for v in o.data.vertices],[list(row) for row in o.matrix_world]) for o in bpy.data.objects if o.type=='MESH'};cams={o.name:([list(row) for row in o.matrix_world],o.data.ortho_scale) for o in bpy.data.objects if o.type=='CAMERA'}
bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-finish-v2.blend'));S=bpy.context.scene
errors=[]
for n,(v,m) in original.items():
 o=bpy.data.objects[n]
 if [list(x.co) for x in o.data.vertices]!=v or [list(row) for row in o.matrix_world]!=m:errors.append(n)
for n,(m,scale) in cams.items():
 o=bpy.data.objects[n]
 if [list(row) for row in o.matrix_world]!=m or o.data.ortho_scale!=scale:errors.append(n)
labels=[o.data.body for o in bpy.data.objects if o.name.startswith('Plaque ')]
assert not errors,errors
assert sorted(labels)==sorted(['А-Б','В-К','Л-М','Н-У','Ф-Э','Ю-Я']),labels
rec={'original_meshes_checked':len(original),'original_cameras_checked':len(cams),'coordinate_or_transform_changes':errors,'literal_labels':labels,'full_source':[1440,1000],'source_provenance':'warehouse-blockout-v4.blend','changed_visibility':['Original keeper cuboid silhouettes hidden; additive keeper same location','Original solid guard roof hidden; additive grille in same envelope','Original truck roof and side skins revealed'],'production_touched':False}
(R/'geometry-preservation-v2.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
S.render.engine='BLENDER_WORKBENCH';S.camera=bpy.data.objects['FullSourceOverscan'];S.render.resolution_x=1440;S.render.resolution_y=1000;S.display.shading.show_shadows=False;S.display.shading.show_cavity=False;S.display.shading.show_object_outline=False;S.display.shading.background_type='VIEWPORT';S.display.shading.background_color=(0,0,0)
colors={'architecture':(.6,.6,.6,1),'receiving':(.05,.8,.8,1),'dispatch':(.8,.1,.8,1),'rack1':(.9,.1,.1,1),'rack2':(.1,.8,.1,1),'rack3':(.1,.2,.9,1),'forklift':(.95,.45,.05,1),'keeper':(.95,.8,.05,1),'wms':(.1,.55,.4,1),'truck':(.4,.15,.6,1),'drone':(.85,.35,.55,1),'pallet':(.5,.3,.1,1)}
lookup={}
for o in bpy.data.objects:
 k='architecture';n=o.name.lower()
 for prefix,cat in [('приёмка','receiving'),('отгрузка','dispatch'),('rack1','rack1'),('rack2','rack2'),('rack3','rack3'),('forklift','forklift'),('keeper','keeper'),('wms','wms'),('truck','truck'),('drone','drone'),('receiving eur','pallet'),('floor staged','pallet')]:
  if prefix in n:k=cat;break
 if 'plaque' in n:k='rack'+str(min(range(3),key=lambda i:abs(o.location.x-[2.4,5.4,8.4][i]))+1)
 o.color=colors[k];lookup[o.name]=k
S.display.shading.light='FLAT';S.display.shading.color_type='OBJECT';S.render.filepath=str(R/'source-v2-semantic-id.png');bpy.ops.render.render(write_still=True)
S.display.shading.light='MATCAP';S.display.shading.studio_light='check_normal+y.exr';S.render.filepath=str(R/'source-v2-normal-check.png');bpy.ops.render.render(write_still=True)
(R/'structural-legend-v2.json').write_text(json.dumps({'colors_linear_rgba':colors,'object_categories':lookup,'limits':'Antialiased semantic colors are not integer IDs. Normal check is Blender matcap for surface-direction inspection, not calibrated world normals.'},indent=2))
print('VALIDATION AND PASSES COMPLETE')
