import bpy,json
from pathlib import Path
s=bpy.context.scene;cab=bpy.data.objects['PILOT 2 reconstructed near-cab'];g=bpy.data.objects['2 windshield'];root=cab.parent;s.frame_set(769);bpy.context.view_layer.update();print('OPAQUE_GLASS',[(list(root.matrix_world.inverted()@(g.matrix_world@v.co))) for v in g.data.vertices]);print('HEAD',[(o.name,list(o.location),list(o.scale)) for o in root.children if 'driver' in o.name])
for idx in (1181,1153,926):
 f=cab.data.polygons[idx];print('FACE',idx,'normal',list(f.normal),'verts',[list(cab.data.vertices[v].co) for v in f.vertices])
# Imported front-side skin locations at each height: exact candidate windshield fit.
for z in (1.7,1.9,2.1,2.3,2.5):
 faces=[f for f in cab.data.polygons if f.normal.x>.5 and abs(f.center.z-z)<.1];print('FRONT',z,'bounds',[(min(f.center[a] for f in faces),max(f.center[a] for f in faces)) for a in (0,1)] if faces else '')
