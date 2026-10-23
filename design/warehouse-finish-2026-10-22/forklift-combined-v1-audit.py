import bpy,json
from pathlib import Path
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-finish-2026-10-22';R=ROOT/'docs/reviews/inventory-2026-10-22-finish'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'design/warehouse-blockout-2026-10-21/warehouse-blockout-v4.blend'))
original={o.name:([list(v.co) for v in o.data.vertices],[list(row) for row in o.matrix_world]) for o in bpy.data.objects if o.type=='MESH'};cams={o.name:([list(row) for row in o.matrix_world],o.data.ortho_scale) for o in bpy.data.objects if o.type=='CAMERA'}
bpy.ops.wm.open_mainfile(filepath=str(D/'forklift-billboard-v1.blend'));S=bpy.context.scene
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
rec={'original_meshes_checked':len(original),'original_cameras_checked':len(cams),'coordinate_or_transform_changes':errors,'literal_labels':labels,'full_source':[1440,1000],'source_provenance':'warehouse-blockout-v4.blend','changed_visibility':['Original keeper cuboid silhouettes hidden; additive keeper same location','Original solid guard roof hidden; additive grille in same envelope','Original truck roof and side skins revealed'],'additional_sprite_changes':['Keeper illustrated proof card camera-only; original keeper shadow retained','Window panorama surface textures in existing window planes','Forklift painted proof card camera-only; original forklift/driver/grille/steering remain non-camera shadow casters'],'production_touched':False}
(R/'forklift-combined-v1-geometry.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
