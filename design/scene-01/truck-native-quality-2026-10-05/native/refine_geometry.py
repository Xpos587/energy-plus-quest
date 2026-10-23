import bpy,bmesh,pathlib,math
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/native');bpy.ops.wm.open_mainfile(filepath=str(P/'scania-native-shape-v4.blend'));s=bpy.context.scene
for o in list(bpy.data.objects):
 if o.name.startswith('Smooth '):bpy.data.objects.remove(o,do_unlink=True)
# Collapse source-only printed relief into original outer surface, then weld/dissolve degeneracies.
o=bpy.data.objects['SCANIA curved cab original shell'];bm=bmesh.new();bm.from_mesh(o.data)
for v in bm.verts:
 if abs(v.co.x)>52 and v.co.z<124:v.co.x=math.copysign(55.8,v.co.x)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.045)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.02)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
# retain cab paint around radiator, narrow gray-blue radiator backing directly under louvre apertures.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-50,77));o=bpy.context.object;o.name='Gray blue radiator inside upper grille';o.scale=(86,1,49);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials['Medium slate grille'])
bpy.data.objects['Two actual seated drivers inside cab'].location.z+=6
s.camera=bpy.data.objects['shape-gate-front-three-quarter'];s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(P/'shape-gate-v4-refined.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'scania-native-shape-v4-refined.blend'));bpy.ops.render.render(write_still=True)
