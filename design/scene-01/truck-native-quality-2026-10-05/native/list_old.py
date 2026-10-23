import bpy
p='/home/michael/Github/energy-plus-quest/design/scene-01/painted-layer-2026-10-05/painted-vehicles-driver-fixed-optimized.blend'
with bpy.data.libraries.load(p,link=False) as (f,t):print('\n'.join(f.objects))
