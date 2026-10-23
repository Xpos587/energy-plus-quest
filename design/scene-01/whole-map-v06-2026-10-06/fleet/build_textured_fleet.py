"""Detailed v02 whole-tractor GLB integration; original source model, no v03."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;ROOT=O.parents[3];s=bpy.context.scene;roots=[o for o in s.objects if o.name.startswith('truck-')]
source=ROOT/'design/scene-01/truck-native-quality-2026-10-05/image-to-3d/green-tractor-detailed.blend'
def poses():
 r={}
 for f in (1,385,769,1152):
  s.frame_set(f);r[str(f)]={o.name:[list(row) for row in o.matrix_world] for o in roots}
 return r
before=poses();cam_original=[list(r) for r in s.camera.matrix_world]
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=['Mesh_0']
base=dst.objects[0];records=[];tex_single=bpy.data.images.load(str(O/'single-driver-windshield.png'));tex_single.pack()
for i in range(1,5):
 root=bpy.data.objects[f'truck-{i}-tractor'];hidden=[]
 for o in root.children_recursive:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=True;hidden.append(o.name)
 o=bpy.data.objects.new(f'V02 DETAILED {i} complete tractor',base.data.copy());s.collection.objects.link(o);o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o.rotation_mode='XYZ';o.rotation_euler=(0,0,math.pi);o.scale=(2.2,2.2,2.2);o.location=(1.48-.9504969*2.2,0,.58552092*2.2)
 # Per-truck materials. Source shader already selects green body pigment without global tinting.
 for idx,m in enumerate(list(o.data.materials)):
  m=m.copy();o.data.materials[idx]=m;m.name=f'V02 {i} '+m.name
  if idx==0:
   node=m.node_tree.nodes.get('Mix (Legacy).001');node.inputs[2].default_value={1:(.66,.105,.070,1),2:(.025,.23,.63,1),3:(.26,.49,.13,1),4:(.82,.49,.065,1)}[i]
  else:
   for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE' and i!=3:n.image=tex_single
 # Only roof vertices above windshield: z>.35, windows end at.248. Tyres/chassis untouched.
 roof_factor=.88 if i==1 else .80 if i==4 else 1
 if roof_factor!=1:
  for v in o.data.vertices:
   if v.co.z>.35:v.co.z=.35+(v.co.z-.35)*roof_factor
  o.data.update()
 records.append({'truck':i,'object':o.name,'hidden_original_tractor_meshes':len(hidden),'uniform_scale':2.2,'rotation_z':math.pi,'location':list(o.location),'roof_above_z':.35,'roof_factor':roof_factor,'driver_texture_count':2 if i==3 else 1,'materials_copied':len(o.data.materials)})
bpy.data.objects.remove(base,do_unlink=True)
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');crypto.matte_id=', '.join(o.name for r in roots for o in r.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
after=poses();delta=max(abs(before[f][r][a][b]-after[f][r][a][b]) for f in before for r in before[f] for a in range(4) for b in range(4));assert delta==0
s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
receipt={'source':str(source),'records':records,'root_matrix_max_delta':delta,'camera_matrix':cam_original,'frames':[1,769],'dimensions':[1920,1334],'single_reference':'design/scene-01/cab-detail-pilot-2026-10-05/single-driver-detail-reference.png','single_reference_crop':[455,229,338,150],'windshield_method':'reuse permanent shader and UV projection from restore_driver_detail.py; swap only windshield material texture','limitations':['Red/yellow use modern detailed source with roof compression and pigment change; exact historical cab shapes not reconstructed.','Drivers are windshield textures, not volumetric people.','Trailer geometry retained unchanged.']}
(O/'textured-receipt.json').write_text(json.dumps(receipt,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'fleet-textured-v02.blend'))
for f in (1,769):s.frame_set(f);s.render.filepath=str(O/f'textured-vehicles-{f:04}.png');bpy.ops.render.render(write_still=True)
# Isolated close tests retain desktop angle then front angle; only QA scene changes.
fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
for obj in s.objects:
 if obj.type in ('MESH','FONT','CURVE') and obj not in fleet:obj.hide_render=True
root=bpy.data.objects['truck-3-tractor'];cam=s.camera;center=root.matrix_world@Vector((0,0,1.5));view=cam.matrix_world.to_quaternion()@Vector((0,0,1));cam.location=center+view*35;cam.data.ortho_scale=6;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.filepath=str(O/'textured-green-desktop-close.png');bpy.ops.render.render(write_still=True)
cam.location=root.matrix_world@Vector((10,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/'textured-green-front-close.png');bpy.ops.render.render(write_still=True)
root=bpy.data.objects['truck-2-tractor'];center=root.matrix_world@Vector((0,0,1.5));cam.location=root.matrix_world@Vector((10,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/'textured-blue-front-close.png');bpy.ops.render.render(write_still=True)
print('TEXTURED PILOT COMPLETE')
