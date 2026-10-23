"""Source-only correction. No render calls; rebuild from delivered v20."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
SRC=P.parent/'fleet-v20-game-loop-2026-10-08/v20-game-loop.blend'
OUT=P/'v21-compact-trailer.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC));s=bpy.context.scene
N=s.frame_end
# Bring coupling forward by .55 local units; retain manoeuvring clearance.
SHIFT=.55;TRACK=.66
roots={i:(bpy.data.objects[f'truck-{i}-tractor'],bpy.data.objects[f'truck-{i}-trailer'])for i in range(1,5)}
positions={i:[] for i in roots}
for f in range(1,N+2):
 s.frame_set(f)
 for i,(t,r) in roots.items():
  positions[i].append(r.location.copy()+t.matrix_world.to_3x3()@Vector((SHIFT,0,0)))
for i,(t,r) in roots.items():
 for f,p in enumerate(positions[i],1):r.location=p;r.keyframe_insert('location',frame=f)
 for name in (f'{i} fifth wheel',f'REPAIRED {i} fifth wheel support deck',f'V14 {i} fifth wheel support platform'):
  bpy.data.objects[name].location.x+=SHIFT
 for o in list(r.children):
  if o.name.startswith(f'WHEEL steering {i} trailer'):
   o.location.y=math.copysign(TRACK,o.location.y)
  elif o.name.startswith(f'WHEEL axle {i} trailer'):
   # Cylinder length runs along its local Z, rotated into trailer Y.
   o.scale.z*= (TRACK-.05)/(.805-.05)
  elif o.name.startswith(f'WHEEL trailer crossmember {i}'):
   o.scale.z*=.86/.93
s.frame_set(1);bpy.context.view_layer.update()
rows=[]
for i,(t,r) in roots.items():
 wheels=[]
 for o in s.objects:
  if o.type!='MESH' or o.hide_render:continue
  parent=o.parent
  if parent and parent.name.startswith(f'WHEEL rotation {i} trailer'):
   wheels.extend(r.matrix_world.inverted()@o.matrix_world@Vector(c) for c in o.bound_box)
 outer=max(abs(p.y) for p in wheels)
 assert outer<.91,(i,outer)
 rows.append({'truck':i,'wheel_hardware_half_width_before':1.0,'wheel_hardware_half_width_after':outer,'wheel_center_half_track':TRACK,'coupling_local_x_before':-2.3,'coupling_local_x_after':-2.3+SHIFT})
# Check exact coupling at every frame plus body-front clearance from cab-back plane.
max_hitch_error=0.;minimum_gap=1e9
for f in range(1,N+2):
 s.frame_set(f);bpy.context.view_layer.update()
 for i,(t,r) in roots.items():
  hitch=t.matrix_world@Vector((-2.3+SHIFT,0,0))
  max_hitch_error=max(max_hitch_error,(hitch-r.matrix_world.translation).length)
  # Body front corners in tractor local coordinates: no cab-back penetration.
  front=[t.matrix_world.inverted()@r.matrix_world@Vector((.7,y,1.5)) for y in (-.997,.997)]
  minimum_gap=min(minimum_gap,-max(p.x for p in front))
assert max_hitch_error<.0003,max_hitch_error
s.frame_set(1);bpy.context.view_layer.update();start={r.name:r.matrix_world.copy()for t,r in roots.values()}
s.frame_set(N+1);bpy.context.view_layer.update();seam=max(abs(a-b)for t,r in roots.values()for ra,rb in zip(start[r.name],r.matrix_world)for a,b in zip(ra,rb))
assert seam<.0002,seam
s.frame_set(1)
s['geometry_revision']='v21: inward trailer wheels and forward fifth-wheel coupling; source only, not rendered'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
report={'source':str(SRC),'output':str(OUT),'rendered':False,'frames':N,'vehicles':rows,'max_hitch_position_error':max_hitch_error,'loop_boundary_matrix_error':seam,'minimum_trailer_front_distance_behind_tractor_origin':minimum_gap}
(P/'geometry-check.json').write_text(json.dumps(report,indent=2))
print('GEOMETRY_SAVED',json.dumps(report))
