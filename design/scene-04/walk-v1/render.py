"""Read the r10 model, render worker cells, export orthographic meshes for route/cab depth tests. Never save the blend."""
import ast,json,math,sys
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector,Matrix
D=Path(__file__).resolve().parent; W=D/'work';W.mkdir(exist_ok=True)
scene=bpy.context.scene
m=json.loads((D/'../crane-r10/render/manifest.json').read_text()); src=(D/'../../design/scene-04/blender-v6/quay.py').read_text()
# Import ONLY pure geometry functions, not the module's scene-building and file-saving side effects.
PEOPLE=3.;ORANGE="#F7721C";NAVY="#203752"
select={'srgb','_bm','ball','cyl','flush','person'}
exec(compile(ast.Module([n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in select],[]),'quay.py','exec'))
NOLINES=bpy.data.collections['NoLines']; MAT={k:bpy.data.materials[k] for k in ['flat','obj']};BATCH={};GROUPS={}
# Broad two-tone cel shadows, like the painted workers; no physical GI or texture noise.
nt=MAT['obj'].node_tree;nt.nodes.clear(); geo=nt.nodes.new('ShaderNodeNewGeometry'); color=nt.nodes.new('ShaderNodeObjectInfo');dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.25,-.62,.74);nt.links.new(geo.outputs['Normal'],dot.inputs[0]);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.interpolation='EASE';r.color_ramp.elements[0].position=.08;r.color_ramp.elements[0].color=(.36,.36,.48,1);r.color_ramp.elements[1].position=.68;r.color_ramp.elements[1].color=(1.05,1.05,1.03,1);r.color_ramp.elements.new(.25).color=(.74,.70,.76,1);nt.links.new(dot.outputs['Value'],r.inputs[0]);mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;nt.links.new(color.outputs['Color'],mul.inputs[1]);nt.links.new(r.outputs[0],mul.inputs[2]);em=nt.nodes.new('ShaderNodeEmission');nt.links.new(mul.outputs[0],em.inputs[0]);nt.links.new(em.outputs[0],nt.nodes.new('ShaderNodeOutputMaterial').inputs[0])
# Right, up, towards camera, and true scale from the r10 cameras (manifest.affine is rounded).
axes={}
with bpy.data.libraries.load(str(D/'../crane-r10/model/quay.blend'),link=False) as (a,b): b.objects=[f for f in ['desk','wide','mid'] if f not in bpy.data.objects]
for f in ('desk','wide','mid','tall'):
 c=bpy.data.objects[f];R,U,N=map(Vector,c.rotation_euler.to_matrix().transposed());s=m[f]['width']*2/c.data.ortho_scale
 axes[f]=dict(basis=[list(R),list(U),list(N)],ppm=s,origin=[m[f]['width']-s*c.location.dot(R), m[f]['height']+s*c.location.dot(U)])
print('CAMERAS',axes)
(W/'axes.json').write_text(json.dumps(axes));

def triangles(o):
 me=o.data;me.calc_loop_triangles();pts=np.array([v.co[:] for v in me.vertices]);idx=np.array([t.vertices[:] for t in me.loop_triangles]);return pts[idx]
geometry={}
for g in ('far','far_hook','far_ladder','far_top','near','near_top','ladder','crates','stops','barge','barge2','quay','pru','tractor','pallet','gift'):
 geometry[g]=np.concatenate([triangles(o) for o in scene.objects if o.get('group')==g]).astype('float32')
np.savez_compressed(W/'geometry.npz',**geometry)
for o in list(scene.objects):
 if o.type=='MESH': bpy.data.objects.remove(o,do_unlink=True)
