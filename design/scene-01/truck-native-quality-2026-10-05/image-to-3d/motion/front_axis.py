import bpy
p='/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/image-to-3d/green-tractor-finished.blend';bpy.ops.wm.open_mainfile(filepath=p);o=bpy.data.objects['Mesh_0'];im=next(n.image for n in o.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE');pix=list(im.pixels);w,h=im.size;uv=o.data.uv_layers.active.data;counts=[0,0];sums=[0,0]
for poly in o.data.polygons:
 li=poly.loop_indices[0];u,v=uv[li].uv;j=(int(v*(h-1))*w+int(u*(w-1)))*4;r,g,b=pix[j:j+3];co=o.matrix_world@o.data.vertices[poly.vertices[0]].co
 c=0 if g>1.3*r and g>1.3*b and g>.12 else 1;counts[c]+=1;sums[c]+=co.x
print('green/non green meanX',[sums[i]/counts[i] for i in range(2)],'matrix',o.matrix_world)
