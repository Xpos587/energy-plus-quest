from pathlib import Path
import bpy,hashlib,json
root=Path.cwd()
bpy.ops.wm.open_mainfile(filepath=str(root/'design/scene-04/blender-v4/quay.blend'))
before=json.loads((root/'.tmp-work/scene4-final-render/proof/geometry-check.json').read_text())['objects']
after={o.name:{'type':o.type,'matrix':[list(v) for v in o.matrix_world], 'mesh':hashlib.sha256(json.dumps({'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]}).encode()).hexdigest() if o.type=='MESH' else None, 'ortho':o.data.ortho_scale if o.type=='CAMERA' else None} for o in bpy.data.objects}
assert before==after,[k for k in set(before)|set(after) if before.get(k)!=after.get(k)]
scene=bpy.context.scene
assert scene.camera.name=='wide'
assert len(bpy.data.cameras)==4
assert scene.eevee.taa_render_samples==128
assert (scene.render.resolution_x,scene.render.resolution_y)==(3884,1618)
barge=bpy.data.collections['Barge - approved geometry']
assert len(barge.objects)==12 and all(o.get('quay_group')=='barge' for o in barge.objects)
assert all(o.hide_render for o in scene.objects if o.get('quay_group','').startswith('o_'))
result={'identical_geometry_and_cameras':True,'objects':len(after),'cameras':len(bpy.data.cameras),'barge_objects':len(barge.objects),'samples':128,'scale':2,'source':'design/scene-04/blender-v4/quay.py','blend':'design/scene-04/blender-v4/quay.blend'}
(root/'.tmp-work/scene4-final-render/master-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print('MASTER VERIFIED',json.dumps(result))
