"""One green UV-cab experiment; no production changes and no animation render."""
import bpy, math, json, time
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
s=bpy.context.scene
s.frame_set(769)
root=bpy.data.objects['truck-3-tractor']
old=bpy.data.objects['PILOT 3 reconstructed crew-cab']
old.hide_render=True
img=bpy.data.images.load(str(O/'green-cab-uv-atlas.png'),check_existing=True)
img.pack()
m=bpy.data.materials.new('UV PILOT green cab painted atlas');m.use_nodes=True
n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');tex=n.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Linear';tex.extension='EXTEND'
geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.18,-.25,.95);l.new(geo.outputs['Normal'],dot.inputs[0])
gain=n.new('ShaderNodeMath');gain.operation='MULTIPLY_ADD';gain.inputs[1].default_value=.08;gain.inputs[2].default_value=.94;l.new(dot.outputs['Value'],gain.inputs[0])
mul=n.new('ShaderNodeVectorMath');mul.operation='SCALE';l.new(tex.outputs['Color'],mul.inputs[0]);l.new(gain.outputs[0],mul.inputs['Scale']);l.new(mul.outputs[0],em.inputs['Color']);l.new(em.outputs[0],out.inputs[0])
verts=[];faces=[];uvs=[]
def face(points,coords):
    start=len(verts);verts.extend(points);faces.append(tuple(range(start,start+len(points))));uvs.append(coords)
def atlas_uv(u,v,quadrant):
    x,y={'front':(0,.5),'left':(.5,.5),'roof':(0,0),'right':(.5,0)}[quadrant]
    # Tiny inset prevents interpolation across unrelated surfaces.
    return (x+.003+u*.494,y+.003+v*.494)
# Cab front broken into sloping surfaces. UVs share one continuous front elevation.
levels=[(.55,1.04,.78),(1.65,1.06,.82),(2.62,.73,.79),(3.08,.48,.75)]
rear=-.85
for (z0,x0,w0),(z1,x1,w1) in zip(levels,levels[1:]):
    face([(x0,-w0,z0),(x0,w0,z0),(x1,w1,z1),(x1,-w1,z1)],
         [atlas_uv(u,v,'front') for u,v in [(1,(z0-.55)/2.53),(0,(z0-.55)/2.53),(0,(z1-.55)/2.53),(1,(z1-.55)/2.53)]])
    for sign,q in ((-1,'left'),(1,'right')):
        # Left texture has nose at image left; right texture at image right.
        side=[(rear,sign*w0,z0),(x0,sign*w0,z0),(x1,sign*w1,z1),(rear,sign*w1,z1)]
        coords=[]
        for x,y,z in side:
            u=(x-rear)/(1.06-rear)
            if q=='left':u=1-u
            coords.append(atlas_uv(u,(z-.55)/2.53,q))
        if sign==-1:side.reverse();coords.reverse()
        face(side,coords)
z,x,w=levels[-1]
face([(rear,-w,z),(x,-w,z),(x,w,z),(rear,w,z)],[atlas_uv(u,v,'roof') for u,v in [(0,0),(1,0),(1,1),(0,1)]])
face([(rear,.75,3.08),(rear,-.75,3.08),(rear,-.78,.55),(rear,.78,.55)],[atlas_uv(u,v,'roof') for u,v in [(0,1),(1,1),(1,0),(0,0)]])
mesh=bpy.data.meshes.new('UV cab continuous surface');mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='CabAtlas')
for poly,coords in zip(mesh.polygons,uvs):
    for loop,coord in zip(poly.loop_indices,coords):uv.data[loop].uv=coord
cab=bpy.data.objects.new('UV PILOT green cab',mesh);s.collection.objects.link(cab);cab.parent=root;cab.data.materials.append(m)
bev=cab.modifiers.new('soft cabin corners','BEVEL');bev.width=.035;bev.segments=3
def flat_mat(name,color):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;nn=mat.node_tree.nodes;ll=mat.node_tree.links;nn.clear();a=nn.new('ShaderNodeEmission');a.inputs[0].default_value=color+(1,);b=nn.new('ShaderNodeOutputMaterial');ll.new(a.outputs[0],b.inputs[0]);return mat
rubber=flat_mat('UV PILOT slate rubber',(.07,.105,.13));metal=flat_mat('UV PILOT wheel soft silver',(.42,.50,.54));green=flat_mat('UV PILOT mirror green',(.36,.64,.18))
for sign in (-1,1):
    for radius,depth,material,label in ((.405,.26,rubber,'tyre'),(.24,.275,metal,'hub')):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth)
        obj=bpy.context.object;obj.name=f'UV PILOT front {sign} {label}';obj.parent=root;obj.location=(.47,sign*.75,.43);obj.rotation_euler=(math.pi/2,0,0);obj.data.materials.append(material)
        b=obj.modifiers.new('rounded rim','BEVEL');b.width=.025;b.segments=3
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj=bpy.context.object;obj.name=f'UV PILOT mirror {sign}';obj.parent=root;obj.location=(.85,sign*.94,2.03);obj.scale=(.18,.14,.47);obj.data.materials.append(rubber)
    b=obj.modifiers.new('soft mirror edge','BEVEL');b.width=.12;b.segments=4
# Use existing full-city occlusion pass. Other trucks and routes are untouched.
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2')
objs=[]
for rt in [o for o in s.objects if o.name.startswith('truck-')]:
    objs.extend(o for o in rt.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
crypto.matte_id=', '.join(o.name for o in objs)
s.render.resolution_x=3840;s.render.resolution_y=2667;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.render.image_settings.color_mode='RGBA';s.render.use_freestyle=False
s.frame_set(769);bpy.ops.wm.save_as_mainfile(filepath=str(O/'green-uv-candidate.blend'))
s.render.filepath=str(O/'map-vehicles-0769.png');t=time.monotonic();bpy.ops.render.render(write_still=True);elapsed=time.monotonic()-t
from bpy_extras.object_utils import world_to_camera_view
points=[world_to_camera_view(s,s.camera,root.matrix_world@v.co) for v in cab.data.vertices]
bounds=[min(p.x for p in points)*3840,(1-max(p.y for p in points))*2667,max(p.x for p in points)*3840,(1-min(p.y for p in points))*2667]
r={'candidate_only':True,'style_accepted':False,'source':'../painted-layer-2026-10-05/painted-vehicles-driver-fixed-optimized.blend','frame':769,'resolution':[3840,2667],'render_seconds':round(elapsed,3),'texture_resolution':list(img.size),'texture':'green-cab-uv-atlas.png','mapping':'separate front, side and roof UV quadrants; no camera projection','green_cab_bounds_pixels':bounds,'routes_and_other_trucks':'unchanged','drivers':'painted two-driver front glass; count needs visual inspection','limitations':['New cabin is a bounded look-development prototype, not a finished truck model.','Interior faces are baked into glass paint, not independent 3D characters.','Contact-shadow pass and all-angle silhouette checks remain pending.','No animation rendered and no runtime assets changed.']}
(O/'receipt.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
