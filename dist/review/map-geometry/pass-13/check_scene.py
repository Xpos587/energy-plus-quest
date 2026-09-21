"""Run with Blender --background --python check_scene.py -- path/to/scene.blend."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
P = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index('--') + 1])
s = bpy.context.scene
s.frame_set(1)
def objects(prefix): return [o for o in s.objects if o.name.startswith(prefix)]
def bounds(o, vertices=None):
    v = [o.matrix_world @ Vector(p) for p in (vertices if vertices is not None else o.bound_box)]
    return [[min(p[i] for p in v) for i in range(3)], [max(p[i] for p in v) for i in range(3)]]
def separated(a, b, axes=(0,2), gap=0):
    return any(a[1][i] + gap <= b[0][i]+1e-5 or b[1][i]+gap <= a[0][i]+1e-5 for i in axes)
failures=[]
def check(ok, message):
    if not ok: failures.append(message)
rooflights=objects('warehouse rooflight curb')
check(len(objects('warehouse air handling unit'))==2,'Exactly two HVAC units required')
check(len(rooflights)==6, 'Six skylights required')
for o in objects('warehouse air handling unit'):
    b=bounds(o)
    check(all(separated(b,bounds(r),(0,1),.5) for r in rooflights), o.name+': maintenance gap <0.5m')
    check(b[0][0]>=-21.425 and b[1][0]<=-6.575 and b[0][1]>=8.075 and b[1][1]<=20.925,o.name+': parapet maintenance clearance <0.5m')
check(not objects('residential loggia band') and not objects('loggia glass railing'),'Four incompatible loggia levels remain')
for prefix,building,lo,hi in [('retail glazing','retail street frontage',5.25,22.75),('business center glazing','south business center',6,22)]:
    panes=objects(prefix);entry=bounds(bpy.data.objects[building+' entry'])
    for i,o in enumerate(panes):
        b=bounds(o)
        check(b[0][0]>=lo+.1 and b[1][0]<=hi-.1, o.name+': wall overrun')
        check(separated(b,entry,(0,),.2),o.name+': door bay overlap')
        check(b[1][2]<=2.65, o.name+': storefront exceeds ground floor')
        check(all(separated(b,bounds(other),(0,),.1) for other in panes[i+1:]),o.name+': adjacent panel overlap')
        # Batched facade cubes contain eight vertices EACH; never test the entire mesh bounds.
        upper=bpy.data.objects[building+' window glazing']
        verts=upper.data.vertices
        for start in range(0,len(verts),8):
            component=bounds(upper,[v.co for v in verts[start:start+8]])
            if component[0][1]<entry[1][1]+.1:
                check(separated(b,component,(0,2),.1),o.name+': component window overlap')
for o in objects('crosswalk'):
    x,y=o.location[:2]
    check(not (abs(x)<3.5 and any(abs(y-v)<.01 for v in (-19,-17,1))), 'Unusable warehouse-facing crossing remains')
ys={round(o.location.y,3) for o in objects('crosswalk') if abs(o.location.x-28)<3.5 and -22<o.location.y<-14}
check(ys=={-18},'East-road duplicate zebras not consolidated')
check(len(objects('warehouse loading door'))==6,'Loading door count changed')
check(len(objects('dock bay boundary'))==7,'Bay boundary count changed')
check(len(objects('crossing ramp'))==48,'Expected local curb transitions at all retained crossings')
for ramp in objects('crossing ramp'):
    b=bounds(ramp)
    check(b[0][2]<=.03 and .15<=b[1][2]<=.161,ramp.name+': ramp does not connect street to sidewalk')
# The changed crossing's two 1.3m landings must also clear individual furniture cubes.
landings=[[[22.75,-18.9,0],[24.05,-17.1,2]],[[31.95,-18.9,0],[33.25,-17.1,2]]]
for prefix in ('street lamp poles and arms','street lamp luminaires'):
    for furniture in objects(prefix):
        verts=furniture.data.vertices
        for start in range(0,len(verts),8):
            b=bounds(furniture,[v.co for v in verts[start:start+8]])
            if b[0][2]<2:
                check(all(separated(b,landing,(0,1),.1) for landing in landings),'Street furniture obstructs changed crossing landing')

check(len(objects('crew seated head'))==2,'Two seated crew required')
check(bpy.data.objects['truck-3-tractor'].rotation_euler.z<0,'Crew windshield faces away from camera')
result={'passed':not failures,'failures':failures,'scene':bpy.data.filepath}
print(json.dumps(result,indent=2))
if failures: raise AssertionError('; '.join(failures))
(P/'scene-check.json').write_text(json.dumps(result,indent=2))
