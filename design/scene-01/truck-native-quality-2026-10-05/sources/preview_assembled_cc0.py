import bpy,math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/sources/cc0-cabover-sleeper-3dassets.glb')
pts=[o.matrix_world@Vector(p) for o in bpy.data.objects if o.type=='MESH' for p in o.bound_box]
lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)));center=(lo+hi)/2
bpy.ops.object.camera_add(location=center+Vector((8,-10,6)))
cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(hi-lo)*1.5;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=center+Vector((3,-4,8)));bpy.context.object.data.energy=1600;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=7
bpy.context.object.rotation_euler=(center-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.world=bpy.data.worlds.new('World');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(0.55,0.6,0.65,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.6
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=8;sc.render.resolution_x=640;sc.render.resolution_y=480;sc.render.resolution_percentage=100;sc.render.filepath='/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/sources/cc0-cabover-preview.png'
print('Measured geometry',sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH'), 'polygons', 'bounds',list(lo),list(hi))
bpy.ops.render.render(write_still=True)
