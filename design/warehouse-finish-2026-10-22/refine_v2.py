import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('/home/michael/Github/energy-plus-quest');D=ROOT/'design/warehouse-finish-2026-10-22';R=ROOT/'docs/reviews/inventory-2026-10-22-finish';bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-finish-v1.blend'));S=bpy.context.scene
# Stronger direct illustration palette; physical lighting stays soft.
for k,col in {'blue':(.012,.085,.40),'orange':(.95,.115,.006),'ivory':(.82,.79,.66),'floor':(.38,.58,.72),'dark':(.014,.027,.048),'carton':(.60,.32,.10),'tape':(.80,.58,.28),'green':(.08,.30,.035)}.items():
 m=bpy.data.materials['Finish '+k];m.diffuse_color=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1)
S.world.node_tree.nodes['Background'].inputs[1].default_value=.40
for n,p in [('key',1400),('fill',800),('window',900)]:bpy.data.lights[n].energy=p
S.view_settings.view_transform='Standard';S.view_settings.look='None';S.view_settings.exposure=-.25
coll=bpy.data.collections['Illustration finishing']
def box(n,p,d,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name='Finish '+n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);o.data.materials.append(bpy.data.materials['Finish '+m]);b=o.modifiers.new('Soft edge','BEVEL');b.width=.012;b.segments=3;return o
# Real overhead protection grille, exact original guard envelope [-.7,.7]×[-.55,.55]×[-.06,.06].
bpy.data.objects['Forklift overhead guard'].hide_render=True
for y in [1.2,2.2]:box('overhead guard edge',(6.8,y,2.03),(1.4,.1,.12),'dark')
for x in [6.15,7.45]:box('overhead guard edge',(x,1.7,2.03),(.1,.9,.12),'dark')
for x in [6.45,6.80,7.15]:box('overhead guard safety bar',(x,1.7,2.045),(.04,.9,.07),'dark')
# Worker uniform contrast and warm face. No new people or scene anchors.
for o in bpy.data.objects:
 if o.name.startswith('Finish driver head'):o.data.materials[0]=bpy.data.materials['Finish skin']
S.cycles.samples=48;S.render.filepath=str(R/'source-v2-clean.png');bpy.ops.wm.save_as_mainfile(filepath=str(D/'warehouse-finish-v2.blend'));bpy.ops.render.render(write_still=True)
# Check full unchanged originals by direct coordinates against immutable source in separate audit after render.
print('FINISH V2 COMPLETE')