scene.render.engine='BLENDER_EEVEE';scene.render.use_freestyle=False;scene.render.film_transparent=True; scene.eevee.taa_render_samples=16;scene.eevee.use_raytracing=False
scene.render.resolution_percentage=100;scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.image_settings.compression=45
scene.camera=bpy.data.objects['tall']; cam=scene.camera
# Anatomical section rings: bands belong to the garment rather than floating as separate discs.
V=Vector; skin='#ECA57B';boots='#302E32';band='#DBCDBB'; navy2='#293C54'; jacket='#F36A17';shade='#C54A17'
def rings(g, sections):
 bm=_bm(g,sections[0][-1],'obj',False); n=16
 for (p,xr,yr,color),(q,xs,ys,_) in zip(sections,sections[1:]):
  bm=_bm(g,color,'obj',False);v=[]
  for c,rx,ry in ((p,xr,yr),(q,xs,ys)):
   for t in range(n):
    a=t*2*math.pi/n;v.append(bm.verts.new((c[0]+rx*math.cos(a),c[1]+ry*math.sin(a),c[2])))
  for t in range(n):
   f=bm.faces.new((v[t],v[(t+1)%n],v[n+(t+1)%n],v[n+t]));f.smooth=True
  for indices in (list(reversed(range(n))),range(n,2*n)):bm.faces.new([v[i] for i in indices])

def limb(g,p,q,prof):
 # Closed circular cross-sections normal to the bone, so raised forearms and boots have full volume.
 p,q=V(p),V(q);direction=(q-p).normalized();x=V((0,1,0)).cross(direction).normalized();y=direction.cross(x);n=14
 for (t0,r0,c),(t1,r1,_) in zip(prof,prof[1:]):
  bm=_bm(g,c,'obj',False);vv=[]
  for t,r in ((t0,r0),(t1,r1)):
   for i in range(n):
    a=i*math.tau/n;vv.append(bm.verts.new(p.lerp(q,t)+(x*math.cos(a)+y*math.sin(a))*r))
  for i in range(n):bm.faces.new((vv[i],vv[(i+1)%n],vv[n+(i+1)%n],vv[n+i])).smooth=True
  for indices in (list(reversed(range(n))),range(n,2*n)):bm.faces.new([vv[i] for i in indices])

