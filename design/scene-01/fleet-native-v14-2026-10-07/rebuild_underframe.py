import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
trim=bpy.data.materials['V14 satin charcoal trim'];metal=bpy.data.materials['V14 soft warm alloy']
def box(name,loc,dim,parent,material,r=.03):
 bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name='V14 '+name;o.scale=[x/2 for x in dim];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=parent;o.location=loc;o.data.materials.append(material);b=o.modifiers.new('Soft manufactured radius','BEVEL');b.width=r;b.segments=3;o.modifiers.new('Broad face normals','WEIGHTED_NORMAL');return o
counts={}
for i in range(1,5):
 root=bpy.data.objects[f'truck-{i}-tractor'];o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];o.data.materials[1]=bpy.data.materials[f'V02 {i} Permanent high-detail two-driver windshield.001'];t=root.matrix_world.inverted()@o.matrix_world
 bm=bmesh.new();bm.from_mesh(o.data);bad=[]
 for f in bm.faces:
  if f.material_index==1:continue
  pts=[t@v.co for v in f.verts]
  if i in (1,4) or any((p.x<.12 and p.z<1.30) or (p.x<1.37 and p.z<.90)for p in pts):bad.append(f)
 counts[i]=len(bad);bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update()
 for sy in (-1,1):
  box(f'{i} continuous chassis rail {sy}',(-.90,sy*.36,.70),(3.40,.13,.18),root,trim,.022)
  box(f'{i} clean fuel tank {sy}',(-.32,sy*.70,.53),(.78,.37,.47),root,metal,.10)
  for x in (-.57,-.07):box(f'{i} tank strap {sy} {x}',(x,sy*.707,.53),(.034,.385,.485),root,trim,.014)
  for j,x in enumerate((-1.35,-2.20)):
   # Smooth fender sits outside the tyre, original scan triangles are gone.
   verts=[];faces=[]
   for a in range(25):
    theta=math.pi*a/24
    for y in (sy*.65,sy*.962):verts.append((x+.398*math.cos(theta),y,.355+.398*math.sin(theta)))
   for a in range(24):faces.append((2*a,2*a+1,2*a+3,2*a+2))
   me=bpy.data.meshes.new('clean curved wheelguard');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(f'V14 {i} smooth rear wheelguard {sy} {j}',me);s.collection.objects.link(ob);ob.parent=root;me.materials.append(trim)
   for p in me.polygons:p.use_smooth=True
   sol=ob.modifiers.new('Pressed steel thickness','SOLIDIFY');sol.thickness=.023
 for x in (-2.40,-1.70,-.75):box(f'{i} frame crossmember {x}',(x,0,.70),(.10,.84,.17),root,trim,.02)
 box(f'{i} rear platform',(-1.67,0,.89),(1.9,.74,.08),root,trim,.025)
 # All scanned front arches are removed. A manufactured lip follows the remaining front tyre.
 if i in (2,3):
  paint=bpy.data.materials[f'V14 {i} painted body']
  for sy in (-1,1):
   verts=[];faces=[]
   for a in range(25):
    theta=math.pi*a/24
    for rad in (.392,.445):verts.append((.80+rad*math.cos(theta),sy*.962,.355+rad*math.sin(theta)))
   for a in range(24):faces.append((2*a,2*a+1,2*a+3,2*a+2))
   me=bpy.data.meshes.new('front wheel lip');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(f'V14 {i} smooth front wheel lip {sy}',me);s.collection.objects.link(ob);ob.parent=root;me.materials.append(paint)
   so=ob.modifiers.new('Lip thickness','SOLIDIFY');so.thickness=.035
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
(P/'underframe-receipt.json').write_text(json.dumps({'removed_source_faces':counts,'old_scan_retained':'crew faces only','new_underframe':'Continuous double rails, crossmembers, twin fuel tanks, curved rear wheelguards','modern_original_geometry':'Cab upper and front body only; all old lower/axle fragments removed by any-vertex region'},indent=2))
