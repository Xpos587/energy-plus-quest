import bpy
from mathutils import Vector
r=bpy.data.objects['truck-4-tractor']
for o in r.children_recursive:
 if o.type=='MESH' and not o.hide_render:print(o.name)
