"""Clean native cab shell candidate. Existing rig/chassis/trailers stay untouched."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;s=bpy.context.scene
roots=[o for o in s.objects if o.name.startswith('truck-')]
def poses():
 r={}
 for f in (1,385,769,1152):
  s.frame_set(f);r[str(f)]={o.name:[list(row) for row in o.matrix_world] for o in roots}
 return r
before=poses();cam_record=[list(r) for r in s.camera.matrix_world]
def material(name,color):
 m=bpy.data.materials.new('STYLE '+name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');l.new(em.outputs[0],out.inputs[0]);geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.18,-.32,.92);l.new(geo.outputs['Normal'],dot.inputs[0]);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=-.2;ramp.color_ramp.elements[0].color=tuple(x*.68 for x in color)+(1,);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=tuple(color)+(1,);l.new(dot.outputs['Value'],ramp.inputs[0]);l.new(ramp.outputs[0],em.inputs[0]);return m
metal=material('slate hardware',(.20,.28,.31));glass=material('soft blue glass',(.25,.53,.66));light=material('headlights',(.97,.91,.69));rubber=material('tyres',(.055,.085,.10));skin=material('driver skin',(.82,.52,.33));shirt=material('blue uniform',(.07,.31,.56));trim=material('window trim',(.11,.22,.28));wear=material('aged panel contrast',(.48,.36,.23))
new=[]
def mesh(name,verts,faces,root,mat,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.parent=root;o.data.materials.append(mat)
 if bevel:
  b=o.modifiers.new('soft native edges','BEVEL');b.width=bevel;b.segments=3;b.limit_method='ANGLE'
 new.append(o);return o
def box(name,loc,dims,root,mat,bevel=.035):
 x,y,z=dims;v=[(loc[0]+a*x/2,loc[1]+b*y/2,loc[2]+c*z/2) for a,b,c in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
 return mesh(name,v,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],root,mat,bevel)
def sphere(name,loc,scale,root,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=(0,0,0));o=bpy.context.object;o.name=name;o.parent=root;o.location=loc;o.scale=scale;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 new.append(o);return o
records=[]
for i in range(1,5):
 root=bpy.data.objects[f'truck-{i}-tractor'];color={1:(.75,.15,.10),2:(.055,.36,.82),3:(.14,.56,.30),4:(.88,.60,.15)}[i];paint=material(f'{i} enamel',color);accent=material(f'{i} panel accent',tuple(x*.83 for x in color));h={1:2.86,2:3.18,3:3.26,4:2.65}[i];window_top=h-.52
 hidden=[];restored=[]
 for o in root.children_recursive:
  if not o.hide_render and o.type in ('MESH','FONT') and not any(t in o.name for t in ('fifth wheel','archived chassis','support deck')):o.hide_render=True;hidden.append(o.name)
  if any(t in o.name for t in ('seated tire','recessed hub','hub center')) and o.location.x>0:
   o.hide_render=False;restored.append(o.name)
   if 'tire' in o.name:
    for slot in o.material_slots:slot.link='OBJECT';slot.material=rubber
 # Cross-sections: wider lower bumper, angled windshield, rounded high sleeper roof.
 sections=[(.73,1.42),(1.52,1.48),(window_top,1.04),(h,.70)]
 verts=[]
 for z,x in sections:verts.extend([(-1.03,-.96,z),(-1.03,.96,z),(x,.96,z),(x,-.96,z)])
 faces=[(0,3,2,1),(12,13,14,15)]
 for k in range(3):
  for j in range(4):faces.append((k*4+j,k*4+(j+1)%4,(k+1)*4+(j+1)%4,(k+1)*4+j))
 mesh(f'STYLE {i} curved sleeper shell',verts,faces,root,paint,.12 if i in (2,3) else .07)
 # Windshield lies over the sloped shell, deliberately large enough at desktop angle.
 z0=1.64;z1=window_top-.08
 def frontx(z):return 1.48-(z-1.52)*(.44/(window_top-1.52))+.024
 x0=frontx(z0);x1=frontx(z1)
 mesh(f'STYLE {i} windshield',[(x0,-.79,z0),(x0,.79,z0),(x1,.79,z1),(x1,-.79,z1)],[(0,1,2,3)],root,glass)
 box(f'STYLE {i} visor',(1.06,0,window_top+.025),(.22,1.89,.13),root,trim,.05)
 box(f'STYLE {i} bumper',(1.47,0,.85),(.22,1.94,.22),root,metal,.06)
 box(f'STYLE {i} radiator',(1.496,0,1.21),(.034,1.18,.39),root,trim,.035)
 for z in (1.09,1.22,1.35):box(f'STYLE {i} grille bar {z}',(1.52,0,z),(.045,1.04,.045),root,metal,.015)
 for y in (-.72,.72):
  box(f'STYLE {i} headlamp {y}',(1.535,y,1.13),(.055,.27,.16),root,light,.04)
  box(f'STYLE {i} mirror {y}',(.92,y*1.55,2.13),(.16,.13,.36),root,metal,.06)
  box(f'STYLE {i} mirrorarm {y}',(.92,y*1.40,2.04),(.065,.28,.055),root,metal,.018)
 for sign in (-1,1):
  mesh(f'STYLE {i} sideglass {sign}',[(.10,sign*.978,1.69),(.94,sign*.978,1.69),(.91,sign*.978,z1),(.10,sign*.978,z1)],[(0,1,2,3)],root,glass)
  box(f'STYLE {i} door seam {sign}',(-.18,sign*.981,1.37),(.025,.018,1.05),root,accent,.008)
  box(f'STYLE {i} door handle {sign}',(-.03,sign*.99,1.51),(.24,.033,.07),root,metal,.025)
  box(f'STYLE {i} wheel arch {sign}',(.76,sign*.90,.91),(1.03,.14,.13),root,accent,.06)
  box(f'STYLE {i} step {sign}',(-.17,sign*.90,.64),(.53,.17,.10),root,metal,.025)
 # Roof ridgeline and hatch keep the top view from being a flat colored rectangle.
 roofz=h+.012
 box(f'STYLE {i} roof hatch',(-.47,0,roofz),(.56,.55,.035),root,accent,.07)
 for sign in (-1,1):box(f'STYLE {i} roof channel {sign}',(-.41,sign*.64,roofz),(.97,.035,.025),root,accent,.012)
 if i in (1,4):
  for sign in (-1,1):box(f'STYLE {i} aged lower panel {sign}',(-.45,sign*.985,1.02),(.48,.02,.08),root,wear,.015)
 else:
  for y in (-.45,0,.45):box(f'STYLE {i} roof marker {y}',(.88,y,window_top+.13),(.10,.09,.07),root,light,.024)
 # Modest true geometry; one driver except green crew. Head diameter0.25 vs cabwidth1.92.
 for j,y in enumerate((-.43,.43) if i==3 else (-.43,)):
  headz=min(2.13,z1-.16);x=frontx(headz)+.035
  sphere(f'STYLE {i} driver {j} head',(x,y,headz),(.085,.125,.14),root,skin)
  box(f'STYLE {i} driver {j} torso',(frontx(headz-.21)+.04,y,headz-.23),(.07,.26,.29),root,shirt,.065)
  sphere(f'STYLE {i} driver {j} cap',(x+.01,y,headz+.10),(.085,.135,.055),root,shirt)
  for dy in (-.12,.12):sphere(f'STYLE {i} driver {j} hand {dy}',(frontx(headz-.26)+.055,y+dy,headz-.26),(.047,.047,.047),root,skin)
 records.append({'truck':i,'height':h,'width':1.92,'length':2.51,'archived_shell_hidden':hidden,'native_front_wheels_restored':restored,'driver_count':2 if i==3 else 1,'body_type':'modern tall sleeper' if i in (2,3) else 'aged lower sleeper'})
# Rebuild selectors only from render-visible truck descendants.
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2')
crypto.matte_id=', '.join(o.name for r in roots for o in r.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
after=poses();delta=max(abs(before[f][r][a][b]-after[f][r][a][b]) for f in before for r in before[f] for a in range(4) for b in range(4));assert delta==0
s.frame_set(1);s.render.resolution_x=1920;s.render.resolution_y=1334;s.render.resolution_percentage=100
receipt={'records':records,'root_matrix_max_delta':delta,'camera_matrix':cam_record,'frames':[1,769],'dimensions':[1920,1334],'method':'native bevelled shell, sloped glass, roof hatch/channels, hardware, true small driver geometry; archive shell hidden','limitations':['Simple stylized native model; does not reproduce the fine drawn card artwork.','Driver heads and hands intentionally small, readability at full-map scale limited.']}
(O/'style-receipt.json').write_text(json.dumps(receipt,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'fleet-style.blend'))
for f in (1,769):s.frame_set(f);s.render.filepath=str(O/f'style-vehicles-{f:04}.png');bpy.ops.render.render(write_still=True)
# Desktop-angle zoom: preserved angle, focus green; city hidden ONLY for close QA.
fleet=set(roots)
for r in roots:fleet.update(r.children_recursive)
for o in s.objects:
 if o.type in ('MESH','FONT','CURVE') and o not in fleet:o.hide_render=True
root=bpy.data.objects['truck-3-tractor'];cam=s.camera;center=root.matrix_world@Vector((0,0,1.7));view=(cam.matrix_world.to_quaternion()@Vector((0,0,1)));cam.location=center+view*35;cam.data.ortho_scale=6;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.filepath=str(O/'style-green-desktop-close.png');bpy.ops.render.render(write_still=True)
# Front close for figures/hardware QA.
cam.location=root.matrix_world@Vector((10,-8,7));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/'style-green-front-close.png');bpy.ops.render.render(write_still=True)
print('STYLE PILOT COMPLETE')
