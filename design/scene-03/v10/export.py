# Blender manifests + v10 restyles -> runtime art and native hit regions.
#   python3 export.py   (after compose.py for desk, tall and every outcome-*)
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

here = Path(__file__).parent
w = here.parents[2] / ".tmp-work/v13"  # restyles + compose.py output (local only)
root = here.parents[2]
base = "scene-art/warehouse-v12"
pub = root / "public" / base
pub.mkdir(parents=True, exist_ok=True)



# Story layer: only a spotlight on the gift. The walk to dispatch is painted on
# the warehouse floor itself (Blender route + metres), so nothing floats over people.
def story(im, gift, ring=1.0):
    k = 2  # supersample
    W, H = im.size
    gx, gy = gift[0] * k, gift[1] * k
    rx, ry = 96 * ring, 76 * ring
    glow = Image.new("RGBA", (W * k, H * k))
    ImageDraw.Draw(glow).ellipse([gx - rx - 28, gy - ry - 28, gx + rx + 28, gy + ry + 28], fill=(255, 214, 80, 170))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    d = ImageDraw.Draw(glow)
    d.ellipse([gx - rx, gy - ry, gx + rx, gy + ry], fill=(0, 0, 0, 0))  # keep the gift itself clear
    for w, c in ((14, "white"), (8, "#FFC20E")):
        d.ellipse([gx - rx, gy - ry, gx + rx, gy + ry], outline=c, width=w)
    return Image.alpha_composite(im.convert("RGBA"), glow.resize((W, H), Image.LANCZOS)).convert("RGB")


def webp(src, dst, size, frame=None, name=None):
    im = Image.open(src).convert("RGB").resize(size, Image.LANCZOS)
    if frame and name:
        im = story(im, frame["story"]["gift"], ring=0.85)
    elif frame:
        # Tight ring a little below the gift top, clear of the receiving sign above.
        dy, ring = (25, 0.78) if size[0] > size[1] else (30, 0.95)  # px below the gift top; the tall frame shows it bigger
        im = story(im, (frame["gift"][0], frame["gift"][1] + dy), ring=ring)
    im.save(pub / dst, quality=84, method=6)


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


METHOD = ("Projected from the Blender warehouse (design/scene-03/blender-v1/warehouse.py) camera; v10 restyle in the game-map style, 1 November 2026; "
          "GPT restyle aligned back onto the render; alphabet runs left to right, from receiving (А–Б) to dispatch (Ю–Я)")
out = {}
for layout, fmt, name in (("wide", "desk", "overview"), ("tall", "tall", "overview-mobile")):
    frame = json.loads((here / f"manifest-{layout}-plate.json").read_text())["formats"][fmt]
    if layout == "tall":  # portrait: keeper's number sits level with the terminal's, so drop it to his chest
        frame["regions"]["keeper"]["anchor"][1] += 50
    webp(w / f"gen/{fmt}-final.png", f"{name}.webp", (frame["width"], frame["height"]), frame)
    data = contours(frame, f"{base}/{name}.webp", METHOD)
    suffix = "" if layout == "wide" else ".mobile"
    (root / f"src/scenes/inventory/segmentedContours{suffix}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    out[layout] = {"size": [frame["width"], frame["height"]], "labels": {k: [round(x / frame["width"], 4), round(y / frame["height"], 4)] for k, (x, y) in frame["labels"].items()},
                   "anchors": {k: [round(v["anchor"]["x"], 4), round(v["anchor"]["y"], 4)] for k, v in data["regions"].items()}}

outcomes = json.loads((here / "manifest-wide-outcomes.json").read_text())["outcomes"]
focus = {}
for name, frame in outcomes.items():
    webp(w / f"gen/outcome-{name}-final.png", f"outcome-{name}.webp", (frame["width"], frame["height"]), frame, name)
    xs = [x for x, _ in frame["regions"][name]["hull"]]
    focus[f"inventory-{name}"] = f"{round((min(xs) + max(xs)) / 2 / frame['width'] * 100, 1)}%"
# The WMS story ends at dispatch: the forklift taking the gift out.
wms = outcomes["wms"]
# gift sits near the right edge; bias right so the "12 m" route to dispatch stays in frame
focus["inventory-wms"] = f"{round(min(95, wms['story']['gift'][0] / wms['width'] * 100 + 6), 1)}%"
out["focus"] = focus
print(json.dumps(out, ensure_ascii=False, indent=1))
