import bpy,pathlib,math
from mathutils import Vector
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05');O=P/'native';bpy.ops.wm.open_mainfile(filepath=str(O/'scania-native-v4.blend'));s=bpy.context.scene
green=bpy.data.materials['Moderate sage green paint'];gray=bpy.data.materials['Medium slate grille']
# Restore original cab instead of degenerating relief facets. Plain rounded door skins cover the optional printed motif.
bpy.data.objects.remove(bpy.data.objects['SCANIA curved cab with embossed door panels'],do_unlink=True);bpy.ops.wm.stl_import(filepath=str(P/'sources/scania-r730-paolo/r730-1.stl'));o=bpy.context.object;o.name='SCANIA curved cab original shell'
for v in o.data.vertices:x,y,z=v.co;v.co=(x-55,50-y,z+42)
o.data.materials.append(green)
for p in o.data.polygons:p.use_smooth=True
for side in [-1,1]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(side*57,3,83));o=bpy.context.object;o.name='Smooth green door outer skin '+str(side);o.scale=(2,91,82);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(green);m=o.modifiers.new('Rounded pressed door panel','BEVEL');m.width=2;m.segments=4
# actual fascia louvres sit in front of green backing instead of behind it
bpy.data.objects['Joined front green fascia and radiator backing'].location.y+=9
# thin pale clear glazing; transparency dominates, leaving readable interior under diffuse light.
m=bpy.data.materials['Clear understated windshield glass'];n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');tr=n.new('ShaderNodeBsdfTransparent');tr.inputs[0].default_value=(.9,.97,1,1);diff=n.new('ShaderNodeBsdfDiffuse');diff.inputs[0].default_value=(.65,.8,.83,1);mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.07;m.node_tree.links.new(tr.outputs[0],mix.inputs[1]);m.node_tree.links.new(diff.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs[0])
s.cycles.samples=48;s.camera=bpy.data.objects['shape-gate-front-three-quarter'];s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(O/'shape-gate-v4-clean.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-native-shape-v4.blend'));bpy.ops.render.render(write_still=True)
for name in ['orthographic-front','orthographic-side','map-heading-0','map-heading-120','map-heading-240']:
 s.camera=bpy.data.objects[name];s.render.resolution_x=900 if name=='orthographic-front' else 1200 if name=='orthographic-side' else 640;s.render.resolution_y=900 if name=='orthographic-front' else 800 if name=='orthographic-side' else 640;s.render.filepath=str(O/(name+'-v4-clean.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-native-shape-v4.blend'))
