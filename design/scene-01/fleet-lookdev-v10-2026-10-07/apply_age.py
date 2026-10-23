"""Local paint wear and restrained exhaust; source rigs and crew unchanged."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

P = Path(__file__).resolve().parent
SOURCE = P.parent / 'fleet-style-v08-2026-10-07/projected/clean/fleet-v09-clean-sill.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
s = bpy.context.scene
flags = {o.name: o.hide_render for o in s.objects}
roots = [bpy.data.objects[f'truck-{i}-{part}'] for i in range(1, 5) for part in ('tractor', 'trailer')]
fleet = set(roots)
for root in roots:
    fleet.update(root.children_recursive)
baseline = {}
for frame in (1, 385, 769):
    s.frame_set(frame)
    baseline[frame] = {o.name: list(sum((list(row) for row in o.matrix_world), [])) for o in roots}

for i in (1, 4):
    material = bpy.data.materials[f'V09 {i} painted cab front roof near side']
    n, l = material.node_tree.nodes, material.node_tree.links
    original = n['Emission.001'].inputs['Color'].links[0].from_socket
    pigment = n['Map Range'].outputs[0]
    faded = n.new('ShaderNodeHueSaturation')
    faded.name = 'V10 sun faded paint only'
    faded.inputs['Saturation'].default_value = .90 if i == 1 else .87
    faded.inputs['Value'].default_value = 1.0
    l.new(original, faded.inputs['Color'])
    fade_mix = n.new('ShaderNodeMixRGB')
    l.new(pigment, fade_mix.inputs[0])
    l.new(original, fade_mix.inputs[1])
    l.new(faded.outputs[0], fade_mix.inputs[2])

    coord = n.new('ShaderNodeTexCoord')
    scaled = n.new('ShaderNodeVectorMath'); scaled.operation = 'MULTIPLY'
    scaled.inputs[1].default_value = (2, 10, 45)
    l.new(coord.outputs['Object'], scaled.inputs[0])
    noise = n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 1
    noise.inputs['Detail'].default_value = 0
    l.new(scaled.outputs[0], noise.inputs['Vector'])
    ramp = n.new('ShaderNodeMapRange')
    ramp.inputs['From Min'].default_value = .60 if i == 1 else .54
    ramp.inputs['From Max'].default_value = .72 if i == 1 else .70
    ramp.inputs['To Max'].default_value = .62
    ramp.clamp = True
    l.new(noise.outputs['Fac'], ramp.inputs['Value'])
    xyz = n.new('ShaderNodeSeparateXYZ'); l.new(coord.outputs['Object'], xyz.inputs[0])
    below = n.new('ShaderNodeMath'); below.operation = 'LESS_THAN'; below.inputs[1].default_value = .14
    above = n.new('ShaderNodeMath'); above.operation = 'GREATER_THAN'; above.inputs[1].default_value = -.55
    l.new(xyz.outputs['Z'], below.inputs[0]); l.new(xyz.outputs['Z'], above.inputs[0])
    current = ramp.outputs[0]
    for mask in (below.outputs[0], above.outputs[0], pigment):
        product = n.new('ShaderNodeMath'); product.operation = 'MULTIPLY'
        l.new(current, product.inputs[0]); l.new(mask, product.inputs[1]); current = product.outputs[0]
    worn = n.new('ShaderNodeMixRGB'); worn.name = 'V10 local lower paint scuffs'
    l.new(current, worn.inputs[0]); l.new(fade_mix.outputs[0], worn.inputs[1])
    worn.inputs[2].default_value = (.35, .40, .41, 1)
    for node_name in ('Emission.001', 'Diffuse BSDF.001'):
        l.new(worn.outputs[0], n[node_name].inputs['Color'])

    for j in range(3):
        puff = bpy.data.objects[f'V08 {i} light exhaust {j}']
        puff.scale *= 1.8
        m = bpy.data.materials.new(f'V10 {i} soft connected exhaust {j}')
        m.use_nodes = True; nn = m.node_tree.nodes; ll = m.node_tree.links; nn.clear()
        transparent = nn.new('ShaderNodeBsdfTransparent')
        emit = nn.new('ShaderNodeEmission'); emit.inputs[0].default_value = (.50, .50, .48, 1)
        emit.inputs[1].default_value = .85
        weight = nn.new('ShaderNodeLayerWeight')
        opacity = nn.new('ShaderNodeMath'); opacity.operation = 'MULTIPLY'
        opacity.inputs[1].default_value = (.46, .38, .28)[j]
        inverse = nn.new('ShaderNodeMath'); inverse.operation = 'SUBTRACT'; inverse.inputs[0].default_value = 1
        ll.new(weight.outputs['Facing'], inverse.inputs[1]); ll.new(inverse.outputs[0], opacity.inputs[0])
        mix = nn.new('ShaderNodeMixShader')
        ll.new(opacity.outputs[0], mix.inputs[0]); ll.new(transparent.outputs[0], mix.inputs[1]); ll.new(emit.outputs[0], mix.inputs[2])
        out = nn.new('ShaderNodeOutputMaterial'); ll.new(mix.outputs[0], out.inputs['Surface'])
        puff.data.materials.clear(); puff.data.materials.append(m)

for o in s.objects:
    if o.type in ('MESH', 'FONT', 'CURVE') and o not in fleet:
        o.hide_render = True
for frame, expected in baseline.items():
    s.frame_set(frame)
    actual = {o.name: list(sum((list(row) for row in o.matrix_world), [])) for o in roots}
    assert actual == expected
s.frame_set(1)
s.render.film_transparent = True
s.render.use_compositing = False
s.render.resolution_x = 1920; s.render.resolution_y = 1334; s.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(P / 'fleet-v10-age.blend'))
for frame in (1, 385, 769):
    s.frame_set(frame); s.render.filepath = str(P / f'vehicles-{frame:04d}.png')
    bpy.ops.render.render(write_still=True)
s.frame_set(769); camera = s.camera
s.render.resolution_x = 1200; s.render.resolution_y = 1200
for i in (1, 4):
    tractor = bpy.data.objects[f'truck-{i}-tractor']; trailer = bpy.data.objects[f'truck-{i}-trailer']
    own = {tractor, trailer, *tractor.children_recursive, *trailer.children_recursive}
    for o in fleet:
        if o.type in ('MESH', 'FONT', 'CURVE'): o.hide_render = flags[o.name] or o not in own
    target = tractor.matrix_world @ Vector((.25, 0, 1.65))
    camera.location = tractor.matrix_world @ Vector((11, -8, 7))
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = 6.5
    s.render.filepath = str(P / f'front-{i}.png'); bpy.ops.render.render(write_still=True)
(P / 'age-receipt.json').write_text(json.dumps({
    'source': str(SOURCE), 'old_trucks_only': [1, 4],
    'changes': ['Object-fixed lower paint scuffs restricted to pigmented body; no crew or window edit',
                'Moderate faded paint, clean modern trucks untouched',
                'Existing old exhaust clouds enlarged 1.8 with softer rim and upward opacity decay'],
    'root_transforms_equal_at_frames': [1, 385, 769],
    'render_dimensions': [1920, 1334], 'pilot_only': True
}, indent=2))
print('AGE PILOTS COMPLETE')
