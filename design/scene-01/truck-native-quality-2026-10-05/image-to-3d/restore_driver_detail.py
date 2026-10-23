import bpy
import pathlib
import json
from mathutils import Vector

P = pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P / 'green-tractor-finished.blend'))
o = bpy.data.objects['Mesh_0']
uv = o.data.uv_layers.new(name='Permanent windshield projection')
for poly in o.data.polygons:
    for index in poly.loop_indices:
        p = o.data.vertices[o.data.loops[index].vertex_index].co
        u = (-p.y + .39) / .78
        v = (p.z - .012539) / .239284
        uv.data[index].uv = ((u-.5)*1.35+.5, v)
m = bpy.data.materials.new('Permanent high-detail two-driver windshield')
m.use_nodes = True
n, links = m.node_tree.nodes, m.node_tree.links
n.clear()
tex = n.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(str(P / 'windshield-high-detail.png'))
tex.image.pack()
tex.extension = 'CLIP'
map = n.new('ShaderNodeUVMap')
map.uv_map = uv.name
links.new(map.outputs[0], tex.inputs['Vector'])
mix = n.new('ShaderNodeMixRGB')
mix.inputs[1].default_value = (.10, .28, .42, 1)
links.new(tex.outputs['Alpha'], mix.inputs[0])
links.new(tex.outputs['Color'], mix.inputs[2])
pigment = n.new('ShaderNodeEmission')
links.new(mix.outputs[0], pigment.inputs['Color'])
pigment.inputs['Strength'].default_value = .85
out = n.new('ShaderNodeOutputMaterial')
links.new(pigment.outputs[0], out.inputs['Surface'])
o.data.materials.append(m)
idx = len(o.data.materials)-1
selected = []
for poly in o.data.polygons:
    p = sum((o.data.vertices[i].co for i in poly.vertices), Vector()) / len(poly.vertices)
    if poly.normal.x < -.3 and abs(p.x-(.187338*p.z-.913884)) < .021 and abs(p.y) < .384 and .025 < p.z < .248:
        poly.material_index = idx
        selected.append(poly.index)
assert len(selected) > 20, 'Windshield projection selected too few faces'
s = bpy.context.scene
c = s.camera
for name, position in [('detail-front', (-3.8,0,2.945)), ('detail-three-quarter',(-1.9,3.287,2.945))]:
    c.location = position
    c.rotation_euler = (-c.location).to_track_quat('-Z', 'Y').to_euler()
    s.render.filepath = str(P / (name+'.png'))
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P / 'green-tractor-detailed.blend'))
(P/'driver-projection-receipt.json').write_text(json.dumps({
    'projected_faces': len(selected),
    'windshield_only': True,
    'reference': '../cab-detail-pilot-2026-10-05/green-detail-reference.png',
    'method': 'permanent world-YZ to UV projection onto existing front windshield faces',
    'volumetric_crew': False,
}, indent=2))
