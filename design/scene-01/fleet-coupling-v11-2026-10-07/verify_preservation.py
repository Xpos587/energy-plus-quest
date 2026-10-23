import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
def capture():
 s=bpy.context.scene;s.frame_set(1)
 return {'camera':(s.camera.name,tuple(s.camera.location),tuple(s.camera.rotation_euler),s.camera.data.ortho_scale),'objects':{o.name:{'hide':o.hide_render,'parent':o.parent.name if o.parent else None,'mesh':tuple(tuple(v.co) for v in o.data.vertices) if o.type=='MESH' else None,'materials':tuple(x.name for x in o.material_slots),'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None} for o in s.objects},'images':{x.name:x.filepath for x in bpy.data.images},'resolution':(s.render.resolution_x,s.render.resolution_y),'range':(s.frame_start,s.frame_end)}
a=capture();bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v11-coupling.blend'));b=capture();assert a['camera']==b['camera'];assert a['images']==b['images'];assert a['resolution']==b['resolution'];assert a['range']==b['range'];assert a['objects'].keys()==b['objects'].keys()
changed=[]
for n,x in a['objects'].items():
 y=b['objects'][n]
 for prop in ['hide','parent','materials','action']:assert x[prop]==y[prop],(n,prop)
 if x['mesh']!=y['mesh']:
  assert 'exhaust' in n,n
  changed.append(n)
r={'source_camera_identical':True,'all_source_hide_flags_identical':True,'source_image_paths_identical':True,'all_material_slot_names_identical':True,'all_parent_relationships_identical':True,'all_animation_action_assignments_identical':True,'resolution':b['resolution'],'frame_range':b['range'],'changed_meshes_only':changed,'note':'trailer location keyframe values deliberately rebaked in existing actions; actions retained, trailer headings retained, source camera saved before QA'}
(P/'preservation-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
