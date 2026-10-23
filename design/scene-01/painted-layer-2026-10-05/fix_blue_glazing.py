"""Geometry-only blue windshield repair; source cab texture pixels remain untouched."""
import bpy,json,time
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene;root=bpy.data.objects['truck-2-tractor'];g=bpy.data.objects['2 windshield']
# Follow imported tapered nose and wrap both rounded front corners instead of
# leaving the narrow, forward-floating legacy plane with exposed painted edges.
verts=[(1.025,-.59,1.69),(1.025,.59,1.69),(.70,.60,2.47),(.70,-.60,2.47),(.79,-.80,1.67),(.79,.80,1.67),(.54,.79,2.45),(.54,-.79,2.45)]
faces=[(0,1,2,3),(4,0,3,7),(1,5,6,2)]
mesh=bpy.data.meshes.new('BLUE fitted full-width wrapped windshield');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(bpy.data.materials['PILOT 2 translucent cab glass']);g.data=mesh;g.location=(0,0,0);g.rotation_euler=(0,0,0);g.scale=(1,1,1)
# Single existing native relief sits on the fitted front glass plane.
def glass_x(z):return 1.025-(z-1.69)/(.78)*.325
head=bpy.data.objects['PILOT 2 driver head'];torso=bpy.data.objects['PILOT 2 driver torso']
head.location=(glass_x(2.17)+.045,-.30,2.17);head.scale=(.10,.85,.98)
torso.location=(glass_x(1.92)+.045,-.30,1.92);torso.scale=(.055,.245,.47)
# Empty neutral passenger seat, without a skin/hair/head element.
seatmat=bpy.data.materials['PILOT soft slate fittings']
for name,location,scale in [('empty passenger seat back',(glass_x(1.90)+.03,.30,1.90),(.04,.29,.36)),('empty passenger seat cushion',(glass_x(1.74)+.03,.30,1.74),(.055,.31,.08))]:
 bpy.ops.mesh.primitive_cube_add(size=1);obj=bpy.context.object;obj.name='BLUE '+name;obj.parent=root;obj.location=location;obj.scale=scale;obj.data.materials.append(seatmat)
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');objects=[]
for r in [o for o in s.objects if o.name.startswith('truck-')]:objects.extend(o for o in r.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
crypto.matte_id=', '.join(o.name for o in objects)
s.render.resolution_x=3840;s.render.resolution_y=2667;s.eevee.taa_render_samples=8;s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(p/'painted-vehicles-driver-fixed-optimized.blend'))
times={}
for f in (1,769):
 s.frame_set(f);s.render.filepath=str(p/'repaired-stills'/f'4k-driver-fixed-{f:04}.png');t=time.monotonic();bpy.ops.render.render(write_still=True);times[str(f)]=round(time.monotonic()-t,3)
(p/'blue-glazing-repair-receipt.json').write_text(json.dumps({'source':'painted-vehicles-repaired-optimized.blend','change':'Blue-only wrapped opaque windshield, moved existing one-driver relief, added empty neutral passenger seat','textures_modified':False,'other_trucks_modified':False,'routes_camera_modified':False,'frames':[1,769],'dimensions':[3840,2667],'samples':8,'render_wall_seconds':times,'full_animation_rendered':False},indent=2));print('BLUE GEOMETRY REPAIR COMPLETE',times)
