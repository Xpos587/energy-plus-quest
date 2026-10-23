import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
# Retain original physical meshes, replace all photographic surface color by role.
trim=bpy.data.materials['V14 satin charcoal trim'];metal=bpy.data.materials['V14 soft warm alloy'];glass=bpy.data.materials['V14 cool glazing'];lamp=bpy.data.materials['V14 warm round headlight']
rubber=trim.copy();rubber.name='V14 clean blue charcoal rubber'
for n in rubber.node_tree.nodes:
 if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and not n.inputs[1].is_linked:n.inputs[1].default_value=(.07,.105,.13,1)
receipts=[]
for i in range(1,5):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];paint=bpy.data.materials[f'V14 {i} painted body'];r=o.parent;t=r.matrix_world.inverted()@o.matrix_world;pts=[t@v.co for v in o.data.vertices]
 role={}
 for name,m in [('paint',paint),('rubber',rubber),('metal',metal),('glass',glass),('trim',trim),('lamp',lamp)]:role[name]=len(o.data.materials);o.data.materials.append(m)
 counts={k:0 for k in role}
 for f in o.data.polygons:
  if f.material_index==1:continue
  p=sum((pts[v]for v in f.vertices),Vector())/len(f.vertices);x,y,z=p;ay=abs(y);kind='metal'
  if f.material_index in (2,4):kind='paint'
  elif f.material_index==3:kind='trim'
  elif z<1.15:
   nearest=min((.80,-1.35,-2.20),key=lambda q:abs(x-q));rad=math.hypot(x-nearest,z-.35)
   if rad<.39 and ay>.36:
    kind='rubber'
    if rad<.238 and ay>.785:kind='metal'
    if .08<rad<.135 and ay>.80:kind='trim'
   elif x>1.30 and z>.50:kind='paint' if ay>.52 else 'trim'
   elif x>.08 and ay>.65 and z>.69:kind='paint'
   elif ay<.37:kind='trim'
  else:
   kind='paint'
   if ay>.97:kind='trim'
   elif ay>.85 and 1.48<z<2.06 and .2<x<1.5:kind='glass'
   elif x>1.52 and z<1.38:kind='trim'
  f.material_index=role[kind];counts[kind]+=1
 o.data.update()
 # All overlay sill / mirror materials follow the same native finish too.
 for ob in r.children_recursive:
  if ob.name.startswith(f'V09 CLEAN {i}') and ob.type=='MESH':
   for j in range(len(ob.data.materials)):ob.data.materials[j]=paint if 'sill' in ob.name else trim
 if i in (1,4):
  shift=(-.12 if i==1 else .10)-.25
  for ob in r.children_recursive:
   if ob.name==f'{i} exhaust stack' or ob.name.startswith(f'V08 {i} light exhaust'):ob.location.x+=shift
  stack=bpy.data.objects[f'{i} exhaust stack'];stack.location.z-=.18;stack.scale.z*=.88
  for ob in r.children_recursive:
   if ob.name.startswith(f'V08 {i} light exhaust'):ob.location.z-=.27
 receipts.append({'truck':i,'material_face_counts':counts,'original_tread_hub_mesh_retained':True})
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
(P/'clean-material-receipt.json').write_text(json.dumps(receipts,indent=2))
