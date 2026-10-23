import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
s=bpy.context.scene
before={'camera':s.camera.name,'camera_matrix':[list(r) for r in s.camera.matrix_world],'resolution':[s.render.resolution_x,s.render.resolution_y], 'taa':s.eevee.taa_render_samples,'engine':s.render.engine,'frame_end':s.frame_end,'objects':len(s.objects),'collections':[c.name for c in bpy.data.collections]}
textures=[]
for image in bpy.data.images:
 if image.source=='FILE':
  path=Path(bpy.path.abspath(image.filepath)).resolve();textures.append({'name':image.name,'path':str(path),'exists':path.exists(),'packed':bool(image.packed_file)})
  if not image.packed_file and not path.exists():raise RuntimeError('Missing texture: '+str(path))
  image.filepath=str(path)
s.render.resolution_x=3840;s.render.resolution_y=2668;s.render.resolution_percentage=100
s.eevee.taa_render_samples=8;s.eevee.volumetric_samples=32
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'v22-4k-source.blend'))
(P/'source-receipt.json').write_text(json.dumps({'source':'../../fleet-v21-coupling-geometry-2026-10-09/v21-compact-trailer.blend','before':before,'textures':textures,'after':{'resolution':[3840,2668],'taa':8,'volume_samples':32}},indent=2))
print('SOURCE_READY',json.dumps(before),flush=True)
