"""Bounded coherent tractor repair; no native animation/camera/route changes."""
import bpy,json,math
from pathlib import Path
O=Path(__file__).resolve().parent;D=Path('/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-21-live/atlas');R=O/'repaired-stills';R.mkdir(exist_ok=True);s=bpy.context.scene
receipt=[]
for i,family in ((1,'old-cab'),(2,'near-cab'),(3,'crew-cab'),(4,'old-cab')):
 root=bpy.data.objects[f'truck-{i}-tractor'];cab=next(o for o in root.children if 'reconstructed' in o.name)
 # Preserve archive mesh as one fitted tractor instead of thinning its native rear hardware.
 cabtop=max(v.co.z for v in cab.data.vertices);target_top={1:2.95,2:2.95,3:3.08,4:2.52}[i]
 zfactor=(target_top-.08)/(cabtop-.08)
 upperrear=min(v.co.x for v in cab.data.vertices if v.co.z>1);shift=-.85-upperrear
 for v in cab.data.vertices:v.co.x+=shift;v.co.z=.08+(v.co.z-.08)*zfactor
 cab.data.update()
 # Match the archived rear chassis through the same source-to-cab mapping.
 with bpy.data.libraries.load(str(D/f'{family}.blend'),link=False) as (src,dst):dst.objects=['Mesh_0.001']
 rear=dst.objects[0];s.collection.objects.link(rear);rear.name=f'REPAIRED {i} detailed archived chassis';rear.parent=root;rear.location=(0,0,0);rear.rotation_euler=(0,0,0);rear.scale=(1,1,1);rear.animation_data_clear();rear.hide_render=False
 source_min={1:-1.3458664417,2:-1.0349359512,3:-1.0349359512,4:-1.3458664417}[i]
 source_cab_top={1:2.65,2:2.78,3:3.08,4:2.65}[i]
 source_cab_min_z={1:.0977141038,2:.06,3:.06,4:.0977141038}[i]
 source_cab_length=1.65-source_min;xfactor=2.61426*.85/source_cab_length;yfactor=2.0196*.85/2.26
 for v in rear.data.vertices:
  v.co.x=(v.co.x-source_min)*xfactor-1.025+shift
  v.co.y*=yfactor
  v.co.z=.08+(v.co.z-source_cab_min_z)*(target_top-.08)/(source_cab_top-source_cab_min_z)
 rear.data.update()
 # Cab and rear share the already brightened projected materials and packed textures.
 rear.data.materials.clear()
 for m in cab.data.materials:rear.data.materials.append(m)
 # Rear tyre/rim geometry comes from archive once; preserve native fifth-wheel plate only.
 for obj in root.children_recursive:
  if obj in (cab,rear):continue
  if obj.name.startswith('PILOT') and 'driver' in obj.name and i==2:continue
  if obj.name==f'{i} windshield' and i==2:continue
  if obj.type in ('MESH','FONT'):obj.hide_render=obj.name!=f'{i} fifth wheel'
 # Existing fifth-wheel disc covers native trailer root pivot; make its supporting deck coherent.
 metal=bpy.data.materials['PILOT soft slate fittings']
 bpy.ops.mesh.primitive_cube_add(size=1)
 deck=bpy.context.object;deck.name=f'REPAIRED {i} fifth wheel support deck';deck.parent=root;deck.location=(-1.94,0,.85);deck.scale=(1.40,1.12,.20);deck.data.materials.append(metal)
 bevel=deck.modifiers.new('gentle deck edge','BEVEL');bevel.width=.045;bevel.segments=2
 # Blue's one-driver glazing and relief follow the same cab shift/height correction.
 if i==2:
  for obj in root.children:
   if obj.name=='2 windshield' or ('PILOT 2 driver' in obj.name):
    obj.location.x+=shift;obj.location.z=.08+(obj.location.z-.08)*zfactor;obj.scale.z*=zfactor
 receipt.append({'truck':i,'cab_shift_x_m':shift,'cab_height_factor':zfactor,'cab_top_z_m':target_top,'upper_cab_rear_x_target_m':-.85,'rear_chassis':'matching archived mesh; native duplicate rear wheels/tanks/ladder hidden','native_fifth_wheel':'retained at x=-2.3 covering trailer pivot -2.5806','support_deck_bounds_x':[-2.64,-1.24]})
crypto=next(n for n in s.compositing_node_group.nodes if n.type=='CRYPTOMATTE_V2');objects=[]
for root in [o for o in s.objects if o.name.startswith('truck-')]:objects.extend(o for o in root.children_recursive if o.type in ('MESH','FONT') and not o.hide_render)
crypto.matte_id=', '.join(o.name for o in objects)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(O/'painted-vehicles-repaired.blend'))
for f in (1,133,169,769):s.frame_set(f);s.render.filepath=str(R/f'{f:04}.png');bpy.ops.render.render(write_still=True)
(O/'repaired-geometry-receipt.json').write_text(json.dumps({'frames':[1,133,169,769],'dimensions':[1280,889],'routes_and_camera':'unchanged','repairs':receipt,'limitations':['Matching archived chassis wheelbase now replaces generic native rear running gear; still-only verification.','Projected texture detail and very small faces remain departures from final approved truck cards.','No full animation render.']},indent=2))
