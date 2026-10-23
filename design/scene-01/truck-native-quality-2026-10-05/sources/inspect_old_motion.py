import bpy,json
from mathutils import Vector
from pathlib import Path
scene=bpy.context.scene
rows=[]
for o in scene.objects:
    row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'dimensions':list(o.dimensions),'matrix_world':[list(r) for r in o.matrix_world],'constraints':[{'type':c.type,'name':c.name,'target':getattr(getattr(c,'target',None),'name',None)} for c in o.constraints]}
    if o.type=='MESH':
        pts=[o.matrix_world@Vector(p) for p in o.bound_box]
        row['world_bounds']={'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
        row['materials']=[m.name if m else None for m in o.data.materials]
    if o.animation_data:
        row['action']=o.animation_data.action.name if o.animation_data.action else None
        row['drivers']=[{'path':f.data_path,'index':f.array_index,'expression':f.driver.expression} for f in o.animation_data.drivers]
    rows.append(row)
actions=[]
for a in bpy.data.actions:
    curves=[]
    try: fs=a.fcurves
    except AttributeError:
        fs=[f for l in a.layers for s in l.strips if s.type=='KEYFRAME' for bag in s.channelbags for f in bag.fcurves]
    for f in fs: curves.append({'path':f.data_path,'index':f.array_index,'keys':[[k.co.x,k.co.y,k.interpolation] for k in f.keyframe_points]})
    actions.append({'name':a.name,'range':list(a.frame_range),'curves':curves})
report={'file':bpy.data.filepath,'frame':scene.frame_current,'range':[scene.frame_start,scene.frame_end],'fps':scene.render.fps,'camera':scene.camera.name if scene.camera else None,'objects':rows,'actions':actions}
Path('/home/michael/Github/energy-plus-quest/design/scene-01/truck-native-quality-2026-10-05/sources/old-motion-inspection.json').write_text(json.dumps(report,indent=2))
print('SCENE',report['frame'],report['range'],report['fps'],report['camera'])
for r in rows:
    print(r['name'],r['type'],'parent=',r['parent'],'loc=',[round(v,3) for v in r['location']],'scale=',[round(v,3) for v in r['scale']],'dim=',[round(v,3) for v in r['dimensions']],'action=',r.get('action'),'mats=',r.get('materials'))
print('ACTIONS',json.dumps(actions))
