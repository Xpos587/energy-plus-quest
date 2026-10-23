import bpy,json,math
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).parent;s=bpy.context.scene
roots=[bpy.data.objects[n] for n in ('truck-3-tractor','truck-3-trailer')];keep=set(roots)
for r in roots:keep.update(r.children_recursive)
for o in s.objects:
 if o.type not in ('CAMERA','LIGHT') and o not in keep:o.hide_render=True
vis=[o for o in keep if o.type=='MESH' and not o.hide_render]
pts=[];trans=[]
for f in range(85,218):
 s.frame_set(f)
 trans.append({'frame':f,'roots':{r.name:{'loc':list(r.location),'rot':list(r.rotation_euler)} for r in roots}})
 for o in vis:
  pts.extend(world_to_camera_view(s,s.camera,o.matrix_world @ __import__('mathutils').Vector(c)) for c in o.bound_box)
mnx=min(p.x for p in pts);mxx=max(p.x for p in pts);mny=min(p.y for p in pts);mxy=max(p.y for p in pts)
pad=.012
roi=[mnx-pad,mny-pad,mxx+pad,mxy+pad]
W=int(math.ceil(960/(roi[2]-roi[0])/2)*2);H=int(round(W*2667/3840/2)*2)
s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=roi[0];s.render.border_max_x=roi[2];s.render.border_min_y=roi[1];s.render.border_max_y=roi[3]
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16;s.render.film_transparent=True;s.render.use_freestyle=False
# Remove city cryptomatte compositor; direct isolated render.
s.use_nodes=False;s.compositing_node_group=None
s.render.image_settings.color_mode='RGBA';s.render.image_settings.file_format='PNG'
s.frame_set(120);s.render.filepath=str(O/'structural-still.png');bpy.ops.render.render(write_still=True)
(O/'source-geometry-inspection.json').write_text(json.dumps({'source_frames':[85,217],'output_frames':72,'fps':12,'camera':s.camera.name,'camera_matrix':[list(r) for r in s.camera.matrix_world],'roi_normalized':roi,'full_render':[W,H],'visible_meshes':[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'materials':[m.name for m in o.data.materials]} for o in vis],'transforms':trans},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'isolated-source.blend'))
