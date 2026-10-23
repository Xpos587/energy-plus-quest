import bpy,json,time
from pathlib import Path
P=Path('/home/michael/Github/energy-plus-quest');D=P/'design/warehouse-finish-2026-10-22';R=P/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'forklift-billboard-v1.blend'));s=bpy.context.scene;before={o.name:([list(v.co) for v in o.data.vertices],[list(x) for x in o.matrix_world]) for o in bpy.data.objects if o.type=='MESH'};cams={o.name:([list(x) for x in o.matrix_world],o.data.ortho_scale) for o in bpy.data.objects if o.type=='CAMERA'};changes=[]
def material(o):
 old=o.active_material;m=old.copy();m.name='forklift-combined-v2 '+o.name;o.active_material=m;return m,m.node_tree.nodes,m.node_tree.links,m.node_tree.nodes.get('Principled BSDF')
def ramp(nodes,stops):
 q=nodes.new('ShaderNodeValToRGB');q.color_ramp.interpolation='CONSTANT';q.color_ramp.elements.remove(q.color_ramp.elements[1]);first=q.color_ramp.elements[0];first.position=stops[0][0];first.color=(*stops[0][1],1)
 for pos,color in stops[1:]:q.color_ramp.elements.new(pos).color=(*color,1)
 return q
for o in list(bpy.data.objects):
 if o.type!='MESH':continue
 if o.name.startswith('Truck cargo side'):
  m,n,l,bs=material(o);tex=n.new('ShaderNodeTexCoord');xyz=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Generated'],xyz.inputs[0]);c=ramp(n,[(0,(.012,.10,.40)),(.23,(.91,.94,.94))]);l.new(xyz.outputs['Z'],c.inputs[0]);l.new(c.outputs[0],bs.inputs['Base Color']);changes.append(o.name+' lower blue band material')
 elif o.name.startswith('Truck wheel'):
  m,n,l,bs=material(o);tex=n.new('ShaderNodeTexCoord');xyz=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Generated'],xyz.inputs[0]);sub=[]
  for axis in ['X','Y']:
   a=n.new('ShaderNodeMath');a.operation='SUBTRACT';a.inputs[1].default_value=.5;l.new(xyz.outputs[axis],a.inputs[0]);b=n.new('ShaderNodeMath');b.operation='MULTIPLY';l.new(a.outputs[0],b.inputs[0]);l.new(a.outputs[0],b.inputs[1]);sub.append(b)
  add=n.new('ShaderNodeMath');add.operation='ADD';l.new(sub[0].outputs[0],add.inputs[0]);l.new(sub[1].outputs[0],add.inputs[1]);c=ramp(n,[(0,(.21,.29,.37)),(.025,(.11,.17,.23)),(.058,(.43,.54,.63)),(.083,(.014,.027,.048))]);l.new(add.outputs[0],c.inputs[0]);l.new(c.outputs[0],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.42;changes.append(o.name+' radial hub/rim shader')
 elif o.name in {'Finish truck windshield','Finish truck side window'}:
  m,n,l,bs=material(o);tex=n.new('ShaderNodeTexCoord');xyz=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Generated'],xyz.inputs[0]);c=ramp(n,[(0,(.04,.24,.48)),(.20,(.10,.43,.70)),(.73,(.43,.74,.90)),(.84,(.12,.45,.69))]);l.new(xyz.outputs['Z'],c.inputs[0]);l.new(c.outputs[0],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.26;changes.append(o.name+' clean glass reflections')
 elif o.name.startswith('Rack') and any(t in o.name.lower() for t in ['post','upright','beam']):
  m,n,l,bs=material(o);bs.inputs['Base Color'].default_value=(*((.95,.16,.008) if 'beam' in o.name.lower() else (.012,.10,.48)),1);changes.append(o.name+' saturated rack colour')
 elif 'carton' in o.name.lower():
  m,n,l,bs=material(o);base=tuple(bs.inputs['Base Color'].default_value);tex=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.8;noise.inputs['Detail'].default_value=0;noise.inputs['Roughness'].default_value=0;l.new(tex.outputs['Generated'],noise.inputs['Vector']);c=n.new('ShaderNodeValToRGB');c.color_ramp.elements[0].color=(.72,.69,.64,1);c.color_ramp.elements[1].color=(1,.97,.90,1);l.new(noise.outputs['Fac'],c.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.30;mix.inputs[1].default_value=base;l.new(c.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.86;changes.append(o.name+' broad soft paper colour only')
# Deterministic geometry gate prior to any preview render.
errors=[]
for name,(v,m) in before.items():
 o=bpy.data.objects[name]
 if v!=[list(x.co) for x in o.data.vertices] or m!=[list(x) for x in o.matrix_world]:errors.append(name)
for name,(m,scale) in cams.items():
 o=bpy.data.objects[name]
 if m!=[list(x) for x in o.matrix_world] or scale!=o.data.ortho_scale:errors.append(name)
assert not errors,errors
s.camera=bpy.data.objects['FullSourceOverscan'];s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=960;s.render.resolution_y=667;s.render.resolution_percentage=100;s.cycles.samples=16;s.cycles.seed=0;s.render.use_freestyle=False
bpy.ops.wm.save_as_mainfile(filepath=str(D/'forklift-combined-v2-no-outline.blend'));s.render.filepath=str(R/'forklift-combined-v2-no-outline-source.png');start=time.perf_counter();bpy.ops.render.render(write_still=True);plain=time.perf_counter()-start
# Thin blue physical-object lines only. Sprite cards excluded so no quad frame.
collection=bpy.data.collections.new('forklift-combined-v2 line candidates');s.collection.children.link(collection)
for o in bpy.data.objects:
 if o.type=='MESH' and o.visible_camera and (o.name.startswith(('Rack','Truck','Finish truck')) or 'carton' in o.name.lower()):collection.objects.link(o)
s.render.use_freestyle=True;layer=s.view_layers[0];fs=layer.freestyle_settings;lines=fs.linesets[0] if len(fs.linesets) else fs.linesets.new('Thin blue physical contours');lines.select_by_collection=True;lines.collection=collection;lines.select_silhouette=True;lines.select_border=True;lines.select_crease=False;lines.select_edge_mark=False;style=lines.linestyle;style.color=(.025,.09,.19);style.alpha=.50;style.thickness=.65
s.render.filepath=str(R/'forklift-combined-v2-thin-outline-source.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'forklift-combined-v2-thin-outline.blend'));start=time.perf_counter();bpy.ops.render.render(write_still=True);outlined=time.perf_counter()-start
(R/'forklift-combined-v2-render-receipt.json').write_text(json.dumps({'status':'two small local style comparison previews, no promotion','base_scene':'forklift-billboard-v1.blend','render':[960,667],'samples':16,'seed':0,'measured_render_seconds':{'without_outline':plain,'thin_outline':outlined},'timer':'time.perf_counter around bpy.ops.render.render(write_still=True)','all_existing_meshes_checked':len(before),'all_existing_cameras_checked':len(cams),'coordinate_or_transform_changes':errors,'native_sprite_modified':False,'objects_added':False,'material_changes':changes,'outline':{'type':'Freestyle silhouette/border','width_px':.65,'alpha':.5,'colour':[.025,.09,.19],'sprite_cards_excluded':True},'production_changed':False},indent=2));print('V2_TIMES',plain,outlined)
