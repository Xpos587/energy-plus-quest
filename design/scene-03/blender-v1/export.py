# Blender manifest + styled renders -> runtime art and native hit regions.
#   python3 export.py   (after plate/outcome renders, gen/*-final.png)
import json
from pathlib import Path

from PIL import Image

here = Path(__file__).parent
root = here.parents[2]
base = "scene-art/warehouse-v7"
pub = root / "public" / base
pub.mkdir(parents=True, exist_ok=True)
SS = 1.5  # plate supersampling


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


METHOD = ("Projected from the Blender warehouse (design/scene-03/blender-v1/warehouse.py) camera, 29 October 2026; "
          "GPT restyle aligned back onto the render; alphabet runs left to right, from receiving (А–Б) to dispatch (Ю–Я)")
out = {}
for layout, fmt, name in (("wide", "desk", "overview"), ("tall", "tall", "overview-mobile")):
    frame = json.loads((here / f"out/manifest-{layout}-plate.json").read_text())["formats"][fmt]
    webp(here / f"gen/{fmt}-final.png", f"{name}.webp", (frame["width"], frame["height"]))
    data = contours(frame, f"{base}/{name}.webp", METHOD)
    suffix = "" if layout == "wide" else ".mobile"
    (root / f"src/scenes/inventory/segmentedContours{suffix}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    out[layout] = {"size": [frame["width"], frame["height"]], "labels": {k: [round(x / frame["width"], 4), round(y / frame["height"], 4)] for k, (x, y) in frame["labels"].items()},
                   "anchors": {k: [round(v["anchor"]["x"], 4), round(v["anchor"]["y"], 4)] for k, v in data["regions"].items()}}

outcomes = json.loads((here / "out/manifest-wide-outcomes.json").read_text())["outcomes"]
focus = {}
for name, frame in outcomes.items():
    webp(here / f"gen/outcome-{name}-final.png", f"outcome-{name}.webp", (frame["width"], frame["height"]))
    xs = [x for x, _ in frame["regions"][name]["hull"]]
    focus[f"inventory-{name}"] = f"{round((min(xs) + max(xs)) / 2 / frame['width'] * 100, 1)}%"
# The WMS story ends at dispatch: frame the terminal and the forklift taking the gift out.
focus["inventory-wms"] = "42%"
out["focus"] = focus
print(json.dumps(out, ensure_ascii=False, indent=1))
