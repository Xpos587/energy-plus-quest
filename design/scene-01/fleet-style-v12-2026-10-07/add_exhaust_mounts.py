import bpy
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'fleet-v12-style.blend'))
for i in (1,4):
 stack=bpy.data.objects[f'{i} exhaust stack'];root=stack.parent;mat=bpy.data.materials[f'V12 {i} clean hardware']
 for z in (1.86,2.10):
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.085,depth=.065);o=bpy.context.object;o.name=f'V12 {i} exhaust visible clamp';o.parent=root;o.location=(stack.location.x,stack.location.y,z);o.data.materials.append(mat)
  bpy.ops.mesh.primitive_cube_add();o=bpy.context.object;o.name=f'V12 {i} exhaust cab mounting bracket';o.parent=root;o.location=(stack.location.x+.1,stack.location.y,z);o.scale=(.12,.055,.035);o.data.materials.append(mat)
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v12-style.blend'))
