"""Fixed geometry + continuous illustrated diffuse shading; no frame generation."""
import bpy
import pathlib
import sys
from mathutils import Vector

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path(__file__).resolve().parent
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
source = pathlib.Path(args[0]) if args else ROOT / 'native/scania-native-shape-v4.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.82, 0.90, 1.0, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4

# Half diffuse, half constant pigment keeps the same painted colour in shadow.
# Broad real area lighting supplies volume without black silhouettes or outlines.
palette = {
    'Moderate sage green paint': (0.20, 0.44, 0.085),
    'Medium slate grille': (0.13, 0.22, 0.27),
    'Warm soft tire': (0.075, 0.12, 0.15),
    'Warm white trim': (0.70, 0.75, 0.76),
    'Seat textile muted blue': (0.16, 0.29, 0.39),
    'Warm headlamps': (0.89, 0.92, 0.84),
    'Background warm ivory': (0.52, 0.72, 0.85),
}
for name, colour in palette.items():
    material = bpy.data.materials.get(name)
    if material is None:
        continue
    material.use_nodes = True
    material.diffuse_color = (*colour, 1)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = (*colour, 1)
    diffuse.inputs['Roughness'].default_value = 0.85
    pigment = nodes.new('ShaderNodeEmission')
    pigment.inputs['Color'].default_value = (*colour, 1)
    pigment.inputs['Strength'].default_value = 0.85
    mix = nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = 0.52
    links.new(diffuse.outputs[0], mix.inputs[1])
    links.new(pigment.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs['Surface'])

for obj in bpy.data.objects:
    if obj.type == 'LIGHT' and obj.data.type == 'AREA':
        obj.data.energy *= 0.60
        obj.data.size = max(obj.data.size, 290)
        obj.data.color = (1.0, 0.97, 0.92)

scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
for name, dims in [
    ('shape-gate-front-three-quarter', (1400, 1050)),
    ('orthographic-front', (1100, 1100)),
    ('map-heading-0', (1000, 1000)),
    ('map-heading-120', (1000, 1000)),
    ('map-heading-240', (1000, 1000)),
]:
    camera = bpy.data.objects.get(name)
    if camera is None:
        continue
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = dims
    scene.render.filepath = str(OUT / (name + '-style.png'))
    bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'scania-fixed-illustrated.blend'))
