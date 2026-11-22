"""Render neutral and recipient beauty, local stylization, rotor film and matching evidence."""
import json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from surface import paint

out=Path(bpy.data.filepath).parent
sc=bpy.context.scene; r=sc.render; r.resolution_percentage=100; r.image_settings.file_format='PNG'; r.image_settings.color_mode='RGB'; r.image_settings.compression=25
r.use_border=False; r.film_transparent=False
sc.eevee.taa_render_samples=32
views=('wide','tall'); variants=('neutral','alva','khor','arseniy')
def view(name):
    c=bpy.data.objects[name]; sc.camera=c; r.resolution_x,r.resolution_y=c['W'],c['H']; bpy.context.view_layer.update(); return c

def render(name):
    r.filepath=str(out/(name+'.png')); bpy.ops.render.render(write_still=True)

paint()
if sys.argv[-1]=='preview':
    for name in views:
        view(name); r.resolution_percentage=50; sc.eevee.taa_render_samples=12; render(name+'-preview')
    sys.exit(0)

# Isolate the five long blades from the tail rotor's loose mesh parts.
ob=next(o for o in sc.objects if o.name.startswith('helicopter|#3D4651'))
bm=bmesh.new(); bm.from_mesh(ob.data); seen=set(); blades=[]
for v in bm.verts:
    if v in seen: continue
    todo=[v]; island=[]; seen.add(v)
    while todo:
        a=todo.pop(); island.append(a)
        for edge in a.link_edges:
            b=edge.other_vert(a)
            if b not in seen: seen.add(b); todo.append(b)
    if max((a.co-b.co).length for a in island for b in island)>6: blades.append(island)
assert len(blades)==5
verts=[v for part in blades for v in part]; hub=sum((ob.matrix_world@v.co for v in verts),Vector())/len(verts)
rot=bmesh.new(); remap={v:rot.verts.new(ob.matrix_world@v.co-hub) for v in verts}
for f in bm.faces:
    if all(v in remap for v in f.verts): rot.faces.new([remap[v] for v in f.verts])
me=bpy.data.meshes.new('main rotor'); rot.to_mesh(me); rot.free(); bmesh.ops.delete(bm,geom=verts,context='VERTS'); bm.to_mesh(ob.data); bm.free()
rotor=bpy.data.objects.new('rotor',me); sc.collection.objects.link(rotor); me.materials.append(ob.data.materials[0]); rotor.color=ob.color; rotor.location=hub; rotor.hide_render=True
for name in views:
    view(name)
    for var in variants:
        for o in sc.objects:
            if o.get('group') in variants: o.hide_render=o['group']!=var
        render(name+'-'+var)

# View-dependent rotor sheet; each frame is rendered from its own real orientation.
visible=[o for o in sc.objects if o.type in ('MESH','FONT','CURVE') and not o.hide_render]
for o in visible:o.hide_render=True
rotor.hide_render=False; r.film_transparent=True; r.image_settings.color_mode='RGBA'; sc.eevee.taa_render_samples=16
for name in views:
    c=view(name); W,H=c['W'],c['H']; v=world_to_camera_view(sc,c,hub); hx,hy=v.x*W,(1-v.y)*H
    # Crop in the exporter: scene space and pixel origin remain identical to the beauty plate.
    for i in range(12):
        rotor.rotation_euler.z=math.radians(i*6); render(f'{name}-blade-{i:02}')
for o in visible: o.hide_render=False
rotor.hide_render=True; r.film_transparent=False; r.image_settings.color_mode='RGB'
for o in sc.objects:
    if o.get('group') in variants: o.hide_render=True
# Raw emission carries 8-bit IDs; no edge antialiasing or tone mapping.
keys=('helicopter','rover','pipe_carrier','robot','barge','ice','harbor_water','industry','abk','chums','helipad','windsock','gift','reindeer','river','helideck','alva','khor','arseniy')
palette={k:((41+51*i)%250+1,(73+97*i)%250+1,(233+37*i)%250+1) for i,k in enumerate(keys)}
mat=bpy.data.materials.new('semantic IDs');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear(); em=nt.nodes.new('ShaderNodeEmission'); info=nt.nodes.new('ShaderNodeObjectInfo'); outmat=nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(info.outputs['Color'],em.inputs[0]); nt.links.new(em.outputs[0],outmat.inputs[0]);
for o in sc.objects:
    if o.type not in ('MESH','FONT','CURVE'): continue
    o.color=tuple(c/255 for c in palette.get(o.get('group'),(0,0,0)))+(1,);o.data.materials.clear();o.data.materials.append(mat)
    if o.get('group') in variants: o.hide_render=False
bg=sc.world.node_tree; bg.nodes.clear(); wbg=bg.nodes.new('ShaderNodeBackground'); wo=bg.nodes.new('ShaderNodeOutputWorld'); wbg.inputs[1].default_value=0;bg.links.new(wbg.outputs[0],wo.inputs[0]); sc.view_settings.view_transform='Raw'; sc.eevee.taa_render_samples=1; r.filter_size=.01; r.dither_intensity=0
for name in views: view(name); render(name+'-id')
cd=nt.nodes.new('ShaderNodeCameraData'); m=nt.nodes.new('ShaderNodeMapRange'); m.inputs['From Min'].default_value=55; m.inputs['From Max'].default_value=450; nt.links.new(cd.outputs['View Z Depth'],m.inputs['Value']);nt.links.new(m.outputs[0],em.inputs[0]);
for name in views: view(name); render(name+'-depth')
(out/'palette.json').write_text(json.dumps(palette,indent=2)+'\n'); print('R30_RENDER_COMPLETE',flush=True)