def worker(g,who,action,phase):
 hat='#FA841B' if who=='Ivan' else '#FFF1D5'; t=(phase+(.25 if action=='Climb' else 0))*math.tau; sit=action=='Cab'; climb=action=='Climb'; bob=0 if sit or climb else -.022*math.cos(2*t)
 base=.55 if sit else .89+bob; lean=.085 if not climb else .025
 # Use quay.person()'s head, hard-hat brim, neck, beard & peak verbatim; replace its fixed arm/trouser chains.
 old=globals()['ball']; oldc=globals()['cyl'];headscale=1.28
 def headball(group,color,c,r,**kw):
  if c[2]<.62:return
  lift=.058 if color==hat else .016
  center=(c[0]*headscale+lean,c[1]*headscale,base+.62+(c[2]-.62)*headscale+lift);kw.pop('M',None);old(group,color,center,r*headscale,**kw)
 def headcyl(group,color,c,r,h,**kw):
  kw.pop('M',None);oldc(group,'#A54B18' if who=='Ivan' else '#B9AFAC',(c[0]*headscale+lean,c[1]*headscale,base+.62+(c[2]-.62)*headscale+.054),r*headscale,h*headscale,**kw)
 globals()['ball']=headball;globals()['cyl']=headcyl
 try:person(g,(0,0,0),0,hat,beard=who=='Petr',sitting=True,s=1)
 finally:globals()['ball']=old;globals()['cyl']=oldc
 # Ears, eyes, nose and helmet rib. Back views keep a hairline under the brim.
 for s in [-1,1]:
  ball(g,'#C38866',(lean-.014,s*.107,base+.747),.031,sy=.6,sz=1.35)
  ball(g,'#342F35',(lean-.065,s*.070,base+.79),.052,sx=.9,sy=.78,sz=1.3)
  ball(g,'#704731',(lean+.102,s*.083,base+.835),.024,sx=.81,sy=.77,sz=.95)
  ball(g,'#F9D9B7',(lean+.109,s*.087,base+.834),.020,sx=.85,sy=.82,sz=.86)
  ball(g,'#322D33',(lean+.120,s*.090,base+.835),.012,sx=.84,sy=.88,sz=1.18)
  ball(g,'#47352E',(lean+.101,s*.088,base+.860),.018,sx=.86,sy=1.19,sz=.43)
 ball(g,skin,(lean+.143,0,base+.794),.033,sx=1.12,sy=.74)
 ball(g,'#AF715F',(lean+.125,0,base+.746),.021,sx=.53,sy=1.15,sz=.34)
 rib='#FF9C23' if who=='Ivan' else '#FDF3DE';accent='#FFBB51' if who=='Ivan' else '#FFF9E6'
 ball(g,rib,(lean-.009,0,base+1.026),.113,sx=1.24,sy=.31,sz=.68)
 ball(g,accent,(lean-.04,-.071,base+1.069),.046,sx=1.24,sy=.52,sz=.58)
 ball(g,'#413332',(lean-.067,0,base+.763),.090,sx=.87,sy=1.11,sz=.72)
 # Hip and jacket profile, navy shoulder yoke, reflective silver waist band, centre zip, pocket.
 rings(g,[((lean*(z/.6),0,base+z),rx,ry,c) for z,rx,ry,c in [(-.09,.115,.176,shade),(.015,.14,.199,NAVY),(.09,.146,.207,navy2),(.12,.151,.213,band),(.157,.153,.215,jacket),(.305,.161,.216,band),(.33,.163,.216,jacket),(.35,.163,.216,jacket),(.445,.148,.222,NAVY),(.51,.125,.225,navy2),(.553,.105,.123,navy2),(.58,.071,.076,NAVY)]])
 limb(g,(.154+lean*.28,0,base+.17),(.15+lean*.68,0,base+.4),[(0,.009,shade),(1,.009,shade)])
 ball(g,navy2,(lean*.86,0,base+.546),.112,sx=.89,sy=1.03,sz=.55)
 # Knees and ankles use a fixed-length two-link chain with a planted heel / bent recovery leg.
 for s in [-1,1]:
  a=t+(0 if s<0 else math.pi);sw=math.sin(a);rec=0.;yy=s*.112
  if not (climb or sit):
   u=(a/math.tau)%1;v=2*(u-.5)
   # The stance boot moves back at exactly 1.28 local units/cycle; the root advances
   # the same amount at runtime. Recovery returns the foot while it is off the floor.
   sw=(1-4*u) if u<.5 else -1+2*v-2*math.sin(math.tau*v)/math.pi
   rec=max(0,math.sin(math.pi*v)) if u>=.5 else 0.
  hip=V((0,yy,base-.038)); foot=V((.32*sw,yy,.113+.18*rec**1.7));
  if climb:foot=V((.15,yy,.13+.28*(sw+1)/2))
  if sit:foot=V((.36,yy,.03))
  d=foot-hip; knee=(hip+foot)/2+V((-d.z,0,d.x)).normalized()*math.sqrt(max(0,.393**2-d.length_squared/4))
  limb(g,hip,knee,[(0,.115,shade),(.14,.118,jacket),(.72,.093,jacket),(.98,.091,shade),(1,.088,shade)])
  ball(g,shade,knee,.090)
  limb(g,knee,foot,[(0,.09,jacket),(.28,.088,jacket),(.43,.083,NAVY),(.65,.082,band),(.75,.08,NAVY),(1,.073,boots)])
  ball(g,boots,foot+V((.036,0,-.03)),.083,sx=1.52,sy=1.08,sz=.87)
  ball(g,'#25282C',foot+V((.055,0,-.072)),.076,sx=1.67,sy=1.08,sz=.57)
  shoulder=V((lean*.73,s*.21,base+.453)); elbow=V((-.04-.155*sw,s*.255,base+.23+.040*abs(sw)));wrist=V((.08-.28*sw,s*.265,base+.026+.12*abs(sw)))
  if climb:elbow=V((.074,s*.286,base+.50+.12*sw));wrist=V((.23,s*.21,base+.69+.17*sw))
  if sit:elbow=V((.04,s*.253,base+.17));wrist=V((.34,s*.20,base+.19))
  ball(g,NAVY,shoulder,.09);limb(g,shoulder,elbow,[(0,.09,NAVY),(.26,.092,navy2),(.42,.087,jacket),(1,.075,jacket)])
  ball(g,jacket,elbow,.075);limb(g,elbow,wrist,[(0,.076,jacket),(.34,.071,band),(.51,.069,navy2),(.87,.063,NAVY),(1,.061,NAVY)])
  hand=wrist+(wrist-elbow).normalized()*.046;ball(g,skin,hand,.056,sy=.80,sz=1.20)
 # Expandable back pleat & twin lower jacket pockets, visible in the high camera.
 for side in (-1,1):
  ball(g,'#D95418',(-.094,side*.117,base+.212),.061,sx=.28,sy=.84,sz=.82)
  ball(g,'#EF7726',(-.094,side*.118,base+.240),.046,sx=.31,sy=1.15,sz=.34)
 # Worker looks slightly towards the berth while his feet track the lane.
 if action=='Walk':
  turn=Matrix.Rotation(math.radians(-53),4,'Z');z0=base+.53
  for bm in BATCH.values():
   for v in bm.verts:
    if v.co.z>z0:v.co=turn@v.co
 flush()

