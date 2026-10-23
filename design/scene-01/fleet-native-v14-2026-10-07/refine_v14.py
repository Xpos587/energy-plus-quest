import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene;s.frame_set(1)
def box(name,loc,dim,root,mat,bevel=.025):
 bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name='V14 '+name;o.scale=[x/2 for x in dim];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=root;o.location=loc;o.data.materials.append(mat);b=o.modifiers.new('Rounded manufactured edge','BEVEL');b.width=bevel;b.segments=3;o.modifiers.new('Broad face normals','WEIGHTED_NORMAL');return o
for i in (1,4):
 root=bpy.data.objects[f'truck-{i}-tractor'];paint=bpy.data.materials[f'V14 {i} painted body'];h=2.13 if i==1 else 1.99
 top=1.37+((2.063 if i==1 else 2.206)-1.405)*(.86 if i==1 else .69)
 box(f'{i} structural upper windshield brow',(1.63,0,(h-.06+top+.03)/2),(.17,1.86 if i==1 else 1.77,h-.06-top-.03),root,paint,.017)
# Fourth truck has the narrower vertically-slatted old radiator and darker utility bumper.
i=4;root=bpy.data.objects['truck-4-tractor'];trim=bpy.data.materials['V14 satin charcoal trim'];metal=bpy.data.materials['V14 soft warm alloy']
for o in list(root.children_recursive):
 if o.name.startswith('V14 4 horizontal grille bar'):bpy.data.objects.remove(o,do_unlink=True)
for y in (-.25,-.125,0,.125,.25):box('4 vertical radiator slat',(1.759,y,.98),(.028,.024,.245),root,metal,.008)
o=bpy.data.objects['V14 4 separate steel bumper'];o.data.materials[0]=trim
# Lower blue day cab roof; keep the windshield/driver region exactly unchanged.
o=bpy.data.objects['V02 DETAILED 2 complete tractor'];root=o.parent;t=root.matrix_world.inverted()@o.matrix_world;inv=t.inverted();count=0
for v in o.data.vertices:
 p=t@v.co
 if p.z>2.11:p.z=2.11+(p.z-2.11)*.60;v.co=inv@p;count+=1
o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v14-native.blend'))
(P/'refine-receipt.json').write_text(json.dumps({'blue_day_cab_roof_vertices_lowered':count,'blue_windshield_unchanged_below_z':2.11,'yellow_radiator':'vertical narrow slats','yellow_bumper':'utility charcoal','old_cab_upper_header':'closed structural brow'},indent=2))
