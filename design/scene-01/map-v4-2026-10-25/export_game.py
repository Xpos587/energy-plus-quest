# Scene 1 map v4: export Blender outputs to game assets.
# python3 export_game.py [PLATE_DIR]
#   plates  : out-style/plate-{wide,tall}-empty.png (or restyled versions in PLATE_DIR)
#   sprites : out-style/sprites/{plate}-{truck}-{k}.png + sprites.json
#   geometry: out-v5/blockout.json
# Writes public/scene1-v4/*.webp and src/components/cityV4Manifest.json.
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PLATE_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "out-style"
SPR = HERE / "out-style" / "sprites"
# Repainted frames (sheet/reslice.py) override the Blender ones when present.
import os
OVR = Path(os.environ["SPR_OVR"]) if os.environ.get("SPR_OVR") else None
KEEP_PLATES = os.environ.get("KEEP_PLATES") == "1"
OUT = REPO / "public" / "scene1-v4"
OUT.mkdir(parents=True, exist_ok=True)
blk = json.loads((HERE / "out-v5" / "blockout.json").read_text())
spr = json.loads((SPR / "sprites.json").read_text())
TRUCKS = list(spr["plates"]["wide"]["trucks"].keys())
N = spr["headings"]
S = spr["scale"]


def r(v, d=2):
    return round(v, d)


man = {
    "truckM": [r(v, 3) for v in blk["truckM"]],
    "speedKmh": blk["speedKmh"],
    "routes": blk["routesWorld"],
    "headings": N,
    "rig": spr.get("rig"),
    "plates": {},
}
for pname in ("wide", "tall"):
    p = blk["plates"][pname]
    W, H = p["res"]
    src = PLATE_DIR / f"plate-{pname}-restyled.png"
    if not src.exists():
        src = HERE / "out-style" / f"plate-{pname}-empty.png"
    if not KEEP_PLATES:
        Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS).save(OUT / f"plate-{pname}.webp", quality=86, method=6)
    sp = spr["plates"][pname]
    size = sp["size"]
    # Trim every frame, then pack rows into one atlas per plate.
    frames = {}
    for tid in TRUCKS:
        for k in range(N):
            f0 = SPR / f"{pname}-{tid}-{k:02d}.png"
            if OVR and (OVR / f0.name).exists():
                f0 = OVR / f0.name
            im = Image.open(f0).convert("RGBA")
            bb = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
            x0, y0, x1, y1 = bb
            x0, y0, x1, y1 = max(0, x0 - 2), max(0, y0 - 2), min(im.width, x1 + 2), min(im.height, y1 + 2)
            frames[(tid, k)] = (im.crop((x0, y0, x1, y1)), x0, y0)
    AW = 2048
    x = y = rowh = 0
    place = {}
    for key, (im, _, _) in frames.items():
        if x + im.width > AW:
            x, y, rowh = 0, y + rowh + 2, 0
        place[key] = (x, y)
        x += im.width + 2
        rowh = max(rowh, im.height)
    atlas = Image.new("RGBA", (AW, y + rowh))
    for key, (im, _, _) in frames.items():
        atlas.paste(im, place[key])
    atlas.save(OUT / f"trucks-{pname}.webp", quality=90, method=6)
    trucks = {}
    for tid in TRUCKS:
        rows = []
        for k in range(N):
            im, cx0, cy0 = frames[(tid, k)]
            ax, ay = place[(tid, k)]
            f = sp["trucks"][tid][k]
            # offsets in plate px from the rig centre (sprite centre = size/2)
            rows.append([ax, ay, im.width, im.height, r(cx0 / S - size / 2), r(cy0 / S - size / 2),
                         r(f["exhaust"][0] - size / 2), r(f["exhaust"][1] - size / 2)])
        trucks[tid] = rows
    W2 = lambda q: [r(q[0] * W), r(q[1] * H)]
    man["plates"][pname] = {
        "res": [W, H],
        "mpp": p["metresPerPx"],
        "proj": [[round(v, 5) for v in row] for row in p["proj"]],
        "keep": p["keep"],
        "dock": W2(p["dock"]),
        "express": W2(p["express"]),
        "autopick": W2(p["autopick"]),
        "warehouse": W2(p["warehouse"]),
        "sign": [W2(q) for q in p["sign"]],
        "sprites": {"scale": S, "atlas": list(atlas.size), "trucks": trucks},
    }
    print(pname, "atlas", atlas.size, (OUT / f"trucks-{pname}.webp").stat().st_size // 1024, "KB plate", (OUT / f"plate-{pname}.webp").stat().st_size // 1024, "KB")
(REPO / "src" / "components" / "cityV4Manifest.json").write_text(json.dumps(man, separators=(",", ":")))
print("manifest", (REPO / "src" / "components" / "cityV4Manifest.json").stat().st_size // 1024, "KB")
