# Blender plate manifest + composed restyle -> runtime overview art and native hit regions.
#   python3 export.py   (after compose.py desk 1536 1024)
# The 1536x1024 render is cropped to 16:9 and scaled onto the game's 1672x941 plane.
import json
import re
from pathlib import Path

from PIL import Image

here = Path(__file__).parent
root = here.parents[2]
w = root / ".tmp-work/wh3d"  # restyle + compose.py output (local only)
IMAGE = "scene-art/inventory-master-v7.webp"
W, H, Y0 = 1672, 941, 100  # target plane; crop top in render px
k = W / 1536
frame = json.loads((here / "manifest-wide-plate.json").read_text())["formats"]["desk"]
P = lambda x, y: (x * k, (y - Y0) * k)
# Pin tails (render px) picked on the restyled art: plaque top edge, not its letters;
# keeper's head and the WMS operator's head, far enough apart for two pins on a phone.
PIN = {"keeper": (1234, 612), "wms": (1300, 706)} | {f"alphabet-{p}": (frame["regions"][f"alphabet-{p}"]["anchor"][0], 650) for p in ("camera", "socks", "boat")}

Image.open(w / "gen/desk-final.png").convert("RGB").crop((0, Y0, 1536, Y0 + round(H / k))).resize((W, H), Image.LANCZOS).save(root / "public" / IMAGE, quality=90, method=6)

regions = {}
for key, r in frame["regions"].items():
    pts = [P(*p) for p in r["hull"]]
    ax, ay = P(*PIN.get(key, r["anchor"]))
    regions[key] = {"path": "M " + " L ".join(f"{round(x)} {round(y)}" for x, y in pts) + " Z",
                    "anchorPixel": [round(ax), round(ay)], "anchor": {"x": round(ax / W, 4), "y": round(ay / H, 4)}, "contourCount": 1}
signs = [(*P(s[0], s[1]), *P(s[2], s[3])) for s in frame["signs"].values()]
contours = {"width": W, "height": H, "source": IMAGE,
            "method": "Projected from the Blender warehouse (design/scene-03/blender-v1/warehouse.py, v16: the pre-3D illustration's plan, docks in both side walls); GPT restyle aligned back onto the render with the rendered lettering",
            "regions": regions,
            # Both zone signs explain the task, so the overview camera keeps them.
            "overviewRequiredBounds": {"left": round(min(s[0] for s in signs)), "top": round(min(s[1] for s in signs)),
                                       "right": round(max(s[2] for s in signs)), "bottom": round(max(s[3] for s in signs))}}
(root / "src/scenes/inventory/segmentedContours.json").write_text(json.dumps(contours, indent=2, ensure_ascii=False) + "\n")

wm_path = root / "src/scenes/worldManifest.json"
wm = json.loads(wm_path.read_text())
for key in ("desktop", "mobile"):
    wm["scenes"]["inventory"][key].update(image=IMAGE, width=W, height=H, hotspots=[
        {"id": c, "x": regions[r]["anchor"]["x"], "y": regions[r]["anchor"]["y"]}
        for c, r in (("entrance", "entrance"), ("alphabet", "alphabet-camera"), ("keeper", "keeper"), ("wms", "wms"))])
wm_path.write_text(json.dumps(wm, indent=2, ensure_ascii=False) + "\n")

alpha = root / "src/scenes/inventory/alphabet.ts"
t = alpha.read_text()
for label, (x, y) in frame["labels"].items():
    x, y = P(x, y)
    t = re.sub(rf'(label: "{label}", letters: "[^"]+", )x: [^,]+, y: [^ ]+ / \d+ ', rf"\g<1>x: {round(x)} / {W}, y: {round(y)} / {H} ", t)
alpha.write_text(t)
print(json.dumps({k_: v["anchorPixel"] for k_, v in regions.items()}), contours["overviewRequiredBounds"])
