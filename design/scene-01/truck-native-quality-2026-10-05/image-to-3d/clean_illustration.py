import bpy
import pathlib
from mathutils import Vector

P = pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P / 'green-tractor-textured.blend'))
s = bpy.context.scene
o = bpy.data.objects['Mesh_0']
import bmesh
bm = bmesh.new()
bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00001)
bm.to_mesh(o.data)
bm.free()
for poly in o.data.polygons:
    poly.use_smooth = True
o.data.normals_split_custom_set([(0, 0, 0)] * len(o.data.loops))
smooth = o.modifiers.new('Remove reconstruction ripples', 'SMOOTH')
smooth.factor = .35
smooth.iterations = 4

for m in o.data.materials:
    nodes, links = m.node_tree.nodes, m.node_tree.links
    image = next(n.image for n in nodes if n.type == 'TEX_IMAGE')
    nodes.clear()
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = image
    hsv = nodes.new('ShaderNodeSeparateColor')
    hsv.mode = 'HSV'
    links.new(tex.outputs[0], hsv.inputs[0])
    def math(op, a, b):
        n = nodes.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate([a, b]):
            if isinstance(v, (float, int)):
                n.inputs[i].default_value = v
            else:
                links.new(v, n.inputs[i])
        return n.outputs[0]
    def recolour(previous, mask, colour):
        n = nodes.new('ShaderNodeMixRGB')
        links.new(mask, n.inputs[0])
        links.new(previous, n.inputs[1])
        n.inputs[2].default_value = (*colour, 1)
        return n.outputs[0]
    hue, saturation, value = [hsv.outputs[k] for k in range(3)]
    green = math('MULTIPLY', math('GREATER_THAN', hue, .19), math('LESS_THAN', hue, .42))
    green = math('MULTIPLY', green, math('GREATER_THAN', saturation, .3))
    neutral = math('LESS_THAN', saturation, .26)
    purple = math('MULTIPLY', math('GREATER_THAN', hue, .68), math('LESS_THAN', hue, .94))
    neutral = math('MAXIMUM', neutral, purple)
    dark = math('MULTIPLY', neutral, math('LESS_THAN', value, .36))
    bright = math('MULTIPLY', neutral, math('GREATER_THAN', value, .36))
    colour = recolour(tex.outputs[0], green, (.27, .51, .135))
    colour = recolour(colour, dark, (.095, .15, .19))
    colour = recolour(colour, bright, (.71, .74, .72))
    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Roughness'].default_value = 1
    links.new(colour, diffuse.inputs['Color'])
    pigment = nodes.new('ShaderNodeEmission')
    links.new(colour, pigment.inputs['Color'])
    mix = nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = .18
    links.new(diffuse.outputs[0], mix.inputs[1])
    links.new(pigment.outputs[0], mix.inputs[2])
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(mix.outputs[0], out.inputs['Surface'])
s.world.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1)
s.world.node_tree.nodes['Background'].inputs[1].default_value = .9
bpy.ops.object.light_add(type='AREA', location=(-2.5, -3, 5))
lamp = bpy.context.object
lamp.data.energy = 100
lamp.data.size = 5
lamp.rotation_euler = (-lamp.location).to_track_quat('-Z', 'Y').to_euler()
s.cycles.samples = 48
camera = bpy.data.objects['Fixed map test camera']
for angle, vec in [(120, (-1, 1.73, 1.55)), (180, (-2, 0, 1.55)), (300, (1, -1.73, 1.55))]:
    camera.location = Vector(vec) * 1.9
    camera.rotation_euler = (-camera.location).to_track_quat('-Z', 'Y').to_euler()
    s.render.filepath = str(P / ('clean-%03d.png' % angle))
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P / 'green-tractor-clean.blend'))
