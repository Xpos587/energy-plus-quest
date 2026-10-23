import bpy,pathlib,math
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'crew-cab-preview.blend'))
for role,y,offset in [('driver',-.20,.55),('passenger',.20,.64)]:
 im=bpy.data.images.load(str(P/('face-lookdev-'+role+'-texture.png')));im.pack()
 skin=bpy.data.materials['CREW_skin_highlight'];base=skin.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value[:]
 m=bpy.data.materials.new('CREW_'+role+'_projected_illustrated_face');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.82;bs.inputs['Specular IOR Level'].default_value=.15;l.new(bs.outputs[0],out.inputs['Surface'])
 tex=n.new('ShaderNodeTexImage');tex.image=im;tex.extension='CLIP'
 uv=n.new('ShaderNodeUVMap');uv.uv_map='ApprovedFaceProjection';l.new(uv.outputs[0],tex.inputs[0])
 geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-1,0,0);l.new(geo.outputs['Normal'],dot.inputs[0])
 gate=n.new('ShaderNodeMapRange');gate.clamp=True;gate.inputs['From Min'].default_value=.25;gate.inputs['From Max'].default_value=.75;l.new(dot.outputs['Value'],gate.inputs['Value'])
 mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';l.new(tex.outputs['Alpha'],mult.inputs[0]);l.new(gate.outputs['Result'],mult.inputs[1])
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=base;l.new(mult.outputs[0],mix.inputs[0]);l.new(tex.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
 # small emission preserves illustrated identity without flat replacement of volume
 bs.inputs['Emission Strength'].default_value=.08;l.new(mix.outputs[0],bs.inputs['Emission Color'])
 for o in list(bpy.data.collections['CREW'].objects):
  if not o.name.startswith('CREW_'+role+'_'):continue
  if any(s in o.name for s in ['_eye_','_iris_','_pupil_','_brow_','_upper_lid_','_upper_lip','_lower_lip','_nostril_']):o.hide_render=True;o.hide_viewport=True
  if any(s in o.name for s in ['_sculpted_head','_nose_bridge','_nose_tip']):
   if '_nose_' in o.name:
    o.scale.x*=.55;o.location.x+=.004
   uv=o.data.uv_layers.new(name='ApprovedFaceProjection')
   for face in o.data.polygons:
    for index in face.loop_indices:
     p=o.matrix_world@o.data.vertices[o.data.loops[index].vertex_index].co
     uv.data[index].uv=(-(p.y-y)/.118+offset,(p.z-.070)/.190)
   o.data.materials.clear();o.data.materials.append(m)
s=bpy.context.scene;s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.film_transparent=True
cam=s.camera;cam.location=(-3,0,.32);cam.rotation_euler=(Vector((-.80,0,.12))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.91
bpy.ops.wm.save_as_mainfile(filepath=str(P/'face-lookdev.blend'))
s.render.filepath=str(P/'face-lookdev-cab-front.png');bpy.ops.render.render(write_still=True)
cam.location=(-2.3,1.1,.42);cam.rotation_euler=(Vector((-.77,0,.10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.0
s.render.filepath=str(P/'face-lookdev-cab-three-quarter.png');bpy.ops.render.render(write_still=True)
