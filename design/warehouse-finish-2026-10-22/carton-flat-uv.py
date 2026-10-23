"""Opt-in material-only carton surface mapping. Run with runpy, call apply(texture_path).
No scene is loaded/saved/rendered automatically. Existing carton meshes only.
All transform/vertex coordinates are asserted unchanged. Existing tape/labels remain.
Texture must contain ordinary flat cardboard grain only (no baked perspective,
lighting, text, frame, or additional packages). Existing lighting remains authority.
"""
import bpy

def apply(texture_path):
    image=bpy.data.images.load(str(texture_path),check_existing=True)
    targets=[o for o in bpy.data.objects if o.type=='MESH' and ('carton' in o.name.lower())]
    records=[]
    for o in targets:
        vertices=[tuple(v.co) for v in o.data.vertices];matrix=o.matrix_world.copy()
        # Each original planar face receives local normalized coordinates using
        # its two axes perpendicular to the face normal. No UV projection operator,
        # object transforms, mesh subdivision, frame movement or text regeneration.
        uv=o.data.uv_layers.get('CartonFlatSurface') or o.data.uv_layers.new(name='CartonFlatSurface')
        for face in o.data.polygons:
            dominant=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=dominant]
            lows=[min(v[a] for v in vertices) for a in axes];spans=[max(v[a] for v in vertices)-lo for a,lo in zip(axes,lows)]
            for li in face.loop_indices:
                p=vertices[o.data.loops[li].vertex_index];uv.data[li].uv=[(p[a]-lo)/span if span else 0 for a,lo,span in zip(axes,lows,spans)]
        # Clone current material to retain source colour and roughness. Texture
        # modulates base colour mildly, avoiding a baked new perspective/shadow.
        for slot in o.material_slots:
            if not slot.material:continue
            m=slot.material.copy();slot.material=m;m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
            bs=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
            if bs is None:continue
            base=tuple(bs.inputs['Base Color'].default_value);tex=n.new('ShaderNodeTexImage');tex.image=image;tex.extension='REPEAT';uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map=uv.name;l.new(uvnode.outputs['UV'],tex.inputs['Vector'])
            mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.28;mix.inputs[1].default_value=base;l.new(tex.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
        assert vertices==[tuple(v.co) for v in o.data.vertices] and o.matrix_world==matrix
        records.append({'object':o.name,'vertex_count':len(vertices),'uv_layer':uv.name,'geometry_unchanged':True})
    return records
