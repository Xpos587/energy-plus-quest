import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'fleet-readable-v15-2026-10-07/fleet-v15-readable.blend'))
s=bpy.context.scene;s.frame_set(1)
oldm={m.name:m for m in bpy.data.materials}
with bpy.data.libraries.load(str(P.parent/'fleet-clean-v13-2026-10-07/fleet-v13-clean.blend'),link=False) as (a,b):b.objects=[f'V02 DETAILED {i} complete tractor' for i in (1,4)]
keep=('alloy rim','central hub','clean fuel tank','continuous chassis','fifth wheel support','frame crossmember','rear platform','recessed wheel bowl','rim vent','smooth rear wheelguard','tank strap','tire carcass','rolled wheel arch')
receipt=[]
for i,src in zip((1,4),b.objects):
 dst=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];root=dst.parent
 dst.data=src.data.copy()
 # Imported source contains the original windshield positions as well as exact approved UVs.
 for k,m in enumerate(dst.data.materials):
  base=m.name
  if base.endswith('.001') and base[:-4] in oldm:base=base[:-4]
  if base in oldm:dst.data.materials[k]=oldm[base]
 dst.data.materials[1]=oldm[f'V02 {i} Permanent high-detail two-driver windshield.001']
 t=root.matrix_world.inverted()@dst.matrix_world
 bm=bmesh.new();bm.from_mesh(dst.data);bad=[]
 for f in bm.faces:
  if f.material_index==1:continue
  pts=[t@v.co for v in f.verts]
  if any((p.x<.12 and p.z<1.30)or(p.x<1.37 and p.z<.90)for p in pts):bad.append(f)
 bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(dst.data);bm.free();dst.data.update()
 for o in root.children_recursive:
  if o.name.startswith(f'V14 {i} '):o.hide_render=not any(w in o.name for w in keep)
  if o.name.startswith(f'V15 {i} ') and 'connected exhaust plume' not in o.name:o.hide_render=True
 bpy.data.objects.remove(src,do_unlink=True)
 receipt.append({'truck':i,'restored_cab_vertices':len(dst.data.vertices),'crew_faces':sum(p.material_index==1 for p in dst.data.polygons),'removed_lower_faces':len(bad)})
# Remove high-contrast decorative roof treatments; structural curtain/box geometry stays.
for o in bpy.data.objects:
 if 'V15 ' in o.name and any(x in o.name for x in ('sewn canvas roof joint','ribbed rigid roof','roof transverse rib')):o.hide_render=True
# Reuse the v15 single-response correction without its save/output footer.
code=(P.parent/'fleet-readable-v15-2026-10-07/calibrate_light_once.py').read_text().split('bpy.ops.wm.save_as_mainfile')[0]
exec(compile(code,'calibrate_light_once','exec'))
P=Path(__file__).resolve().parent
# Restrained physical pigment wear: generated noise gives attached uneven patches on existing surfaces.
for i,color in ((1,(.56,.20,.12,1)),(4,(.73,.49,.16,1))):
 o=bpy.data.objects[f'V02 DETAILED {i} complete tractor'];m=o.data.materials[2].copy();m.name=f'V16 {i} aged detailed pigment';o.data.materials[2]=m;n=m.node_tree.nodes;l=m.node_tree.links
 tex=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=24;noise.inputs['Detail'].default_value=2.2;l.new(tex.outputs['Generated'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.55;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(.22,.22,.22,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
 for e in [x for x in n if x.type=='EMISSION']:
  source=e.inputs[0].links[0].from_socket if e.inputs[0].is_linked else None
  mix=n.new('ShaderNodeMixRGB');mix.inputs[2].default_value=color;l.new(ramp.outputs[0],mix.inputs[0])
  if source:l.new(source,mix.inputs[1])
  l.new(mix.outputs[0],e.inputs[0])
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'fleet-v16.blend'))
(P/'geometry-receipt.json').write_text(json.dumps({'source':'v15; old upper cabs restored from v13','restoration':receipt,'motion':'untouched; separate retime agent owns behavior','wear':'attached restrained material noise, no flat shell or decal mesh'},indent=2))
