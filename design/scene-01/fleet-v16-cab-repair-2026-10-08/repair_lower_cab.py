"""Restore only the clipped lower cab skirt and its formed wheel-well return."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parent
SOURCE=P.parent/'fleet-v16-worn-motion-2026-10-08/fleet-v16-worn-motion.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
changed=[];created=[]
for i in (1,4):
 root=bpy.data.objects[f'truck-{i}-tractor'];group=bpy.data.objects[f'WORN {i} isolated cab suspension'];paint=bpy.data.materials[f'V14 {i} painted body']
 for side in (-1,1):
  hidden=bpy.data.objects[f'V14 {i} formed side cab {side}']
  # Keep only its lower manufactured profile. The detailed upper cab is untouched.
  profile=[]
  for j,v in enumerate(hidden.data.vertices):
   x,z=v.co.x,min(v.co.z,1.07)
   if 6<=j<=19:
    angle=math.atan2(v.co.z-.355,v.co.x-.8);x=.8+.49*math.cos(angle);z=.355+.49*math.sin(angle)
   x=min(1.66,max(.30,x))
   y=.962-.062*max(0,min(1,(z-.88)/.19))-.38*max(0,x-1.40)
   point=(x,side*y,z)
   if not profile or Vector(point)!=Vector(profile[-1]):profile.append(point)
  mesh=bpy.data.meshes.new(f'Restored lower cab profile {i} {side}');mesh.from_pydata(profile,[],[tuple(range(len(profile)))]);mesh.update()
  ob=bpy.data.objects.new(f'CABREPAIR {i} continuous lower cladding {side}',mesh);s.collection.objects.link(ob);ob.parent=group;ob.location=(-.8,0,-.9);mesh.materials.append(paint)
  if side==-1:
   for poly in mesh.polygons:poly.flip()
  solid=ob.modifiers.new('Formed panel thickness inward','SOLIDIFY');solid.thickness=.028;solid.offset=-1
  bevel=ob.modifiers.new('Rolled skirt edge','BEVEL');bevel.width=.012;bevel.segments=3
  ob.modifiers.new('Broad panel normals','WEIGHTED_NORMAL');created.append(ob.name)
  # The flange turns inward around the opening, avoiding a free-floating flat patch.
  vs=[];fs=[]
  for k in range(33):
   angle=math.pi*k/32
   for y in (side*.962,side*.76):vs.append((.8+.49*math.cos(angle),y,.355+.49*math.sin(angle)))
  for k in range(32):fs.append((2*k,2*k+1,2*k+3,2*k+2))
  me=bpy.data.meshes.new('Contoured wheel well return');me.from_pydata(vs,[],fs);me.update();well=bpy.data.objects.new(f'CABREPAIR {i} formed wheel well return {side}',me);s.collection.objects.link(well);well.parent=group;well.location=(-.8,0,-.9);me.materials.append(paint)
  for poly in me.polygons:poly.use_smooth=True
  thick=well.modifiers.new('Pressed wheel well thickness','SOLIDIFY');thick.thickness=.012
  created.append(well.name)
  # Existing rolled lip follows the cab rather than separating when suspension rises.
  for o in [o for o in root.children if o.name.startswith(f'V14 {i} rolled wheel arch {side} ')]:
   local=o.matrix_local.copy();loc=local.translation;loc.x=.8+(loc.x-.8)*(.49/.425);loc.z=.355+(loc.z-.355)*(.49/.425);local.translation=loc
   o.parent=group;o.matrix_parent_inverse=Matrix.Translation(Vector((-.8,0,-.9)));o.matrix_basis=local;o.scale.z*=.49/.425;o.scale.x*=.75;o.scale.y*=.75;changed.append(o.name)
s.frame_set(96);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v16-cab-repair.blend'))
(P/'geometry-change-receipt.json').write_text(json.dumps({'source':str(SOURCE),'root_cause':'v16 lower shell faces were clipped below z .90; replacement side profiles hidden, leaving open strip above isolated front tire lips; cab shake increased separation','created':created,'reparented_arch_lips':changed,'upper_cab_mesh_materials_and_crew':'untouched','suspension_actions':'untouched','new_wheel_opening_radius_local':.49,'lower_cladding_upper_overlap_z':1.07,'wheels_chassis_hitch_stacks_smoke':'untouched'},indent=2))
