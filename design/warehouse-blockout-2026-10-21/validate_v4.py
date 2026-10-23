import bpy,json,math
from pathlib import Path
from mathutils import Vector
D=Path('/home/michael/Github/energy-plus-quest/design/warehouse-blockout-2026-10-21');R=Path('/home/michael/Github/energy-plus-quest/docs/reviews/inventory-2026-10-21-geometry');bpy.ops.wm.open_mainfile(filepath=str(D/'warehouse-blockout-v4.blend'));m=json.loads((D/'manifest-v4.json').read_text())
def bounds(group):
 pts=[o.matrix_world@Vector(p) for o in group for p in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];return {'min':lo,'max':hi,'dimensions':[b-a for a,b in zip(lo,hi)]}
measured={}
for n in range(1,4):
 b=bounds([o for o in bpy.data.objects if o.name.startswith('Rack'+str(n))]);measured['rack'+str(n)]=b
 assert all(abs(a-b)<1e-5 for a,b in zip(b['dimensions'],[1.8,1.2,2.7])),b
clear=[measured['rack2']['min'][0]-measured['rack1']['max'][0],measured['rack3']['min'][0]-measured['rack2']['max'][0]];assert all(abs(v-1.2)<1e-5 for v in clear)
measured['forklift']=bounds([o for o in bpy.data.objects if o.name.startswith('Forklift')]);measured['keeper']=bounds([o for o in bpy.data.objects if o.name.startswith('Keeper 1.76m')]);assert abs(measured['keeper']['dimensions'][2]-1.76)<1e-5
plaque=[o for o in bpy.data.objects if 'plaque' in o.name];plaque.sort(key=lambda o:o.location.x);assert [o.name.split(' plaque')[0] for o in plaque]==['А-Б','В-К','Л-М','Н-У','Ф-Э','Ю-Я']
parallel={}
for name,c in m['cameras'].items():
 p=c['proof_points_uvz'];a=[p['receivingY'][i]-p['receiving0'][i] for i in [0,1]];b=[p['dispatchY'][i]-p['dispatch0'][i] for i in [0,1]];dot=sum(x*y for x,y in zip(a,b))/math.sqrt(sum(x*x for x in a)*sum(x*x for x in b));parallel[name]={'normalized_projected_dot':dot,'receiving_Y_vector_uv':a,'dispatch_Y_vector_uv':b};assert abs(dot-1)<1e-5
s=m['runtime_source_contract'];W,H=s['dimensions'];assert s['full_source']=='source-v4-clean.png';assert all(0<x<W and 0<y<H for x,y in s['all_four_anchor_px'].values());x0,y0,x1,y1=s['portrait_initial_viewport_source_xyxy'];assert 0<=x0<x1<=W and 0<=y0<y1<=H
receipt={'status':'PASS','measured_world_bounds_m':measured,'clear_pedestrian_gaps_m':clear,'plaques_left_to_right':[{'text':o.name.split(' plaque')[0],'world':list(o.location)} for o in plaque],'parallel_wall_projected_direction':parallel,'same_camera_rotation_desktop_portrait':m['cameras']['Desktop']['rotation_euler']==m['cameras']['Portrait']['rotation_euler'],'source_anchor_and_portrait_crop_inside':True,'limits':['front3.5m is footprint-to-wall spacing; not a certified turning envelope','1.2m rack gaps are pedestrian/service, excluded from forklift travel','portrait initial viewport excludes keeper; horizontal pan required','cutaway surfaces are omitted for legibility; physical wall planes unchanged']};(R/'geometry-validation-v4.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'PASS','clear_gaps':clear,'forklift_envelope':measured['forklift']['dimensions'],'keeper_height':measured['keeper']['dimensions'][2]}))
