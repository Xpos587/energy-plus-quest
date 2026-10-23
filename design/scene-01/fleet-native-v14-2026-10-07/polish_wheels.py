import bpy,math,bmesh
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
trim=bpy.data.materials['V14 satin charcoal trim'];metal=bpy.data.materials['V14 soft warm alloy'];glass=bpy.data.materials['V14 cool glazing'];lamp=bpy.data.materials['V14 warm round headlight'];rubber=bpy.data.materials['V14 clean blue charcoal rubber']
def cylinder(name,x,y,z,r,depth,material,parent,bevel=.005):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=(0,0,0));o=bpy.context.object;o.name='V14 '+name;o.parent=parent;o.location=(x,y,z);o.rotation_euler[0]=math.pi/2;o.data.materials.append(material)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 if bevel:
  b=o.modifiers.new('Soft machined edge','BEVEL');b.width=bevel;b.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
for i in range(1,5):
 root=bpy.data.objects[f'truck-{i}-tractor'];o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];t=root.matrix_world.inverted()@o.matrix_world;pts=[t@v.co for v in o.data.vertices]
 slots={m.name:j for j,m in enumerate(o.data.materials)}
 for f in o.data.polygons:
  if f.material_index==1:continue
  p=sum((pts[v]for v in f.vertices),Vector())/len(f.vertices);x,y,z=p;ay=abs(y)
  if x<.05 and .72<z<1.10:f.material_index=slots[trim.name]
  if i in (2,3):
   if x>1.53 and .47<z<1.34 and ay<.37+.27*(z-.47)/.87:f.material_index=slots[trim.name]
   if ay>.80 and 1.50<z<2.04 and .30<x<1.44:f.material_index=slots[glass.name]
   if x>1.68 and .45<z<.71 and .66<ay<.90:f.material_index=slots[lamp.name]
  if z<.8 and ay>.63:f.material_index=slots[rubber.name]
 # Existing tire/hub scan remains in source but is covered by clean machined surfaces at exactly same axle centers.
 for axle,x in enumerate((.80,-1.35,-2.20)):
  for sy in (-1,1):
   y=sy*.805
   cylinder(f'{i} tire carcass {axle} {sy}',x,y,.355,.358,.255,rubber,root,.037)
   outside=sy*.944
   cylinder(f'{i} alloy rim ring {axle} {sy}',x,outside,.355,.229,.018,metal,root,.01)
   cylinder(f'{i} recessed wheel bowl {axle} {sy}',x,outside+sy*.012,.355,.183,.013,trim,root,.006)
   cylinder(f'{i} central hub {axle} {sy}',x,outside+sy*.022,.355,.091,.055,metal,root,.01)
   for k in range(8):
    a=2*math.pi*k/8
    cylinder(f'{i} rim vent {axle} {sy} {k}',x+.149*math.cos(a),outside+sy*.026,.355+.149*math.sin(a),.023,.010,metal,root,.004)
 # Seat the preserved old steel steps in the same dark metal finish.
 o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
