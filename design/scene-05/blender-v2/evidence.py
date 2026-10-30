"""Read the saved structural scene and export ID/depth evidence for both cameras.
blender -b STRUCTURE/lastmile.blend -t 8 -P evidence.py -- OUTDIR
IDs prove visible pixels, not a percentage of the whole object's surface.
"""
import json, math, sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

out = Path(sys.argv[sys.argv.index('--') + 1]); out.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.render.use_freestyle = False
scene.view_layers[0].use_freestyle = False
scene.eevee.taa_render_samples = 1
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
groups = ['abk', 'barge', 'helicopter', 'pipe-carrier', 'rover', 'robot', 'chums', 'r_arseniy', 'gift']
colors = [(1,0,0,1),(0,1,0,1),(0,0,1,1),(1,1,0,1),(1,0,1,1),(0,1,1,1),(1,.3,0,1),(.3,0,1,1),(.3,1,0,1)]
mat = bpy.data.materials.new('Evidence'); mat.use_nodes = True
nt = mat.node_tree; nt.nodes.clear()
output = nt.nodes.new('ShaderNodeOutputMaterial'); emission = nt.nodes.new('ShaderNodeEmission')
nt.links.new(emission.outputs[0], output.inputs[0])
info = nt.nodes.new('ShaderNodeObjectInfo'); nt.links.new(info.outputs['Color'], emission.inputs[0])
for o in scene.objects:
    if o.type in ('MESH', 'FONT'):
        g = o.get('group', '')
        o.color = colors[groups.index(g)] if g in groups else (0,0,0,1)
        o.data.materials.clear(); o.data.materials.append(mat)
scene.world.node_tree.nodes.get('Background').inputs[0].default_value = (0,0,0,1)
scene.world.node_tree.nodes.get('Background').inputs[1].default_value = 0
pivots = {'pipe-carrier':(-35,2,0), 'rover':(-30,-39,0), 'robot':(-27,-74,0), 'helicopter':(-30,64,0)}
report = {}
for fmt, size, degrees in [('wide',(1942,809),0),('tall',(948,1659),-50)]:
    scene.camera = bpy.data.objects[fmt]
    scene.render.resolution_x, scene.render.resolution_y = size
    for o in scene.objects:
        if o.get('group') in pivots:
            p = Vector(pivots[o['group']])
            o.matrix_world = Matrix.Translation(p) @ Matrix.Rotation(math.radians(degrees),4,'Z') @ Matrix.Translation(-p)
    nt.links.new(info.outputs['Color'], emission.inputs[0])
    scene.render.filepath = str(out / f'{fmt}-id.png'); bpy.ops.render.render(write_still=True)
    # Actual rendered visibility is validated by downstream evidence-check.py.
    camera_data = nt.nodes.new('ShaderNodeCameraData')
    mapping = nt.nodes.new('ShaderNodeMapRange')
    mapping.inputs['From Min'].default_value = 730
    mapping.inputs['From Max'].default_value = 1100
    nt.links.new(camera_data.outputs['View Z Depth'], mapping.inputs['Value'])
    nt.links.new(mapping.outputs[0], emission.inputs[0])
    scene.render.filepath = str(out / f'{fmt}-depth.png'); bpy.ops.render.render(write_still=True)
    report[fmt] = {'size':size,'camera':fmt,'azimuth':-25 if fmt=='wide' else -62,'elevation':40 if fmt=='wide' else 48}
(out / 'passes.json').write_text(json.dumps({'cameras':report,'ids':dict(zip(groups,colors))}, indent=2))
