import bpy, json
from pathlib import Path
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'maz500-isolated-study.blend'))
result=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    parents=list(range(len(pts)))
    def root(x):
        while parents[x]!=x:
            parents[x]=parents[parents[x]]
            x=parents[x]
        return x
    for e in o.data.edges:
        a,b=e.vertices
        parents[root(a)]=root(b)
    groups={}
    for i in range(len(pts)): groups.setdefault(root(i),[]).append(i)
    components=[]
    for indices in groups.values():
        lo=[min(pts[i][a] for i in indices) for a in range(3)]
        hi=[max(pts[i][a] for i in indices) for a in range(3)]
        components.append({'vertices':len(indices),'bounds':[lo,hi]})
    result.append({'object':o.name,'bounds':[[min(p[a] for p in pts) for a in range(3)],[max(p[a] for p in pts) for a in range(3)]],'components':components})
(OUT/'component-inspection.json').write_text(json.dumps(result,indent=2))
for entry in result:
    print(entry['object'],len(entry['components']),entry['bounds'])
