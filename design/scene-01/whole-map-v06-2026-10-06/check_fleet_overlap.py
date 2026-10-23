import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;s=bpy.context.scene
roots={i:[bpy.data.objects[f'truck-{i}-{part}'] for part in ['tractor','trailer']] for i in range(1,5)}
def hull(points):
    ps=sorted(set(points))
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    lower=[];upper=[]
    for p in ps:
        while len(lower)>1 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
        lower.append(p)
    for p in reversed(ps):
        while len(upper)>1 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]
def shape(root):
    pts=[]
    for o in root.children_recursive:
        if o.type!='MESH' or o.hide_render:continue
        for b in o.bound_box:
            v=o.matrix_world@Vector(b);pts.append((v.x,v.y))
    return hull(pts)
def intersects(a,b):
    for poly in [a,b]:
        for p,q in zip(poly,poly[1:]+poly[:1]):
            axis=(-(q[1]-p[1]),q[0]-p[0])
            pa=[x*axis[0]+y*axis[1] for x,y in a];pb=[x*axis[0]+y*axis[1] for x,y in b]
            if max(pa)<=min(pb) or max(pb)<=min(pa):return False
    return True
hits=[]
for f in range(1,1153):
    s.frame_set(f);shapes={i:[shape(r) for r in rs] for i,rs in roots.items()}
    for i in range(1,5):
        for j in range(i+1,5):
            if any(intersects(a,b) for a in shapes[i] for b in shapes[j]):hits.append({'frame':f,'seconds':(f-1)/24,'pair':[i,j]})
receipt={'frames':1152,'method':'Conservative convex ground footprints from visible mesh bounding boxes; SAT over tractor and trailer separately','truck_truck_overlap_candidates':hits,'limitations':'World geometry only; does not certify rendered illustrated-building registration, close-up style, or mirror clearance.'}
(P/'fleet-overlap-v07.json').write_text(json.dumps(receipt,indent=2));print('Overlap candidates',len(hits),hits[:5])
