from pathlib import Path
p=Path('/home/michael/Github/energy-plus-quest/design/warehouse-blockout-2026-10-21/revise_blockout_v2.py').read_text();prefix,suffix=p.split("manifest={'units'",1);exec(prefix)
for o in bpy.data.objects:
 if o.name.startswith('Keeper 1.76m') or o.name=='Target keeper':o.location.x-=1
targets['keeper']=[9.8,2.3,1.5]
# Exact clear dimensional envelopes: uprights inside nominal bounds, beams below top, 3x3 opening between jambs.
for o in bpy.data.objects:
 if o.name.startswith('Rack'):
  if 'upright' in o.name:
   cx=min([2.4,5.4,8.4],key=lambda x:abs(x-o.location.x))
   if abs(o.location.x-cx)>.5:o.location.x+=.0275 if o.location.x<cx else -.0275
   o.location.y+=.0275 if o.location.y<4.1 else -.0275
  if 'beam' in o.name:
   o.location.y+=.0325 if o.location.y<4.1 else -.0325
   if o.location.z>2.6:o.location.z=2.655
  if 'deck' in o.name and o.location.z>2.6:o.location.z=2.67
 if ('ПРИЁМКА jamb' in o.name or 'ОТГРУЗКА jamb' in o.name):o.location.y+=-.07 if o.location.y<2.2 else .07
 if ('ПРИЁМКА header' in o.name or 'ОТГРУЗКА header' in o.name):o.location.z=3.08
# One volumetric four-rotor drone, geometric authority for later illustration.
current='Props';dc=Vector((9.5,5.8,2.8));body=sphere('Drone rounded body',dc,.22,'steel');body.scale=(1.25,1,.65)
for dx,dy in [(-.4,-.35),(-.4,.35),(.4,-.35),(.4,.35)]:
 p0=dc+Vector((dx,dy,0));line('Drone arm',dc,p0,.035,'steel');cyl('Drone rotor hub',p0,.065,.10,'dark')
 bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=6,location=p0,major_radius=.18,minor_radius=.016);place(bpy.context.object,'Drone rotor guard','steel')
 line('Drone rotor blade',p0+Vector((-.15,0,.055)),p0+Vector((.15,0,.055)),.013,'dark')
sphere('Drone camera pod',dc+Vector((0,-.08,-.2)),.09,'dark')
source=cams['Desktop']['object'].copy();source.data=cams['Desktop']['object'].data.copy();source.name='FullSourceOverscan';S.collection.objects.link(source);cams['Source']={'object':source,'resolution':(1440,1000),'look_at':cams['Desktop']['look_at']}
suffix="manifest={'units'"+suffix;suffix=suffix.replace('v2','v4')
a=suffix.index('# Full runtime source');b=suffix.index("cols['Guides'].hide_render=False",a);chunk=suffix[a:b].replace("cams['Desktop']","cams['Source']").replace("manifest['cameras']['Desktop']","manifest['cameras']['Source']").replace("'desktop-v4-clean.png'","'source-v4-clean.png'");suffix=suffix[:a]+chunk+suffix[b:];exec(suffix)
p=D/'manifest-v4.json';m=json.loads(p.read_text());m['runtime_source_contract']['desktop_viewport_source_xyxy']=[0,50,1440,950];m['runtime_source_contract']['portrait_policy']='same full overscan source plane; initial viewport fully inside source; horizontal pan reaches all four targets';p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

m=json.loads(p.read_text());m['forklift_total_length_m']=3.1;m['rack_clear_envelope_m']=[1.8,1.2,2.7];m['rack_front_plaque_projection_m']=.0725;m['front_cross_aisle_note']='3.5m to rack footprint; plaque at z2.32 protrudes .0725m above forklift guard';m['gate_opening_m']=[3,3];p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')

m=json.loads(p.read_text());m['drone']={'body_center':[9.5,5.8,2.8],'rotor_count':4,'approx_span_m':[1.16,1.06],'role':'volumetric geometry authority; not fifth gameplay target'};p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
