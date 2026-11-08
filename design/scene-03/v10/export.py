# Blender plate manifests + composed restyles -> runtime overview art (wide + tall) and native hit regions.
#   python3 export.py   (after compose.py desk 2048 1365 and compose.py tall 1600 2000)
# wide: the 1536x1024 render plane is cropped to 16:9 and mapped onto the game's 1672x941 plane;
# tall: the 1200x1500 render plane is the phone plane. Rasters are downscaled from the larger composes.
import json
import re
from pathlib import Path

from PIL import Image

here = Path(__file__).parent
root = here.parents[2]
w = root / ".tmp-work/wh3d"  # restyle + compose.py output (local only)
inv = root / "src/scenes/inventory"
VERSION = "v10"
# v10 (7.11): full GPT restyle of the v18 render in the scene 1-2 painterly style (`carrier-results-2026-10-02/crew-wide-v6.webp`
# as the style reference), aligned onto the render by compose.py with the Blender lettering put back.

def export(fmt, frame_key, out_name, W, H, RW, Y0, contours_file):
    frame = json.loads((here / f"manifest-{fmt}-plate.json").read_text())["formats"][frame_key]
    k = W / RW  # render px -> plane px
    P = lambda x, y: (x * k, (y - Y0) * k)
    image = f"scene-art/{out_name}"
    src = Image.open(w / f"gen/{frame_key}-final.png").convert("RGB")
    s = src.width / RW  # compose px per render px
    src.crop((0, round(Y0 * s), src.width, round((Y0 + H / k) * s))).resize((W, H), Image.LANCZOS).save(root / "public" / image, quality=90, method=6)
    regions = {}
    for key, r in frame["regions"].items():
        x, y = r["anchor"]
        # pin tails: people's heads, the plaque's top edge (not its letters)
        # marker tips sit on the anchor. keeper: just above his head; WMS: the operator at the desk's right end, low,
        # so the two 44 px markers stay apart even on a 320 px phone (plane scale ~0.19)
        if key == "keeper":
            y = min(p[1] for p in r["hull"]) + (-22 if fmt == "wide" else 4)  # the tall plate has room: tip on his head
        if key == "wms":
            x, y = max(p[0] for p in r["hull"]) - 36 * RW / 1536, (max(p[1] for p in r["hull"]) - 10 if fmt == "wide" else min(p[1] for p in r["hull"]) + 4)
        elif key.startswith("alphabet"):
            y = min(v[1] for v in frame["labels"].values() if abs(v[0] - x) < 2) - 14 * RW / 1536
        pin = (x, y)
        ax, ay = P(*pin)
        regions[key] = {"path": "M " + " L ".join(f"{round(x)} {round(y)}" for x, y in (P(*p) for p in r["hull"])) + " Z",
                        "anchorPixel": [round(ax), round(ay)], "anchor": {"x": round(ax / W, 4), "y": round(ay / H, 4)}, "contourCount": 1}
    signs = [(*P(s_[0], s_[1]), *P(s_[2], s_[3])) for s_ in frame["signs"].values()]
    contours = {"width": W, "height": H, "source": image,
                "method": "Projected from the Blender warehouse (design/scene-03/blender-v1/warehouse.py, v18: closed shutter doors, zone boards flat on the side walls above both doors); GPT restyle in the scene 1-2 painterly style aligned back onto the render with the rendered lettering",
                "regions": regions,
                # Both zone signs explain the task, so the overview camera keeps them.
                "overviewRequiredBounds": {"left": round(min(s_[0] for s_ in signs)), "top": round(min(s_[1] for s_ in signs)),
                                           "right": round(max(s_[2] for s_ in signs)), "bottom": round(max(s_[3] for s_ in signs))}}
    (inv / contours_file).write_text(json.dumps(contours, indent=2, ensure_ascii=False) + "\n")
    print(fmt, json.dumps({k_: v["anchorPixel"] for k_, v in regions.items()}), contours["overviewRequiredBounds"])
    return frame, P, regions


frame, P, _ = export("wide", "desk", f"inventory-master-{VERSION}.webp", 1672, 941, 1536, 80, "segmentedContours.json")
export("tall", "tall", f"inventory-master-{VERSION}-tall.webp", 1200, 1500, 1200, 0, "segmentedContours.mobile.json")

wm_path = root / "src/scenes/worldManifest.json"
wm = json.loads(wm_path.read_text())
for key, f in (("desktop", "segmentedContours.json"), ("mobile", "segmentedContours.mobile.json")):
    c = json.loads((inv / f).read_text())
    wm["scenes"]["inventory"][key].update(image=c["source"], width=c["width"], height=c["height"], hotspots=[
        {"id": h, "x": c["regions"][r]["anchor"]["x"], "y": c["regions"][r]["anchor"]["y"]}
        for h, r in (("entrance", "entrance"), ("alphabet", "alphabet-camera"), ("keeper", "keeper"), ("wms", "wms"))])
wm_path.write_text(json.dumps(wm, indent=2, ensure_ascii=False) + "\n")

alpha = inv / "alphabet.ts"  # plaque order/positions on the wide plane
t = alpha.read_text()
for label, (x, y) in frame["labels"].items():
    x, y = P(x, y)
    t = re.sub(rf'(label: "{label}", letters: "[^"]+", )x: [^,]+, y: [^ ]+ / \d+ ', rf"\g<1>x: {round(x)} / 1672, y: {round(y)} / 941 ", t)
alpha.write_text(t)
