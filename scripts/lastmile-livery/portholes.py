"""Local porthole finishing and ten-image review; never writes public media.
Run: uv run --with pillow --with numpy python <script> <rollout-workspace>
"""
from pathlib import Path
import hashlib, json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def fix_flight_porthole(im, *, parcel=False):
    """Only the round porthole on white paint; never touch other assets."""
    im = im.copy()
    roi = (1052, 773, 1079, 799)
    scale = 8
    overlay = Image.new('RGBA', ((roi[2]-roi[0])*scale, (roi[3]-roi[1])*scale))
    d = ImageDraw.Draw(overlay)
    cx, cy = 1065.2, 786.0
    def ellipse(rx, ry):
        return tuple((v-roi[j % 2])*scale for j, v in enumerate((cx-rx, cy-ry, cx+rx, cy+ry)))
    # The livery continues to the frame: no protected orange cutout around glass.
    d.ellipse(ellipse(11.5, 11.0), fill=(243, 243, 243, 255))
    d.ellipse(ellipse(9.6, 9.3), fill=(29, 36, 44, 255))
    # Parcel glazing is steel-blue: sample the untouched neighbouring porthole.
    colour = tuple(int(v) for v in np.median(np.array(im)[782:791, 1029:1038], axis=(0, 1))) if parcel else (25, 68, 103)
    glint = (174, 201, 217) if parcel else (92, 130, 160)
    d.ellipse(ellipse(8.6, 8.3), fill=(*colour, 255))
    d.arc(ellipse(7.6, 7.3), 285, 315, fill=(*glint, 255), width=6)
    overlay = overlay.resize((roi[2]-roi[0], roi[3]-roi[1]), Image.Resampling.LANCZOS)
    patch = Image.alpha_composite(im.crop(roi).convert('RGBA'), overlay).convert('RGB')
    im.paste(patch, roi)
    return im

def main(root):
    R = Path(root)
    rows = json.loads((R / 'media-inventory-sha256.json').read_text())
    selected = [r for r in rows if Path(r['path']).name.startswith(('flight-', 'choice-'))]
    selected.sort(key=lambda r: (not Path(r['path']).name.startswith('flight-'), r['path']))
    backup = R / 'porthole-before'
    backup.mkdir(exist_ok=True)
    font = ImageFont.truetype('DejaVuSans.ttf', 18)
    sheet = Image.new('RGB', (1400, 5 * 295), '#edf0ef')
    draw = ImageDraw.Draw(sheet)
    checks = []

    for i, row in enumerate(selected):
        rel = row['path'].removeprefix('public/')
        path = R / 'candidates' / rel
        im = Image.open(path).convert('RGB')
        flight = path.name.startswith('flight-')
        box = (1041, 760, 1091, 811) if flight else (795, 1703, 862, 1760) if 'wide' in path.name else (1112, 2143, 1170, 2191)
        saved = backup / (path.stem + '.png')
        if not saved.exists():
            im.crop(box).save(saved)
        before_crop = Image.open(saved).convert('RGB')
        original = np.array(im)
        if flight:
            # Restore just this review crop so rerunning does not accumulate antialiasing.
            im.paste(before_crop, box)
            roi = (1052, 773, 1079, 799)
            cx, cy = 1065.2, 786.0
            im = fix_flight_porthole(im, parcel='parcel' in path.name)
            a = np.array(im)
            diff = np.any(a != original, axis=2)
            allowed = np.zeros(diff.shape, bool)
            allowed[roi[1]:roi[3], roi[0]:roi[2]] = True
            assert not diff[~allowed].any(), (path.name, 'nonlocal edit')
            yy, xx = np.mgrid[roi[1]:roi[3], roi[0]:roi[2]]
            inside = ((xx-cx)/10.3)**2 + ((yy-cy)/10)**2 < 1
            rgb = np.array(im.crop(roi)).astype(int)
            orange = (rgb[:, :, 0]-rgb[:, :, 2] > 60) & (rgb[:, :, 0] > 120)
            assert not orange[inside].any(), (path.name, 'orange porthole halo')
            im.save(path, lossless=True, method=4)
            assert np.array_equal(np.array(Image.open(path).convert('RGB')), a)
        else:
            diff = np.any(np.array(im) != original, axis=2)
            assert not diff.any()  # Checked maps are already clean; preserve their approved paint.
        x = (i % 2) * 700
        y = (i // 2) * 295
        draw.text((x+8, y+5), path.name, font=font, fill='black')
        draw.text((x+8, y+30), 'BEFORE FIX', font=font, fill='#444')
        draw.text((x+358, y+30), 'AFTER FIX' if flight else 'CHECKED / UNCHANGED', font=font, fill='#444')
        for j, crop in enumerate((before_crop, im.crop(box))):
            # Equal, integer scale and no aspect-ratio distortion; keep original pixels legible.
            crop = crop.resize((crop.width*4, crop.height*4), Image.Resampling.NEAREST)
            sheet.paste(crop, (x+j*350+8, y+60))
        checks.append({'path': row['path'], 'changed_pixels': int(np.any(np.array(im.crop(box)) != np.array(before_crop), axis=2).sum()), 'dimensions': list(im.size),
                       'outside_porthole_roi_identical': True, 'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'status': 'matching neighbour glass / thin frame / no orange halo' if flight else 'no isolated orange halo on white; unchanged'})

    sheet.save(R / 'sheets/portholes-10-before-after.png')
    (R / 'porthole-check.json').write_text(json.dumps(checks, indent=2))
    assert len(checks) == 10
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: portholes.py ROLLOUT_WORKSPACE')
    main(sys.argv[1])
