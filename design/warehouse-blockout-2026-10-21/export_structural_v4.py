import bpy,json
from pathlib import Path
D=Path('/home/michael/Github/energy-plus-quest/design/warehouse-blockout-2026-10-21');R=Path('/home/michael/Github/energy-plus-quest/docs/reviews/inventory-2026-10-21-geometry');bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-blockout-v4.blend'));S=bpy.context.scene;m=json.loads((D/'manifest-v4.json').read_text());bpy.data.collections['Guides'].hide_render=True
colors={'architecture':(.7,.7,.7,1),'receiving':(.05,.8,.8,1),'dispatch':(.8,.1,.8,1),'rack1':(.9,.1,.1,1),'rack2':(.1,.8,.1,1),'rack3':(.1,.2,.9,1),'forklift':(.95,.45,.05,1),'keeper':(.95,.8,.05,1),'wms':(.1,.55,.4,1),'truck':(.4,.15,.6,1),'drone':(.85,.35,.55,1),'pallet':(.5,.3,.1,1)}
lookup={}
for o in bpy.data.objects:
 k='architecture';n=o.name
 for prefix,cat in [('ПРИЁМКА','receiving'),('ОТГРУЗКА','dispatch'),('Rack1','rack1'),('Rack2','rack2'),('Rack3','rack3'),('Forklift','forklift'),('Keeper','keeper'),('WMS','wms'),('Truck','truck'),('Drone','drone'),('Receiving EUR','pallet'),('Floor staged','pallet')]:
  if n.startswith(prefix):k=cat;break
 if 'plaque' in n or n.startswith('Plaque '):k='rack'+str(min(range(3),key=lambda i:abs(o.location.x-[2.4,5.4,8.4][i]))+1)
 o.color=colors[k];lookup[n]=k
S.display.shading.show_shadows=False;S.display.shading.show_cavity=False;S.display.shading.show_object_outline=False;S.display.shading.background_type='VIEWPORT';S.display.shading.background_color=(0,0,0)
for name in ['Desktop','Portrait','Source']:
 camera='FullSourceOverscan' if name=='Source' else name;S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=m['cameras'][name]['resolution']
 S.display.shading.light='FLAT';S.display.shading.color_type='OBJECT';S.render.filepath=str(R/(name.lower()+'-v4-semantic-id.png'));bpy.ops.render.render(write_still=True)
 S.display.shading.light='MATCAP';S.display.shading.studio_light='check_normal+y.exr';S.render.filepath=str(R/(name.lower()+'-v4-normal-check.png'));bpy.ops.render.render(write_still=True)
(R/'structural-pass-legend-v4.json').write_text(json.dumps({'semantic_color_legend_linear_rgba':colors,'object_semantics':lookup,'limits':'Semantic color render includes antialiasing; not integer IDs. Normal check is Blender check_normal+y matcap for surface direction inspection, not calibrated world-normal data. No scene source modified.'},ensure_ascii=False,indent=2)+'\n')
