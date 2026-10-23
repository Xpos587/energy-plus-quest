import bpy, math, pathlib, json
from mathutils import Vector
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05');OUT=P/'native'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_percentage=100
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.79,.83,.79,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
records=[]
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*c,1);n.inputs['Roughness'].default_value=.88;n.inputs['Specular IOR Level'].default_value=.12;return m
green=mat('Moderate sage green paint',(.27,.48,.30));gray=mat('Medium slate grille',(.21,.29,.30));rubber=mat('Warm soft tire',(.18,.21,.21));white=mat('Warm white trim',(.84,.85,.77));seatmat=mat('Seat textile muted blue',(.32,.40,.43));light=mat('Warm headlamps',(.95,.88,.59))
def source(k,name,material,offset=(0,0,0),mapaxes=True):
 f=next((P/'sources/scania-r730-paolo').glob(f'r730-{k}*.stl'));bpy.ops.wm.stl_import(filepath=str(f));o=bpy.context.object;o.name=name
 for v in o.data.vertices:
  x,y,z=v.co
  v.co=Vector((x-55,-z+50,y)) + Vector(offset) if mapaxes else v.co+Vector(offset)
 o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 records.append({'part':f.name,'name':name,'source_map':'(x-55, 50-z, y)' if mapaxes else 'original','offset_mm':offset})
 return o
body=source(1,'SCANIA curved cab with embossed door panels',green,(0,0,53))
base=source(8,'SCANIA lower cab curved wheel arches and steps',green,(1.8,-23,0))
roof=source(46,'SCANIA integrated curved high roof',green,(.7,0,53))
frame=source(31,'SCANIA open windshield and sidewindow frame',gray,(1.65,-55,101))
grille=source(10,'SCANIA sculpted upper front grille',gray,(10.3,-100,53))
lower=source(11,'SCANIA lower fascia grille',gray,(21,-109,12))
# Printed full seat is horizontal on bed; remap same cab convention then center interior.
for side in [-1,1]:
 o=source(39,'Interior detailed seat '+str(side),seatmat,mapaxes=False)
 vs=[v.co.copy() for v in o.data.vertices];lo=Vector(tuple(min(v[j] for v in vs) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vs) for j in range(3)))
 for v in o.data.vertices:
  x,y,z=v.co-(lo+hi)/2;v.co=(x+side*26,-y+12,z+106)
# source mirrors printed face upward; mirror shapes retain full housings and stalks.
for k,side in [(33,-1),(47,1)]:
 o=source(k,'Detailed mirror '+str(side),green,mapaxes=False)
 vs=[v.co.copy() for v in o.data.vertices];lo=Vector(tuple(min(v[j] for v in vs) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vs) for j in range(3)))
 for v in o.data.vertices:
  x,y,z=v.co-(lo+hi)/2;v.co=(side*(61+z),-40+x,y+123)
# wheels sourced STL tread plus separate embossed source rims.
for yi in [8,130,182]:
 for side in [-1,1]:
  o=source(2 if yi==8 else 3,'Detailed tread tire '+str(yi)+' '+str(side),rubber,mapaxes=False)
  vs=[v.co.copy() for v in o.data.vertices];lo=Vector(tuple(min(v[j] for v in vs) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vs) for j in range(3)))
  for v in o.data.vertices:v.co=v.co-(lo+hi)/2+Vector((side*49,yi,22.15))
  o=source(18 if yi==8 else 20,'Embossed wheel rim '+str(yi)+' '+str(side),white,mapaxes=False)
  vs=[v.co.copy() for v in o.data.vertices];lo=Vector(tuple(min(v[j] for v in vs) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vs) for j in range(3)))
  for v in o.data.vertices:v.co=v.co-(lo+hi)/2+Vector((side*58,yi,22.15))
# Kit rear dual fenders printed arc vertical; x=length y=width z=height, translate behind cab.
for k,side in [(12,-1),(40,1)]:
 o=source(k,'Detailed tandem rear mudguard '+str(side),gray,mapaxes=False)
 for v in o.data.vertices:
  x,y,z=v.co;v.co=(side*(39+y),x+100,z+23)
# load-bearing frame source rail 6 has long x axis; two parallel rails
for side in [-1,1]:
 o=source(6,'Native kit chassis frame rail '+str(side),gray,mapaxes=False)
 for v in o.data.vertices:
  x,y,z=v.co;v.co=(side*23+(y-14.6)*.2,x-20,30+z*.18)
# tank molded source mesh
for side in [-1,1]:
 o=source(14,'Curved fuel tank '+str(side),white,mapaxes=False)
 for v in o.data.vertices:
  x,y,z=v.co;v.co=(side*42+(y-15)*.5,x+55,z+15)
# subtle physical ground
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,80,-.6));bpy.context.object.name='Matte warm studio ground';bpy.context.object.data.materials.append(mat('Background warm ivory',(.89,.88,.82)))
for loc,power,size in [((-220,-220,330),2200000,250),((180,30,300),1200000,210)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,40,80))-o.location).to_track_quat('-Z','Y').to_euler()
def cam(name,loc,target,scale,res):
 bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.name=name;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;s.camera=c;s.render.resolution_x=res[0];s.render.resolution_y=res[1];s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
 return {'camera':name,'location_mm':loc,'target_mm':target,'ortho_scale_mm':scale,'resolution':res}
cs=[]
cs.append(cam('shape-gate-front-three-quarter',(-260,-340,235),(0,37,87),350,(1400,1050)))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scania-native-candidate.blend'))
cs.append(cam('orthographic-front',(0,-400,94),(0,0,94),205,(900,900)))
cs.append(cam('orthographic-side',(-500,72,94),(0,72,94),310,(1200,800)))
cs.append(cam('map-heading-0',(-280,-330,370),(0,65,65),390,(640,640)))
cs.append(cam('map-heading-120',(370,220,370),(0,65,65),390,(640,640)))
cs.append(cam('map-heading-240',(-230,390,370),(0,65,65),390,(640,640)))
(OUT/'placement-receipt.json').write_text(json.dumps({'status':'assembled shape candidate, visual gate pending; approximate print-kit placement','source':'Paolo Scania R730 Printables 1396992 CC BY 4.0','materials':{m.name:list(m.diffuse_color) for m in [green,gray,rubber,white,seatmat]},'engine':'Cycles','samples':24,'camera_records':cs,'placements':records},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scania-native-candidate.blend'))
