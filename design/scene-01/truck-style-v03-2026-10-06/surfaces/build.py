import bpy, bmesh, pathlib
from mathutils import Vector
P=pathlib.Path(__file__).resolve().parent
SRC=P.parents[1]/'truck-native-quality-2026-10-05/image-to-3d'
bpy.ops.wm.open_mainfile(filepath=str(SRC/'green-tractor-detailed.blend'))
obj=bpy.data.objects['Mesh_0']; mesh=obj.data
# Keep original topology and UV detail. No smoothing of disconnected UV islands.
def pigment(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 d=n.new('ShaderNodeBsdfDiffuse');d.inputs['Color'].default_value=(*color,1);d.inputs['Roughness'].default_value=1
 e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1);e.inputs['Strength'].default_value=1
 mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.3;l.new(d.outputs[0],mix.inputs[1]);l.new(e.outputs[0],mix.inputs[2]);o=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],o.inputs['Surface'])
 mesh.materials.append(m);return len(mesh.materials)-1
green=pigment('Clean muted green paint',(.29,.49,.16))
steel=pigment('Clean cool grey tanks',(.40,.45,.49))
dark=pigment('Soft charcoal chassis',(.065,.084,.10))
image=bpy.data.images.get('Image_0');pixels=list(image.pixels);w,h=image.size;uv=mesh.uv_layers['UVMap'].data
for f in mesh.polygons:
 p=f.center
 samples=[]
 for li in f.loop_indices:
  u,v=uv[li].uv;x=min(w-1,max(0,int(u*w)));y=min(h-1,max(0,int(v*h)));i=(y*w+x)*4;samples.append(pixels[i:i+3])
 r,g,b=[sum(c[k] for c in samples)/len(samples) for k in range(3)]
 if g>r*1.35 and g>b*1.35 and g>.08:f.material_index=green
 # Compress baked texture contrast continuously, never triangle-wise thresholds.
for m in list(mesh.materials):
 if not m or not m.use_nodes:continue
 n=m.node_tree.nodes;l=m.node_tree.links
 tex=next((a for a in n if a.type=='TEX_IMAGE' and a.image==image),None)
 if not tex:continue
 for link in list(tex.outputs['Color'].links):
  if link.to_node.type=='MIX_RGB':
   dest=link.to_socket;l.remove(link)
   sat=n.new('ShaderNodeHueSaturation');sat.inputs['Saturation'].default_value=.45;l.new(tex.outputs['Color'],sat.inputs['Color'])
   mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(.55,.55,.55,1);l.new(sat.outputs[0],mul.inputs[1])
   add=n.new('ShaderNodeMixRGB');add.blend_type='ADD';add.inputs[0].default_value=1;add.inputs[2].default_value=(.055,.069,.080,1);l.new(mul.outputs[0],add.inputs[1]);l.new(add.outputs[0],dest)
# Open the actual glazing so volumetric people are inside, never painted on top.
bm=bmesh.new();bm.from_mesh(mesh);remove=[]
for f in bm.faces:
 p=f.calc_center_median()
 if f.normal.x<-.3 and abs(p.x-(.187338*p.z-.913884))<.024 and abs(p.y)<.39 and .017<p.z<.254:remove.append(f)
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(mesh);bm.free()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.film_transparent=True
s.view_settings.view_transform='Standard';s.view_settings.look='None'
# One broad key and modest fill keep shadows soft without bleaching the palette.
for o in list(bpy.data.objects):
 if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.86,.93,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.55
for loc,energy,size in [((-3,-2,5),90,5),((-2,3,2),35,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(P/'clean-cab.blend'))
cam=s.camera
for name,loc,target,scale in [('body',(-3,3,2.3),(0,0,0),2.6),('cab',(-3,1.1,.65),(-.7,0,.1),1.05)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
