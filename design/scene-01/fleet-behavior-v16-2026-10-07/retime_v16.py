"""Blender paired-root retiming; default read-only analysis, --apply writes a candidate.
blender -b SOURCE --python retime_v16.py -- [--apply] [--phase 1] [--output PATH]
The 8-second proof is NOT presented as a seamless loop. Full independent route
periods are recorded; loop collision qualification is a separate gate.
"""
import argparse, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Euler, Matrix
P = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true')
parser.add_argument('--phase', type=float, default=1)
parser.add_argument('--output', default=str(P/'fleet-v16-motion.blend'))
a = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
s = bpy.context.scene
fps = s.render.fps / s.render.fps_base
N = 192
rates = {1:1.0,2:0.45,3:1.0,4:0.60}
roots = {i:[bpy.data.objects[f'truck-{i}-{p}'] for p in ('tractor','trailer')] for i in rates}
s.frame_set(1)

def channels(o):
    ad = o.animation_data
    return list(ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves)
curves = {o.name:channels(o) for pair in roots.values() for o in pair}

def matrix(o, t):
    loc, rot = o.location.copy(), o.rotation_euler.copy()
    for c in curves[o.name]:
        (loc if c.data_path=='location' else rot)[c.array_index] = c.evaluate(t)
    return Matrix.LocRotScale(loc, rot.to_quaternion(), o.scale)

def bounds(points):
    return [min(v[k] for v in points) for k in range(3)], [max(v[k] for v in points) for k in range(3)]

def rectangle(lo,hi,m):
    return [(m@Vector((x,y,0))).xy for x,y in ((lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1]))]

def separation(p,q):
    gaps=[]
    for poly in (p,q):
        for x,y in zip(poly,poly[1:]+poly[:1]):
            d=y-x; axis=Vector((-d.y,d.x)).normalized()
            pp=[v.dot(axis) for v in p];qq=[v.dot(axis) for v in q]
            gaps.append(max(min(qq)-max(pp),min(pp)-max(qq)))
    return max(gaps) # positive separating-axis gap is a conservative lower bound

local={};fleet=set()
for pair in roots.values():
    for root in pair:
        own={root,*root.children_recursive};fleet.update(own)
        points=[]
        for obj in own:
            if obj.type=='MESH' and not obj.hide_render and 'smoke' not in obj.name.lower():
                transform=root.matrix_world.inverted()@obj.matrix_world
                points.extend(transform@Vector(v) for v in obj.bound_box)
        local[root.name]=bounds(points)
# Major solid architecture; street furniture is outside this bounded gate.
obstacles=[]
for o in bpy.data.objects:
    if o in fleet or o.type!='MESH':continue
    name=o.name.lower()
    if name.endswith(' body') or (name.startswith('new warehouse') and any(k in name for k in ('root','lower-wing','front-white-pier','loading-column'))):
        lo,hi=bounds([o.matrix_world@Vector(v) for v in o.bound_box])
        obstacles.append((o.name,rectangle(lo,hi,Matrix.Identity(4))))
poses={}; mins={'vehicles':(1e9,None),'buildings':(1e9,None)};collisions=[];stats={}
for i,pair in roots.items():
    poses[i]=[]
    phase=1 if i==2 else a.phase
    for f in range(N+1):
        t=phase+f*rates[i]
        assert t<=1153,'Proof may not cross an unqualified source seam'
        poses[i].append([matrix(o,t) for o in pair])
    path=[p[0].translation for p in poses[i]]
    speeds=[(q-p).length*fps for p,q in zip(path,path[1:])]
    stats[i]={'source_phase':phase,'source_rate':rates[i],'mean_scene_units_per_second':sum(speeds)/len(speeds),'speed_range':[min(speeds),max(speeds)],'distance_8_seconds':sum(speeds)/fps,'start_xyz':list(path[0]),'end_xyz':list(path[-1]),'independent_period_seconds':1152/fps/rates[i]}
for f in range(N):
    rects={i:[rectangle(*local[o.name],m) for o,m in zip(pair,poses[i][f])] for i,pair in roots.items()}
    for i in roots:
        for j in roots:
            if j<=i:continue
            gap=min(separation(p,q) for p in rects[i] for q in rects[j])
            if gap<mins['vehicles'][0]:mins['vehicles']=(gap,{'frame':f+1,'trucks':[i,j]})
            if gap<=0:collisions.append({'frame':f+1,'trucks':[i,j],'envelope_overlap':gap})
        for name,q in obstacles:
            gap=min(separation(p,q) for p in rects[i])
            if gap<mins['buildings'][0]:mins['buildings']=(gap,{'frame':f+1,'truck':i,'building':name})
            if gap<=0:collisions.append({'frame':f+1,'truck':i,'building':name,'envelope_overlap':gap})
report={'source':bpy.data.filepath,'proof_frames':[1,N],'proof_seconds':N/fps,'fps':fps,'stats':stats,'minimum_separating_axis_clearance_scene_units':mins,'envelope_overlaps':collisions,'obstacle_count':len(obstacles),'method':'Conservative XY rectangles of all visible truck mesh bounds, separately tractor/trailer; pairwise and major architecture every rendered proof frame. Smoke excluded. Positive gap guarantees disjoint envelopes; street furniture and exact swept subframes not qualified. Both truck roots sampled at identical source time.','loop_status':'8-second excerpt is not seamless. Independent route periods differ; full least-common loop collisions not qualified.'}
(P/'motion-analysis.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='envelope_overlaps'},indent=2));print('OVERLAPS',len(collisions),collisions[:4])
if a.apply:
    assert not collisions, 'Refusing to save overlapping proof'
    for i,pair in roots.items():
        for j,o in enumerate(pair):
            o.animation_data_clear()
            previous=None
            for f,pose in enumerate(poses[i]):
                loc,quat,scale=pose[j].decompose()
                rot=quat.to_euler('XYZ',previous) if previous else quat.to_euler('XYZ')
                previous=rot.copy();o.location=loc;o.rotation_euler=rot
                o.keyframe_insert('location',frame=f+1);o.keyframe_insert('rotation_euler',frame=f+1)
            for fc in channels(o):
                for key in fc.keyframe_points:key.interpolation='LINEAR'
    s.frame_start=1;s.frame_end=N;s.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(a.output).resolve()))
