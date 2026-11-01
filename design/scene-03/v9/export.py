# Lettered v9 art -> runtime webp, hit regions, plaque coordinates and outcome focus.
#   python3 letter.py && python3 export.py
import json
from pathlib import Path

from PIL import Image

here = Path(__file__).parent
root = here.parents[2]
base = "scene-art/warehouse-v9"
pub = root / "public" / base
pub.mkdir(parents=True, exist_ok=True)
regions = json.loads((here / "regions.json").read_text())
letters = json.loads((here / "gen/letters.json").read_text())
METHOD = ("Generated with GPT Image 2 from the opening route thumbnail style (design/scene-03/v9), 1 November 2026; "
          "plaques and zone signs lettered by letter.py; regions drawn by hand in regions.json; "
          "alphabet runs left to right, from receiving (А–Б) to dispatch (Ю–Я)")


def webp(src, dst, size=None):
    im = Image.open(src).convert("RGB")
    (im.resize(size, Image.LANCZOS) if size else im).save(pub / dst, quality=84, method=6)


for name, layout, suffix in (("overview", "desk", ""), ("overview-mobile", "tall", ".mobile")):
    src = here / f"gen/{layout}-final.png"
    W, H = Image.open(src).size
    webp(src, f"{name}.webp")
    out = {}
    for key, r in regions[layout].items():
        x0, y0, x1, y1 = r.get("box") or r["rack"]
        ax, ay = r["anchor"]
        out[key] = {"path": f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z", "anchor": {"x": round(ax / W, 4), "y": round(ay / H, 4)},
                    "anchorPixel": [ax, ay], "contourCount": 1}
    # The lettering, not the board edge, must stay in frame: inset each board by 10%.
    signs = [[x0 + (x1 - x0) // 10, y0, x1 - (x1 - x0) // 10, y1] for x0, y0, x1, y1 in letters[layout]["signs"]]
    data = {"width": W, "height": H, "source": f"{base}/{name}.webp", "method": METHOD,
            # Both zone signs explain the task, so the overview camera keeps them.
            "overviewRequiredBounds": {"left": min(s[0] for s in signs), "top": min(s[1] for s in signs),
                                       "right": max(s[2] for s in signs), "bottom": max(s[3] for s in signs)},
            "regions": out}
    (root / f"src/scenes/inventory/segmentedContours{suffix}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

for name in ("entrance", "keeper", "wms", "alphabet-boat", "alphabet-socks", "alphabet-camera"):
    webp(here / f"gen/o-{name}.png", f"outcome-{name}.webp")
print(json.dumps({"plaques": letters["desk"]["plaques"],
                  "hotspots": {l: {k: [v["anchor"][0], v["anchor"][1]] for k, v in regions[l].items()} for l in regions}}))
