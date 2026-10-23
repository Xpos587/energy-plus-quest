import bpy,pathlib
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05');O=P/'native';bpy.ops.wm.open_mainfile(filepath=str(O/'scania-native-shape-v4-refined.blend'));s=bpy.context.scene
bpy.data.objects.remove(bpy.data.objects['SCANIA curved cab original shell'],do_unlink=True);bpy.ops.wm.stl_import(filepath=str(P/'sources/scania-r730-paolo/r730-1.stl'));o=bpy.context.object;o.name='SCANIA curved cab original shell'
for v in o.data.vertices:x,y,z=v.co;v.co=(x-55,50-y,z+42)
o.data.materials.append(bpy.data.materials['Moderate sage green paint'])
for p in o.data.polygons:p.use_smooth=True
# Zero thickness side surface skins sit within0.05mm of the source's maximal outside surface.
for x,side in [(-54.45,-1),(56.04,1)]:
 pts=[(x,-45,42),(x,48,42),(x,48,124),(x,-9,124),(x,-9,94),(x,-45,94)]
 faces=[(0,1,4,5),(1,2,3,4)]
 if side<0:faces=[tuple(reversed(f)) for f in faces]
 me=bpy.data.meshes.new('Flush pressed side skin mesh');me.from_pydata(pts,[],faces);me.update();o=bpy.data.objects.new('Flush source cab door skin '+str(side),me);bpy.context.collection.objects.link(o);o.data.materials.append(bpy.data.materials['Moderate sage green paint'])
s.camera=bpy.data.objects['shape-gate-front-three-quarter'];s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(O/'shape-gate-v4-flush.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-native-shape-v4-flush.blend'));bpy.ops.render.render(write_still=True)
