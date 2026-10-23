from pathlib import Path
p=Path('/home/michael/Github/energy-plus-quest/design/warehouse-blockout-2026-10-21/revise_blockout_v2.py').read_text();prefix,suffix=p.split("manifest={'units'",1);exec(prefix)
for o in bpy.data.objects:
 if o.name.startswith('Keeper 1.76m') or o.name=='Target keeper':o.location.x-=1
targets['keeper']=[9.8,2.3,1.5]
source=cams['Desktop']['object'].copy();source.data=cams['Desktop']['object'].data.copy();source.name='FullSourceOverscan';S.collection.objects.link(source);cams['Source']={'object':source,'resolution':(1440,1000),'look_at':cams['Desktop']['look_at']}
suffix="manifest={'units'"+suffix;suffix=suffix.replace('v2','v3')
a=suffix.index('# Full runtime source');b=suffix.index("cols['Guides'].hide_render=False",a);chunk=suffix[a:b].replace("cams['Desktop']","cams['Source']").replace("manifest['cameras']['Desktop']","manifest['cameras']['Source']").replace("'desktop-v3-clean.png'","'source-v3-clean.png'");suffix=suffix[:a]+chunk+suffix[b:];exec(suffix)
p=D/'manifest-v3.json';m=json.loads(p.read_text());m['runtime_source_contract']['desktop_viewport_source_xyxy']=[0,50,1440,950];m['runtime_source_contract']['portrait_policy']='same full overscan source plane; initial viewport fully inside source; horizontal pan reaches all four targets';p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
