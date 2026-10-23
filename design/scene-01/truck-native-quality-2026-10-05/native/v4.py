import bpy,pathlib,json,math
from mathutils import Vector
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05');O=P/'native';bpy.ops.wm.open_mainfile(filepath=str(O/'scania-native-shape-gate.blend'));s=bpy.context.scene
for o in list(bpy.data.objects):
 if 'chassis' in o.name.lower():bpy.data.objects.remove(o,do_unlink=True)
def box(name,loc,scale,mat,bevel=1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);m=o.modifiers.new('Soft manufactured edges','BEVEL');m.width=bevel;m.segments=3;return o
green=bpy.data.materials['Moderate sage green paint'];gray=bpy.data.materials['Medium slate grille']
for side in [-1,1]:box('Controlled thin chassis longitudinal rail '+str(side),(side*22,109,30),(5,195,7),gray)
for y in [50,106,158,202]:box('Controlled frame cross member '+str(y),(0,y,30),(44,5,6),gray)
# Side door surface: remove print model's relief without replacing curved cab identity.
o=bpy.data.objects['SCANIA curved cab with embossed door panels']
for v in o.data.vertices:
 if abs(v.co.x)>52 and v.co.z<108:v.co.x=math.copysign(54.8,v.co.x)
# backing panel closes clear grille openings and mechanical seam; retain real sculpted grille on top.
box('Joined front green fascia and radiator backing',(0,-52,76),(96,6,59),green,2)
o=bpy.data.objects['SCANIA sculpted upper front grille'];o.location.y+=3
for side in [-1,1]:
 o=bpy.data.objects['Curved headlamp lens '+str(side)]
 for v in o.data.vertices:v.co.y=-59+(v.co.y+59)*.16
 o.location.y+=2
for o in bpy.data.objects:
 if 'rear mudguard' in o.name:
  for v in o.data.vertices:
   side=-1 if v.co.x<0 else 1;v.co.x=side*(39+(abs(v.co.x)-39)*.35)
# Physical interior occupant card sits within open cab, behind windshield; no viewport-aligned UI.
f=P/'interior/two-drivers-v1.png'
if f.exists():
 m=bpy.data.materials.new('Two drivers interior painted cloth and faces');m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');tr=n.new('ShaderNodeBsdfTransparent');em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=.8;tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(f));tex.image.pack();m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(tex.outputs['Alpha'],mix.inputs[0]);m.node_tree.links.new(tr.outputs[0],mix.inputs[1]);m.node_tree.links.new(em.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs[0])
 bpy.ops.mesh.primitive_plane_add(size=2,location=(0,-32,113),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Two actual seated drivers inside cab';o.scale=(43,28,1);o.data.materials.append(m)
# Thin clear glazing with understated pale blue tint, actual transparency.
m=bpy.data.materials.new('Clear understated windshield glass');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.71,.83,.85,1);bs.inputs['Transmission Weight'].default_value=1;bs.inputs['Roughness'].default_value=.1;bs.inputs['IOR'].default_value=1.1
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,-55,116),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Actual clear front glazing';o.scale=(46,26,1);o.data.materials.append(m)
s.cycles.samples=48;c=bpy.data.objects['shape-gate-front-three-quarter'];s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(O/'shape-gate-v4.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-native-v4.blend'));bpy.ops.render.render(write_still=True)
for name in ['orthographic-front','orthographic-side','map-heading-0','map-heading-120','map-heading-240']:
 s.camera=bpy.data.objects[name];s.render.resolution_x=900 if name=='orthographic-front' else 1200 if name=='orthographic-side' else 640;s.render.resolution_y=900 if name=='orthographic-front' else 800 if name=='orthographic-side' else 640;s.render.filepath=str(O/(name+'-v4.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-native-v4.blend'))
