import bpy,math,time,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(769);root=bpy.data.objects['truck-3-tractor']
def lin(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def mat(name,srgb):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.35,-.4,.82);l.new(geo.outputs['Normal'],dot.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=-.8;r.color_ramp.elements[0].color=tuple(lin(x*.78) for x in srgb)+(1,);r.color_ramp.elements[1].position=.8;r.color_ramp.elements[1].color=tuple(lin(min(x*1.1,1)) for x in srgb)+(1,);l.new(dot.outputs['Value'],r.inputs[0]);l.new(r.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0]);return m
rubber=mat('UV v2 soft blue-gray rubber',(.24,.29,.32));silver=mat('UV v2 brushed wheel',(.59,.65,.68));dark=mat('UV v2 rim recess',(.33,.40,.44))
for o in root.children:
    if o.name.startswith('UV PILOT front'):
        o.location.x=.20;o.location.z=.46
        o.data.materials.clear();o.data.materials.append(rubber if 'tyre' in o.name else silver)
        o.scale.x=1.13;o.scale.y=1.13
    if o.name.startswith('UV PILOT mirror'):
        o.data.materials.clear();o.data.materials.append(rubber)
for sign in (-1,1):
    for i in range(8):
        a=2*math.pi*i/8
        bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.029,depth=.009)
        o=bpy.context.object;o.name=f'UV v2 wheel bolt {sign} {i}';o.parent=root;o.location=(.20+.17*math.cos(a),sign*.899,.46+.17*math.sin(a));o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(dark)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.09,depth=.014)
    o=bpy.context.object;o.name=f'UV v2 hub cap {sign}';o.parent=root;o.location=(.20,sign*.902,.46);o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(dark)
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2')
objs=[]
for rt in [o for o in s.objects if o.name.startswith('truck-')]:objs.extend(o for o in rt.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
crypto.matte_id=', '.join(o.name for o in objs)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-uv-candidate-v2.blend'))
times={}
def render(name):
    s.render.filepath=str(O/name);t=time.monotonic();bpy.ops.render.render(write_still=True);times[name]=round(time.monotonic()-t,3)
render('map-vehicles-final.png')
trailer=bpy.data.objects['truck-3-trailer'];keep={root,trailer,*root.children_recursive,*trailer.children_recursive}
for o in s.objects:
    if o.type in ('MESH','FONT','CURVE') and o not in keep:o.hide_render=True
cam=s.camera;target=root.matrix_world@Vector((.1,0,1.65));pos=root.matrix_world@Vector((7,-4.2,5.4));cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=4.8;s.render.resolution_x=1200;s.render.resolution_y=1200
tree=s.compositing_node_group;output=next(n for n in tree.nodes if n.type=='GROUP_OUTPUT');rl=next(n for n in tree.nodes if n.type=='R_LAYERS');tree.links.new(rl.outputs['Image'],output.inputs['Image']);render('green-detail-final.png')
r=json.loads((O/'receipt-v1.json').read_text());r.update({'candidate':'green-uv-candidate-v2.blend','render_seconds_by_image':times,'wheel_finish':'soft normal shading and modeled wheel bolts; moved to painted arch centre','style_accepted':False});(O/'receipt-final.json').write_text(json.dumps(r,indent=2))
