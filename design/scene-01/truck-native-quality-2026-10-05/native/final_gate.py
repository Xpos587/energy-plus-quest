import bpy,pathlib,json
from mathutils import Vector
P=pathlib.Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05');O=P/'native';bpy.ops.wm.open_mainfile(filepath=str(O/'scania-assembled-v2.blend'));s=bpy.context.scene
bpy.data.objects['SCANIA open windshield and sidewindow frame'].location.y+=18
bpy.data.objects['SCANIA sculpted upper front grille'].location.y+=5
for side in [-1,1]:
 old=bpy.data.objects.get('Interior detailed seat '+str(side));bpy.data.objects.remove(old,do_unlink=True);bpy.ops.wm.stl_import(filepath=str(P/'sources/scania-r730-paolo/r730-39.stl'));o=bpy.context.object;o.name='Interior upright upholstered seat '+str(side)
 for v in o.data.vertices:x,y,z=v.co;v.co=(x-14.66+side*26,12-z,z*0+y+88)
 o.data.materials.append(bpy.data.materials['Seat textile muted blue'])
 for p in o.data.polygons:p.use_smooth=True
for k,side in [(30,-1),(62,1)]:
 bpy.ops.wm.stl_import(filepath=str(P/f'sources/scania-r730-paolo/r730-{k}.stl'));o=bpy.context.object;o.name='Curved headlamp lens '+str(side)
 for v in o.data.vertices:x,y,z=v.co;v.co=(side*43+x-9.5,-53-z,22+y)
 o.data.materials.append(bpy.data.materials['Warm white trim'])
 for p in o.data.polygons:p.use_smooth=True
# Actual archived native chassis, separately scaled to fit rear running gear.
p='/home/michael/Github/energy-plus-quest/design/scene-01/painted-layer-2026-10-05/painted-vehicles-driver-fixed-optimized.blend'
with bpy.data.libraries.load(p,link=False) as (f,t):t.objects=['REPAIRED 1 detailed archived chassis']
o=t.objects[0];o.parent=None;o.matrix_world.identity();bpy.context.collection.objects.link(o);o.name='Detailed native archived rear chassis fitted to Scania'
vs=[v.co.copy() for v in o.data.vertices];lo=Vector(tuple(min(v[j] for v in vs) for j in range(3)));hi=Vector(tuple(max(v[j] for v in vs) for j in range(3)))
for v in o.data.vertices:
 x,y,z=v.co;v.co=((y-(lo.y+hi.y)/2)*60,(x-lo.x)/(hi.x-lo.x)*145+62,(z-lo.z)/(hi.z-lo.z)*41+12)
o.data.materials.clear();o.data.materials.append(bpy.data.materials['Medium slate grille'])
for poly in o.data.polygons:poly.material_index=0
# moderate green and large diffuse illumination preserved
s.cycles.samples=32
c=bpy.data.objects['shape-gate-front-three-quarter'];s.camera=c;s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.filepath=str(O/'shape-gate-assembled-v3.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-native-shape-gate.blend'));bpy.ops.render.render(write_still=True)
# approved one-model orthographic inspection
for name in ['orthographic-front','orthographic-side','map-heading-0','map-heading-120','map-heading-240']:
 s.camera=bpy.data.objects[name];s.render.resolution_x=900 if name=='orthographic-front' else 1200 if name=='orthographic-side' else 640;s.render.resolution_y=900 if name=='orthographic-front' else 800 if name=='orthographic-side' else 640;s.render.filepath=str(O/(name+'-v3.png'));bpy.ops.render.render(write_still=True)
(O/'FINAL-RECEIPT.md').write_text('''# Actual native Scania shape candidate\n\nSource: Paolo Scania R730, Printables 1396992, CC BY 4.0. See ../sources/SOURCE-RECEIPT.md. The PDF is an automatically generated 9-page listing, no exploded assembly instructions.\n\nThis is an approximate visual reconstruction from print-oriented STL parts, not a verified mechanical kit assembly. Current scene uses source curved cab 1 (Z-up, transformed x-55,50-y,z+42), lower cab8 (Y-up x-53.2,27-z,y), roof46(Y-up x-54.3,50-z,y+53), windowframe31(Z-up x-53.35,-9-y,z+88), sculpted grilles10/11, mirrors33/47, source39 upright interior seats, clean source2 tires and18 rims repeated for all three axles. Source3/20 rear parts had print/support geometry unsuitable for this assembly, so clean front source meshes substituted. Curved source30/62 headlamp lenses. Rear mudguards12/40 retain detailed source mesh, remapped X length, Y height, Z width. Frame6 removed from render due unsupported source orientation. Native archived detailed chassis appended from painted-vehicles-driver-fixed-optimized.blend, transformed to rear bounds xwidth~78mm, y62..207mm, z12..53mm.\n\nNo UV box; no image backdrop; all geometry rendered directly in Blender. No animation, other vehicles, or game integration.\n\nRender: Blender5.2.2 Cycles CPU,32samples, denoise, Standard view, exposure0, gamma1. Green body base linear .18,.33,.22; roughness.88, specular.12. Grille .21,.29,.30; tire .18,.21,.21. Two broad area lights, energy880000/480000 and size250/210mm, worldstrength.65. No outlines.\n\nCameras: shape-gate-front-three-quarter (-260,-340,235), target(0,37,87), ortho350mm,1400x1050. Front(0,-400,94), ortho205mm,900x900. Side(-500,72,94), ortho310mm,1200x800. Map headings(-280,-330,370),(370,220,370),(-230,390,370), target(0,65,65), ortho390mm,640x640. These map samples are shape tests, not verified game camera pixel sizing.\n\nCurrent gate still needs parent visual approval and seam cleanup if rejected. Open interior has two physical seats; occupants not yet inserted.\n''')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scania-native-shape-gate.blend'))
