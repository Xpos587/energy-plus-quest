import bpy, json, math
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT / 'maz_500-original.glb'))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
points = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
lo = Vector([min(p[a] for p in points) for a in range(3)])
hi = Vector([max(p[a] for p in points) for a in range(3)])
center = (lo + hi) / 2
report = {'bounds': [list(lo), list(hi)], 'objects': []}
for o in meshes:
    o.data.calc_loop_triangles()
    report['objects'].append({'name': o.name, 'vertices': len(o.data.vertices), 'triangles': len(o.data.loop_triangles), 'materials': [m.name if m else None for m in o.data.materials], 'dimensions': list(o.dimensions), 'matrix_world': [list(row) for row in o.matrix_world]})
report['materials'] = [{'name': m.name, 'diffuse_color': list(m.diffuse_color), 'images': [n.image.name for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]} for m in bpy.data.materials if m.use_nodes]
(OUT / 'asset-inspection.json').write_text(json.dumps(report, indent=2))
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.studiolight_rotate_z = math.radians(25)
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.background_type = 'WORLD'
scene.world = bpy.data.worlds.new('Study world')
scene.world.color = (0.65, 0.65, 0.65)
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
camdata = bpy.data.cameras.new('Study camera')
cam = bpy.data.objects.new('Study camera', camdata)
scene.collection.objects.link(cam)
scene.camera = cam
camdata.type = 'ORTHO'
span = max(hi-lo)
camdata.ortho_scale = span * 1.35
for name, vec in [('q1', (1,-1,0.7)), ('q2', (-1,-1,0.7)), ('q3',(1,1,0.7)), ('q4',(-1,1,0.7)), ('top',(0,0,1))]:
    cam.location = center + Vector(vec).normalized() * span * 3
    cam.rotation_euler = (center - cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath = str(OUT / f'maz500-{name}.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'maz500-isolated-study.blend'))
