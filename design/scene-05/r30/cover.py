"""Project native art bounds through the unselected lastmile stage without changing WorldArt.tsx.
Stage sizes: measured runtime rectangles at the four requested CSS viewports (review/runtime.json).
"""
STAGES = {'tall': [((412,915),(412,596.84375)),((1024,1366),(704,1302))],
          'wide': [((1920,1080),(1520,1016)),((2560,1080),(2160,1016))]}


def offset(stage, plane, lo, hi):
    centre=(stage-plane)/2
    if plane<=stage: return centre
    lower=max(stage-plane,8-lo); upper=min(0,stage-8-hi)
    return max(lower,min(upper,centre)) if lower<=upper+.5 else centre


def crops(view, size, framing, boxes):
    W,H=size; l,t,r,b=framing; result={}
    for viewport,stage in STAGES[view]:
        w,h=stage; top=56 if w<=420 else 64
        scale=max(w/W,h/H,min((w-16)/(r-l),(h-top-16)/(b-t)))
        dx=offset(w,W*scale,l*scale,r*scale);dy=max(h-H*scale,min(0,top+offset(h-top,H*scale,t*scale,b*scale)))
        area=[-dx/scale,-dy/scale,(w-dx)/scale,(h-dy)/scale]
        # Also check a plain centered cover at the *whole viewport*, independent of stage furniture.
        vw,vh=viewport;s=max(vw/W,vh/H); x=(W-vw/s)/2;y=(H-vh/s)/2;center=[x,y,W-x,H-y]
        def outside(rect):return [key for key,(x0,y0,x1,y1) in boxes.items() if x0<rect[0] or y0<rect[1] or x1>rect[2] or y1>rect[3]]
        result['%dx%d'%viewport]={'stage':list(stage),'nativeStageCrop':[round(a,2) for a in area],'clipped':outside(area),'nativeViewportCover':[round(a,2) for a in center],'viewportClipped':outside(center)}
    return result