cells=[]
for who in ('Ivan','Petr'):
 for action,deg,n in [('East',0,8),('Inland',48,8),('Seaward',-91,8),('Climb',11,2),('Cab',0,16)]:
  for i in range(n):
   # Cab local position matches the outcome rig; bring eyes above the sill, under roof.
   cells.append(dict(who=who,action=action,i=i,angle=m['scene']['slews'][i] if action=='Cab' else deg))
# Build each topology only once. Orient duplicated meshes in a flat screen-space contact atlas.
rig={}; seats={}
for c in cells:
 act=c['action'];key=(c['who'], 'Walk' if act not in ('Climb','Cab') else act, c['i'] if act!='Cab' else 0)
 if key not in rig:
  g=''.join(map(str,key));worker(g,key[0],key[1],key[2]/(2 if act=='Climb' else 8));rig[key]=GROUPS[g];
  if act=='Cab':seats[key[0]]=np.concatenate([triangles(o) for o in rig[key]]).astype('float32')
 c['rig']=key
np.savez_compressed(W/'seats.npz',**seats)
# Atlas view uses exactly the same angles as the scene; position is translated in camera XY only.
cols=8;rows=math.ceil(len(cells)/cols);cell=320; span=8.8;ppm=cell/span; anchor=(.5,.755);meta=[]
for anglefmt in ['desk','tall']:
 basis=axes[anglefmt]['basis'];R,U,N=map(V,basis);cam.rotation_euler=Matrix((R,U,N)).transposed().to_euler();cam.location=N*200;cam.data.ortho_scale=span*cols;cam.data.sensor_fit='HORIZONTAL';cam.data.shift_x=cam.data.shift_y=0;scene.camera=cam
 scene.render.resolution_x=cols*cell;scene.render.resolution_y=rows*cell
 clones=[]
 for j,c in enumerate(cells):
  col,row=j%cols,j//cols;cx=(col+anchor[0]-cols/2)*span;cy=(rows/2-row-anchor[1])*span
  seated=c['action']=='Cab';tilt=0 if seated else (-15 if anglefmt=='desk' else -18)
  actorScale=1.84 if seated else 2.85
  T=Matrix.Translation(R*cx+U*cy)@Matrix.Rotation(math.radians(tilt),4,R)@Matrix.Rotation(math.radians(c['angle']),4,'Z')@Matrix.Scale(actorScale,4)
  if anglefmt=='desk':meta.append({k:v for k,v in c.items() if k!='rig'}|{'box':[col*cell,row*cell,cell,cell]})
  for template in rig[c['rig']]:
   o=bpy.data.objects.new('posed',template.data);scene.collection.objects.link(o);o.matrix_world=T;o.color=template.color;clones.append(o);template.hide_render=True
 scene.render.filepath=str(W/(anglefmt+'-atlas.png'));bpy.ops.render.render(write_still=True)
 for o in clones:bpy.data.objects.remove(o,do_unlink=True)
(W/'cells.json').write_text(json.dumps(dict(items=meta,anchor=anchor,ppm=ppm)))
