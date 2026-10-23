import bpy,json,time,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'forklift-combined-v2-no-outline.blend'));s=bpy.context.scene;before={o.name:([list(v.co) for v in o.data.vertices],[list(x) for x in o.matrix_world])for o in bpy.data.objects if o.type=='MESH'};cams={o.name:([list(x)for x in o.matrix_world],o.data.ortho_scale)for o in bpy.data.objects if o.type=='CAMERA'}
collection=bpy.data.collections.new('forklift-combined-v3 bounded identity');s.collection.children.link(collection);added=[];arch=[];fits=[]
def mat(name,color):
 m=bpy.data.materials.new('forklift-combined-v3 '+name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.62;return m
blue=mat('saturated blue steel',(.008,.075,.44));orange=mat('orange steel',(1,.18,.004));white=mat('white wrapped pack',(.91,.93,.91));paper=mat('warm carton',(.69,.39,.17));ivory=mat('ivory dispatch wall',(.86,.85,.77));doorblue=mat('blue shutter',(.012,.16,.56));doordark=mat('shutter slat seam',(.012,.065,.22))
def box(name,p,d,m,category,rack=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name='forklift-combined-v3 '+name;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 collection.objects.link(o);o.data.materials.append(m);bevel=o.modifiers.new('tiny material edge','BEVEL');bevel.width=.008;bevel.segments=2
 lo=[p[a]-d[a]/2 for a in range(3)];hi=[p[a]+d[a]/2 for a in range(3)]
 if rack is not None:
  cx=[2.4,5.4,8.4][rack-1];limits=[[cx-.9,3.5,0],[cx+.9,4.7,2.7]];assert all(lo[a]>=limits[0][a]-1e-5 and hi[a]<=limits[1][a]+1e-5 for a in range(3)),(name,lo,hi)
 added.append({'name':o.name,'category':category,'world_bbox':[lo,hi],'rack':rack});return o
for o in list(bpy.data.objects):
 if o.type=='MESH' and o.name.startswith('Rack'):
  if 'deck' in o.name:o.data.materials.clear();o.data.materials.append(blue)
  if 'beam' in o.name:o.data.materials.clear();o.data.materials.append(orange)
  if 'upright' in o.name:o.data.materials.clear();o.data.materials.append(blue)
# Upright casing grows inward only; original uprights remain untouched.
for rack,cx in enumerate([2.4,5.4,8.4],1):
 for x in [cx-.85,cx,cx+.85]:
  for y in [3.55,4.65]:box(f'rack{rack} inward upright casing',(x,y,1.35),(.10,.10,2.7),blue,'inward steel casing',rack)
 for z in [.15,1,1.85,2.625]:
  for y in [3.55,4.65]:box(f'rack{rack} beam face',(cx,y,z),(1.8,.10,.15 if z>2.6 else .13),orange,'inward beam casing',rack)
 # Smaller parcels physically stacked on existing cartons, inside free vertical gaps.
 for bay,x in enumerate([cx-.45,cx+.45]):
  for depth,y in enumerate([3.85,4.35]):
   for level,top in enumerate([.66,1.52,2.36]):
    h=.23 if level<2 else .20;w=.42 if (rack+bay+level)%2 else .53;dep=.34 if depth==0 else .38
    box(f'rack{rack} bay{bay+1} stack{level+1} depth{depth+1}',(x+(.035 if level%2 else -.025),y,top+h/2),(w,dep,h),white if (rack+bay+depth+level)%3==0 else paper,'additional parcel within free shelf gap',rack)
# Exact original boards and text origins/order retained. Only glyph size/font/material changes.
font=bpy.data.fonts.load('/usr/share/fonts/TTF/DejaVuSans-Bold.ttf')
for o in bpy.data.objects:
 if o.type=='FONT' and o.name.startswith('Plaque '):
  old=o.data.size;o.data.font=font;o.data.size=.36;o.data.materials.clear();o.data.materials.append(blue);bpy.context.view_layer.update();board=bpy.data.objects[o.data.body+' plaque'];fits.append({'text':o.data.body,'old_font_size':old,'font_size':o.data.size,'glyph_dimensions':list(o.dimensions),'board_dimensions':list(board.dimensions),'fits_board':o.dimensions.x<board.dimensions.x-.06 and max(o.dimensions.y,o.dimensions.z)<board.dimensions.z-.04});assert fits[-1]['fits_board']
# True X=12 dispatch plane. Explicit cutaway: south/front return stays open;
# rear section Y3.85..7.5 restored full-height, lower/front sill unchanged.
arch.append(box('dispatch rear ivory wall',(12,5.675,1.9),(.16,3.65,3.4),ivory,'dispatch wall on X12'))
arch.append(box('dispatch short south return',(12,.28,.65),(.16,.56,.9),ivory,'dispatch front low cutaway return'))
# Existing opening clear Y .70..3.70, Z0..3.0. Upper 0.80m shutter is lowered.
for i in range(6):
 z=2.23+i*.14;arch.append(box(f'dispatch blue upper slat {i+1}',(12,2.2,z),(.055,2.98,.127),doorblue,'partly raised blue roll-up door'))
 arch.append(box(f'dispatch slat seam {i+1}',(12.033,2.2,z+.062),(.008,2.98,.008),doordark,'door seam on same X12 plane'))
bpy.context.view_layer.update();cam=bpy.data.objects['FullSourceOverscan'];s.camera=cam;normal=cam.matrix_world.to_quaternion()@Vector((0,0,1))
# Analytic ray/box intersection against every added dispatch component, using
# orthographic camera-parallel rays to actual keeper card and WMS surface samples.
def segment_hits(origin,target,b):
 delta=target-origin;lo,hi=b;tmin,tmax=0,1
 for a in range(3):
  if abs(delta[a])<1e-9:
   if origin[a]<lo[a] or origin[a]>hi[a]:return False
  else:
   t0=(lo[a]-origin[a])/delta[a];t1=(hi[a]-origin[a])/delta[a];tmin=max(tmin,min(t0,t1));tmax=min(tmax,max(t0,t1))
   if tmax<tmin:return False
 return True
keeper=bpy.data.objects['Keeper illustrated proof card'];v=[keeper.matrix_world@x.co for x in keeper.data.vertices];samples=[]
for u in [.25,.5,.75]:
 for t in [.15,.5,.85]:samples.append(('keeper card sample',v[0]*(1-u)*(1-t)+v[1]*u*(1-t)+v[2]*u*t+v[3]*(1-u)*t))
for x in [9.3,9.5,9.7]:
 for z in [.95,1.1,1.25]:samples.append(('WMS screen sample',Vector((x,.963,z))))
visibility=[]
for name,p in samples:
 origin=p+normal*100;blockers=[o.name for o in arch if segment_hits(origin,p,next(x['world_bbox']for x in added if x['name']==o.name))];uv=world_to_camera_view(s,cam,p);visibility.append({'sample':name,'world':list(p),'source_xy':[uv.x*1440,(1-uv.y)*1000],'new_dispatch_blockers':blockers});assert not blockers,(name,blockers)
errors=[]
for name,(v,m)in before.items():
 o=bpy.data.objects[name]
 if v!=[list(x.co)for x in o.data.vertices]or m!=[list(x)for x in o.matrix_world]:errors.append(name)
for name,(m,scale)in cams.items():
 o=bpy.data.objects[name]
 if m!=[list(x)for x in o.matrix_world]or scale!=o.data.ortho_scale:errors.append(name)
assert not errors,errors
s.render.use_freestyle=False;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=960;s.render.resolution_y=667;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.seed=0;s.render.filepath=str(R/'forklift-combined-v3-source.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'forklift-combined-v3.blend'));start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
(R/'forklift-combined-v3-receipt.json').write_text(json.dumps({'status':'one small identity/cutaway comparison preview only','render':[960,667],'measured_render_seconds':elapsed,'all_original_base_meshes_checked':len(before),'all_cameras_checked':len(cams),'coordinate_or_transform_changes':errors,'additions':added,'plaques':fits,'ray_visibility_new_architecture':visibility,'visibility_limits':['Ray validation addresses added dispatch architecture only; card samples include transparent sprite areas, not semantic visible-fraction proof. Visual viewport inspection remains required.','Dispatch front/south wall remains intentional cutaway; rear wall restored at true X12, upper0.8m door slats restored. Opening remains at least2.16m high.','Rack gaps remain1.2m pedestrian/service aisles; no forklift turning certification.'],'native_sprites_changed':False,'production_changed':False},ensure_ascii=False,indent=2));print('V3_RENDER_SECONDS',elapsed)
