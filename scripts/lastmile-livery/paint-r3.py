"""R3 curved fuselage paint; rollout.py applies the final dark-glass correction.
Requires original map + accepted generated shading reference, never public writes.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import cv2, numpy as np, json, sys
from geometry import pts


def main(workspace, originals):
    R = Path(workspace)
    B = Path(originals)
    orig=Image.open(B/'scene-art/lastmile-family-v1/revision-18/choice-wide-alva.webp').convert('RGB')
    a=np.array(orig);x0,y0,x1,y1=780,1690,870,1805;rgb=a[y0:y1,x0:x1].astype(float);h,w=rgb.shape[:2];yy,xx=np.mgrid[y0:y1,x0:x1];k=8
    # The original pane pixels, including their soft dark frames, not an orange cutout around them.
    glass=np.zeros((h,w),bool)
    for cx,cy,rx,ry in [(816,1735,9,13),(840,1731,10,14)]:
     glass|=(((xx-cx)/rx)**2+((yy-cy)/ry)**2<1)&(rgb.max(axis=2)<190)&(rgb.max(axis=2)-rgb.min(axis=2)<80)
    mask=Image.new('L',(w*k,h*k));ImageDraw.Draw(mask).polygon([((x-x0)*k,(y-y0)*k) for x,y in [(789,1710),(858,1697),(858,1741),(848,1771),(808,1796),(801,1794),(808,1769),(816,1753),(804,1736),(792,1721)]],fill=255)
    remove=np.array(mask.resize((w,h),Image.Resampling.LANCZOS))/255
    remove[glass]=0;remove[yy>=1795-.22*(xx-790)]=0
    # Continuous orange coating removes the old straight livery without preserving its jagged paint edge.
    orange=np.array([254.,78.,2.])[None,None,:]*np.clip(1-(yy-1700)*.0011,.86,1)[:,:,None]
    rgb=rgb*(1-remove[:,:,None])+orange*remove[:,:,None]
    mask=Image.new('L',(w*k,h*k));ImageDraw.Draw(mask).polygon([((788+65*x-5*y-x0)*k,(1709+82*y-11*x-y0)*k) for x,y in pts],fill=255)
    alpha=np.array(mask.resize((w,h),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.3)))/255
    # Use the generated paint's broad lighting only; never transfer its changed geometry/engine/portholes.
    gen=Image.open(R/'candidates/livery-generated.png').convert('RGB')
    s=np.float32([(556,215),(816,177),(638,545)])*(gen.width/1400)
    t=np.float32([(788-x0,1709-y0),(853-x0,1698-y0),(806-x0,1795-y0)])
    warp=cv2.warpAffine(np.array(gen),cv2.getAffineTransform(s,t),(w,h),flags=cv2.INTER_CUBIC)
    lum=warp@[.299,.587,.114];valid=(warp.min(axis=2)>155)&(warp.max(axis=2)-warp.min(axis=2)<45)
    shade=np.where(valid,lum,236).astype('float32');shade=cv2.GaussianBlur(shade,(0,0),4)
    curvature=234+13*np.exp(-((yy-1721)/36)**2)-.17*(yy-1700)+.035*(xx-820)
    shade=np.clip(shade*.3+curvature*.7,212,247)
    paint=np.stack([shade,shade*.997,np.minimum(shade*1.014,255)],axis=-1)
    rgb=rgb*(1-alpha[:,:,None])+paint*alpha[:,:,None]
    # Preserve the real door seam gently across both paint colours.
    seam=Image.new('L',(w*k,h*k));ImageDraw.Draw(seam).line([((x-x0)*k,(y-y0)*k) for x,y in [(819,1710),(823,1715),(825,1730),(827,1760),(824,1789)]],fill=255,width=5,joint='curve')
    sa=np.array(seam.resize((w,h),Image.Resampling.LANCZOS))/255*.25;rgb*=1-sa[:,:,None]
    rgb[glass]=a[y0:y1,x0:x1][glass]
    out=orig.copy();out.paste(Image.fromarray(np.clip(rgb,0,255).astype('uint8')),(x0,y0))
    diff=np.any(np.array(out)!=a,axis=2);diff[y0:y1,x0:x1]=False;assert not diff.any()
    assert np.array_equal(np.array(out)[y0:y1,x0:x1][glass],a[y0:y1,x0:x1][glass])
    out.save(R/'candidates/choice-wide-livery.webp',lossless=True)
    out.crop((590,1580,920,1810)).resize((990,690),Image.Resampling.LANCZOS).save(R/'sheets/livery-wide-detail.png')
    (R/'livery-check.json').write_text(json.dumps({'changed_roi':[x0,y0,x1,y1],'outside_roi_identical':True,'original_glass_pixels_identical':True,'orange_cutout_rims':False},indent=2))
    print('door-local paint; outside ROI and original porthole pixels unchanged; no orange cutout rings')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: paint-r3.py R3_WORKSPACE ORIGINAL_MEDIA_ROOT')
    main(*sys.argv[1:])
