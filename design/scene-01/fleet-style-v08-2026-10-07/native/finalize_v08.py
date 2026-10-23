import bpy,json,time
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'fleet-illustrated-v08.blend'));s=bpy.context.scene
m=bpy.data.materials.new('V08 restrained pale exhaust');m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(.70,.75,.73,1);e.inputs[1].default_value=.75;t=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.30;l=m.node_tree.links;l.new(t.outputs[0],mix.inputs[1]);l.new(e.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs['Surface'])
for i in (1,4):
 root=bpy.data.objects[f'truck-{i}-tractor'];stack=bpy.data.objects[f'{i} exhaust stack'];tip=stack.location.z+stack.dimensions.z/2
 for j in range(3):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1);o=bpy.context.object;o.name=f'V08 {i} light exhaust {j}';o.parent=root;o.matrix_parent_inverse=Matrix.Identity(4);o.location=(stack.location.x-.07*j,stack.location.y,tip+.06+.19*j);o.scale=(.09+.035*j,.08+.025*j,.12+.035*j);o.data.materials.append(m)
  for p in o.data.polygons:p.use_smooth=True
roots=[o for o in s.objects if o.name.startswith('truck-')];fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');crypto.matte_id=', '.join(o.name for o in fleet if o.type in ('MESH','FONT') and not o.hide_render)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'fleet-illustrated-v08.blend'))
receipt=json.loads((O/'v08-native-receipt.json').read_text());receipt['shape_changes'].append('Restrained 3-lobe pale exhaust cue physically parented to original red/yellow exhaust tip; transparent material opacity30%, no black cloud.');(O/'v08-native-receipt.json').write_text(json.dumps(receipt,indent=2))
for f in (1,385,769):
 s.frame_set(f);s.render.filepath=str(O/f'fleet-v08-{f:04}.png');bpy.ops.render.render(write_still=True)
# Re-render isolated fronts with exact original hide flags preserved between captures.
flags={o.name:o.hide_render for o in s.objects};s.frame_set(769);cam=s.camera;s.render.resolution_x=900;s.render.resolution_y=900
for i in range(1,5):
 own=set([bpy.data.objects[f'truck-{i}-tractor'],bpy.data.objects[f'truck-{i}-trailer']]);
 for r in tuple(own):own.update(r.children_recursive)
 for o in s.objects:
  if o.type in ('MESH','FONT','CURVE'):o.hide_render=flags[o.name] or o not in own
 root=bpy.data.objects[f'truck-{i}-tractor'];center=root.matrix_world@Vector((.25,0,1.65));cam.location=root.matrix_world@Vector((11,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.5;s.render.filepath=str(O/f'front-{i}.png');bpy.ops.render.render(write_still=True)
print('FINAL V08 READY',flush=True)
