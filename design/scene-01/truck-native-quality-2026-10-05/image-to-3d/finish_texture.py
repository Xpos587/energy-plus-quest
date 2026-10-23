import bpy
import pathlib
from mathutils import Vector

P = pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P / 'green-tractor-textured.blend'))
s = bpy.context.scene
for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    nodes, links = m.node_tree.nodes, m.node_tree.links
    texture = next((n for n in nodes if n.type == 'TEX_IMAGE'), None)
    if texture is None:
        continue
    image = texture.image
    nodes.clear()
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    rgb = nodes.new('ShaderNodeSeparateColor')
    rgb.mode = 'RGB'
    links.new(tex.outputs['Color'], rgb.inputs['Color'])
    def math_node(op, a, b):
        n = nodes.new('ShaderNodeMath')
        n.operation = op
        if isinstance(a, (int, float)):
            n.inputs[0].default_value = a
        else:
            links.new(a, n.inputs[0])
        if isinstance(b, (int, float)):
            n.inputs[1].default_value = b
        else:
            links.new(b, n.inputs[1])
        return n.outputs[0]
    green_r = math_node('SUBTRACT', rgb.outputs['Green'], math_node('MULTIPLY', rgb.outputs['Red'], 1.5))
    green_b = math_node('SUBTRACT', rgb.outputs['Green'], math_node('MULTIPLY', rgb.outputs['Blue'], 1.5))
    is_green = math_node('MULTIPLY', math_node('GREATER_THAN', green_r, .08), math_node('GREATER_THAN', green_b, .08))
    lift = nodes.new('ShaderNodeMixRGB')
    lift.blend_type = 'ADD'
    lift.inputs[0].default_value = 1
    lift.inputs[2].default_value = (.016, .022, .026, 1)
    links.new(tex.outputs['Color'], lift.inputs[1])
    paint = nodes.new('ShaderNodeMixRGB')
    links.new(is_green, paint.inputs[0])
    links.new(lift.outputs[0], paint.inputs[1])
    paint.inputs[2].default_value = (.26, .49, .13, 1)
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Roughness'].default_value = 1
    links.new(paint.outputs[0], diffuse.inputs['Color'])
    pigment = nodes.new('ShaderNodeEmission')
    pigment.inputs['Strength'].default_value = 1
    links.new(paint.outputs[0], pigment.inputs['Color'])
    mix = nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = .24
    links.new(diffuse.outputs[0], mix.inputs[1])
    links.new(pigment.outputs[0], mix.inputs[2])
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(mix.outputs[0], out.inputs['Surface'])

s.world.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1)
s.world.node_tree.nodes['Background'].inputs[1].default_value = .8
bpy.ops.object.light_add(type='AREA', location=(-2.5, -3, 5))
lamp = bpy.context.object
lamp.data.energy = 110
lamp.data.size = 4
lamp.rotation_euler = (-lamp.location).to_track_quat('-Z', 'Y').to_euler()
s.cycles.samples = 48
camera = bpy.data.objects['Fixed map test camera']
extent = 1.9
for angle, vector in [(60, (1, 1.73, 1.55)), (120, (-1, 1.73, 1.55)), (300, (1, -1.73, 1.55))]:
    camera.location = Vector(vector) * extent
    camera.rotation_euler = (-camera.location).to_track_quat('-Z', 'Y').to_euler()
    s.render.filepath = str(P / ('finished-%03d.png' % angle))
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P / 'green-tractor-finished.blend'))
