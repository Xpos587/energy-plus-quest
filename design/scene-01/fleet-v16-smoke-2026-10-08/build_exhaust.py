import bpy, math, json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
for o in list(bpy.data.objects):
 if any(t in o.name for t in ('connected exhaust plume','light exhaust')):o.hide_render=True
# Capture the genuine stack upper cap in world space at each emission frame.
positions={}
for f in range(1,194):
 s.frame_set(f);bpy.context.view_layer.update()
 for i in (1,4):
  pipe=bpy.data.objects[f'{i} exhaust stack']
  corners=[pipe.matrix_world@Vector(v) for v in pipe.bound_box]
  top=max(v.z for v in corners);positions[i,f]=Vector((sum(v.x for v in corners)/8,sum(v.y for v in corners)/8,top+.018))
for i in (1,4):
 for f in range(-26,1):positions[i,f]=positions[i,1]+(positions[i,2]-positions[i,1])*(f-1)
coll=bpy.data.collections.new('V16 smoke worldspace exhaust puffs');s.collection.children.link(coll)
noise_origin=bpy.data.objects.new('V16 smoke truck noise coordinates',None);s.collection.objects.link(noise_origin)
for i in (1,4):
 for slot in range(13):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1)
  o=bpy.context.object;o.name=f'V16 smoke truck {i} exhaust puff {slot}'
  for c in list(o.users_collection):c.objects.unlink(o)
  coll.objects.link(o)
  mat=bpy.data.materials.new(o.name+' diffuse charcoal');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links
  out=n.new('ShaderNodeOutputMaterial');vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.40,.41,.42,1);l.new(vol.outputs['Volume'],out.inputs['Volume'])
  tex=n.new('ShaderNodeTexCoord');dist=n.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,.5);l.new(tex.outputs['Generated'],dist.inputs[0])
  ramp=n.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=.1;ramp.inputs['From Max'].default_value=.5;ramp.inputs['To Min'].default_value=1;ramp.inputs['To Max'].default_value=0;l.new(dist.outputs['Value'],ramp.inputs['Value'])
  # All parcels sample one continuous world-space noise field, so overlapping
  # meshes reveal shared broad turbulent lobes instead of repeating spheres.
  worldtex=n.new('ShaderNodeTexCoord');worldtex.object=noise_origin
  noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=1.15;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.6;l.new(worldtex.outputs['Object'],noise.inputs['Vector'])
  lobes=n.new('ShaderNodeMapRange');lobes.clamp=True;lobes.inputs['From Min'].default_value=.34;lobes.inputs['From Max'].default_value=.66;lobes.inputs['To Min'].default_value=0;lobes.inputs['To Max'].default_value=1.8;l.new(noise.outputs['Fac'],lobes.inputs['Value'])
  mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';l.new(ramp.outputs[0],mult.inputs[0]);l.new(lobes.outputs[0],mult.inputs[1])
  density=n.new('ShaderNodeMath');density.operation='MULTIPLY';l.new(mult.outputs[0],density.inputs[0]);l.new(density.outputs[0],vol.inputs['Density']);o.data.materials.append(mat)
  for f in range(1,193):
   age=(f-slot*2)%26;birth=f-age;u=age/26
   # Emission follows sampled stack; subsequent positions are world-space drift.
   origin=positions[i,birth];o.location=origin+Vector((0,0,5.0*math.sqrt(u)))
   radius=(.28+1.0*u)*(.93+.12*math.sin(slot*1.7))
   travel=positions[i,birth+1]-positions[i,birth]
   o.rotation_euler[2]=math.atan2(travel.y,travel.x)
   # Overlapping ellipsoids stretch along the actual emission-path tangent.
   o.scale=(radius*1.45,radius,radius*1.45)
   density.inputs[1].default_value=2.8*(1-u)**1.15
   noise.inputs['W'].default_value=f/24*.42;noise.inputs['W'].keyframe_insert('default_value',frame=f)
   o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f);o.keyframe_insert('scale',frame=f);density.inputs[1].keyframe_insert('default_value',frame=f)
s.frame_set(48);s.render.resolution_percentage=100;s.eevee.volumetric_tile_size='2';s.eevee.volumetric_samples=128;s.eevee.use_volume_custom_range=True;s.eevee.volumetric_start=100;s.eevee.volumetric_end=200
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v16-smoke.blend'))
(P/'exhaust-contract.json').write_text(json.dumps({'source':'../fleet-behavior-v16-2026-10-07/fleet-v16-motion.blend','vehicles':[1,4],'puffs_per_vehicle':13,'emission_every_frames':2,'lifetime_frames':26,'fps':24,'origin':'stack upper cap world-space bounding-box center','motion':'overlapping ellipsoids aligned to emission-path tangent, vertical buoyancy only and expansion at historical emission positions; no lateral drift; individually keyed density fades','frames':192,'camera':s.camera.name,'resolution':[s.render.resolution_x,s.render.resolution_y]},indent=2))
