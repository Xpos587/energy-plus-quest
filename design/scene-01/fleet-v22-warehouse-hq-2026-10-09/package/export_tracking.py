"""Read-only frame-matched normalized roof centers for the game loop."""
import json
import sys
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view

out = Path(sys.argv[sys.argv.index('--')+1]).resolve()
scene = bpy.context.scene
assert scene.render.fps / scene.render.fps_base == 24
anchors=[scene.objects[f'vehicle {i} identification'] for i in range(1,5)]
rows=[]
for frame in range(1,1538):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    row=[]
    for anchor in anchors:
        point=world_to_camera_view(scene,scene.camera,anchor.matrix_world.translation)
        row.append([float(point.x),float(1-point.y)])
    rows.append(row)
assert all(0<=v<=1 for row in rows for point in row for v in point)
seam=max(abs(a-b) for pa,pb in zip(rows[0],rows[-1]) for a,b in zip(pa,pb))
assert seam<1e-5,seam
out.write_text(json.dumps(rows[:-1],separators=(',',':'))+'\n')
receipt={'source':bpy.data.filepath,'frames':1536,'fps':24,'order':['old','near','crew','old4'],'colors':['red','blue','green','yellow'],'normalized_start_end_error':seam,'first':rows[0],'boundary':rows[-1],'anchors':[{'name':a.name,'parent':a.parent.name if a.parent else None,'local_location':list(a.location)} for a in anchors],'source_saved':False}
out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
