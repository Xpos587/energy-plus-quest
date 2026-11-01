# Blender manifests + v10 restyles -> runtime art and native hit regions.
#   python3 export.py   (after compose.py for desk, tall and every outcome-*)
import json
from pathlib import Path

from PIL import Image

here = Path(__file__).parent
w = here.parents[2] / ".tmp-work/v17"  # restyles + compose.py output (local only)
root = here.parents[2]
base = "scene-art/warehouse-v15"
pub = root / "public" / base
pub.mkdir(parents=True, exist_ok=True)



def webp(src, dst, size):
    Image.open(src).convert("RGB").resize(size, Image.LANCZOS).save(pub / dst, quality=84, method=6)


def contours(frame, source, method):
    W, H = frame["width"], frame["height"]
    regions = {}
    for k, r in frame["regions"].items():
        pts = " L ".join(f"{round(x)} {round(y)}" for x, y in r["hull"])
        ax, ay = r["anchor"]
        regions[k] = {"path": f"M {pts} Z", "anchor": {"x": ax / W, "y": ay / H},
                      "anchorPixel": [round(ax), round(ay)], "contourCount": 1}
    signs = frame["signs"].values()
    return {"width": W, "height": H, "source": source, "method": method,
            # Both zone signs explain the task, so the overview camera keeps them.
            "overviewRequiredBounds": {"left": round(min(s[0] for s in signs)), "top": round(min(s[1] for s in signs)),
                                       "right": round(max(s[2] for s in signs)), "bottom": round(max(s[3] for s in signs))},
            "regions": regions}


METHOD = ("Projected from the Blender warehouse (design/scene-03/blender-v1/warehouse.py) camera; v15 compact hall, rack-end letter banners, company workwear, game-map restyle, 1 November 2026; "
          "GPT restyle aligned back onto the render; alphabet runs left to right, from receiving (А–Б) to dispatch (Ю–Я)")
out = {}
for layout, fmt, name in (("wide", "desk", "overview"), ("tall", "tall", "overview-mobile")):
    frame = json.loads((here / f"manifest-{layout}-plate.json").read_text())["formats"][fmt]
    webp(w / f"gen/{fmt}-final.png", f"{name}.webp", (frame["width"], frame["height"]))
    data = contours(frame, f"{base}/{name}.webp", METHOD)
    suffix = "" if layout == "wide" else ".mobile"
    (root / f"src/scenes/inventory/segmentedContours{suffix}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    out[layout] = {"size": [frame["width"], frame["height"]], "labels": {k: [round(x / frame["width"], 4), round(y / frame["height"], 4)] for k, (x, y) in frame["labels"].items()},
                   "anchors": {k: [round(v["anchor"]["x"], 4), round(v["anchor"]["y"], 4)] for k, v in data["regions"].items()}}

outcomes = json.loads((here / "manifest-wide-outcomes.json").read_text())["outcomes"]
focus = {}
for name, frame in outcomes.items():
    webp(w / f"gen/outcome-{name}-final.png", f"outcome-{name}.webp", (frame["width"], frame["height"]))
    xs = [x for x, _ in frame["regions"][name]["hull"]]
    focus[f"inventory-{name}"] = f"{round((min(xs) + max(xs)) / 2 / frame['width'] * 100, 1)}%"
# The WMS story runs from the desk monitor to the gift on the pallet jack at the dispatch door: keep both.
wms = outcomes["wms"]
focus["inventory-wms"] = f"{round((min(x for x, _ in wms['regions']['wms']['hull']) + wms['story']['gift'][0] + 40) / 2 / wms['width'] * 100, 1)}%"
out["focus"] = focus

# Feed the game: overview hotspots, shelf plaque positions and outcome focus.
import re
wm_path = root / "src/scenes/worldManifest.json"
wm = json.loads(wm_path.read_text())
for layout, key in (("wide", "desktop"), ("tall", "mobile")):
    a = out[layout]["anchors"]
    wm["scenes"]["inventory"][key]["image"] = f"{base}/{'overview' if layout == 'wide' else 'overview-mobile'}.webp"
    wm["scenes"]["inventory"][key]["hotspots"] = [{"id": k, "x": a[r][0], "y": a[r][1]} for k, r in
                                                   (("entrance", "entrance"), ("alphabet", "alphabet-camera"), ("keeper", "keeper"), ("wms", "wms"))]
wm_path.write_text(json.dumps(wm, indent=2, ensure_ascii=False) + "\n")
alpha = root / "src/scenes/inventory/alphabet.ts"
t = alpha.read_text()
for label, (x, y) in out["wide"]["labels"].items():
    t = re.sub(rf'(label: "{label}", letters: "[^"]+", )x: [\d.]+, y: [\d.]+', rf"\g<1>x: {x}, y: {y}", t)
alpha.write_text(t)
framing = root / "src/scenes/outcomeFraming.ts"
t = framing.read_text()
for k, v in focus.items():
    t = re.sub(rf'"{k}": "[\d.]+%"', f'"{k}": "{v}"', t)
framing.write_text(t)
print(json.dumps(out, ensure_ascii=False, indent=1))
