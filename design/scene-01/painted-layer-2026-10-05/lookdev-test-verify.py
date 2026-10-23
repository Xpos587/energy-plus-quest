import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent

def snap():
 s=bpy.context.scene
 return {'objects':{o.name:{'type':o.type,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'verts':[list(v.co) for v in o.data.vertices] if o.type=='MESH' else None} for o in s.objects},'camera':s.camera.name,'poses':{str(f):capture(s,f) for f in (1,133,769,1153)}}
def capture(s,f):
 s.frame_set(f);return {o.name:[list(o.location),list(o.rotation_euler)] for o in s.objects if o.name.startswith('truck-')}
a=snap();bpy.ops.wm.open_mainfile(filepath=str(p/'lookdev-test-detail.blend'));b=snap()
r={'all_object_geometry_local_transforms_visibility_parenting_equal':a['objects']==b['objects'],'camera_equal':a['camera']==b['camera'],'selected_root_pose_frames_equal':a['poses']==b['poses'],'checked_frames':[1,133,769,1153]}
(p/'lookdev-test-verification.json').write_text(json.dumps(r,indent=2));print(r)
