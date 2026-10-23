"""Bounded proportional pass on the actual visible archived cab meshes.
Run source blend with this script; then run render_candidate.py on the saved candidate.
"""
import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;s=bpy.context.scene
roots=[o for o in s.objects if o.name.startswith('truck-')]
frames=(1,385,769)
def poses():
 result={}
 for f in (1,97,385,769,1152):
  s.frame_set(f); result[str(f)]={o.name:[list(r) for r in o.matrix_world] for o in roots}
 return result
def bounds(o):
 p=[o.matrix_local@v.co for v in o.data.vertices]
 return [[min(v[a] for v in p),max(v[a] for v in p)] for a in range(3)]
before=poses();camera={'name':s.camera.name,'matrix':[list(r) for r in s.camera.matrix_world],'scale':s.camera.data.ortho_scale}
records=[]
for i in range(1,5):
 root=bpy.data.objects[f'truck-{i}-tractor'];cab=next(o for o in root.children if 'reconstructed' in o.name)
 original=bounds(cab)
 # Preserve wheel contact/arch silhouette below z=0.90; upper shell grows smoothly.
 # A body-centred x stretch avoids drifting the tractor/trailer attach point.
 cx=(original[0][0]+original[0][1])/2
 factor=(1.22,1.10,1.12 if i in (2,3) else 1.08)
 def transform(v):
  v=v.copy();w=max(0,min(1,(v.z-.90)/.45));w=w*w*(3-2*w)
  v.x=cx+(v.x-cx)*(1+(factor[0]-1)*w);v.y*=1+(factor[1]-1)*w
  v.z=.90+(v.z-.90)*(factor[2] if v.z>.90 else 1)
  return v
 changed=[]
 for obj in root.children:
  if obj==cab or (i==2 and not obj.hide_render and any(t in obj.name for t in ('windshield','driver','passenger seat'))):
   obj.data=obj.data.copy();local=obj.matrix_local.copy();inverse=local.inverted()
   for v in obj.data.vertices:v.co=inverse@transform(local@v.co)
   obj.data.update();changed.append(obj.name)
 # Very small native edge chamfer; no outlines added, packed artwork stays source.
 bevel=cab.modifiers.new('V06 gentle shell edge rounding','BEVEL');bevel.width=.008;bevel.segments=2;bevel.limit_method='ANGLE';bevel.angle_limit=1.0
 # Soften the darkest baked fittings with a mild slate lift, keeping the paint identity.
 for m in cab.data.materials:
  n=m.node_tree.nodes;l=m.node_tree.links;em=next((x for x in n if x.type=='EMISSION'),None)
  if em and em.inputs['Color'].is_linked:
   source=em.inputs['Color'].links[0].from_socket
   mix=n.new('ShaderNodeMixRGB');mix.name='V06 soft slate contrast';mix.blend_type='MIX';mix.inputs[0].default_value=.045;mix.inputs[2].default_value=(.33,.41,.45,1);l.new(source,mix.inputs[1]);l.new(mix.outputs[0],em.inputs['Color'])
 records.append({'truck':i,'cab':cab.name,'original_bounds':original,'changed_bounds':bounds(cab),'factors':factor,'changed_objects':changed,'wheel_rule':'vertex z <= 0.90 unchanged; smooth x/y transition 0.90..1.35','bevel_width':.008})
after=poses();delta=max(abs(before[f][r][a][b]-after[f][r][a][b]) for f in before for r in before[f] for a in range(4) for b in range(4))
assert delta==0
s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100;s.frame_set(1)
receipt={'source':'design/scene-01/painted-layer-2026-10-05/painted-vehicles-driver-fixed-optimized.blend','records':records,'root_matrix_max_delta':delta,'poses_checked':list(before),'camera':camera,'dimensions':[1920,1334],'frame_range':[s.frame_start,s.frame_end],'limitations':['Visible cabs are archived textured projected meshes, not individually editable native panels.','Mild upper-body deformation and tiny bevel improve proportions; this is not a newly modelled photorealistic cab.','Baked artwork and single/pair driver identities are inherited; blue native glazing/driver overlay transformed together.']}
(O/'receipt.json').write_text(json.dumps(receipt,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'improved-fleet.blend'))
# Full map pilot first.
s.render.resolution_percentage=50;s.render.filepath=str(O/'pilot-0001.png');bpy.ops.render.render(write_still=True)
# Temporary front-oblique close camera for green: uses same full-city crypto.
s.frame_set(769);root=bpy.data.objects['truck-3-tractor'];cam=s.camera;matrix=cam.matrix_world.copy();scale=cam.data.ortho_scale
center=root.matrix_world@Vector((0,0,1.65));cam.location=root.matrix_world@Vector((10,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.5
s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=str(O/'green-front-close.png');bpy.ops.render.render(write_still=True)
cam.matrix_world=matrix;cam.data.ortho_scale=scale
print('V06 PILOT COMPLETE root max delta',delta)
