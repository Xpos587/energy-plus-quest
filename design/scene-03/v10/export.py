# Blender manifests + v10 restyles -> runtime art and native hit regions.
#   python3 export.py   (after compose.py for desk, tall and every outcome-*)
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

here = Path(__file__).parent
w = here.parents[2] / ".tmp-work/v10"  # restyles + compose.py output (local only)
root = here.parents[2]
base = "scene-art/warehouse-v11"
pub = root / "public" / base
pub.mkdir(parents=True, exist_ok=True)



# Story layer, game-UI style: a spotlight on the gift and the path it travels.
# Red = long detour, amber = running around, green = short and right.
STORY = {"entrance": "#E8402A", "alphabet-boat": "#F29A0D", "alphabet-camera": "#F29A0D", "alphabet-socks": "#F29A0D",
         "keeper": "#E8402A", "wms": "#2FB86A"}
BADGE = {"entrance": "clock", "keeper": "search", "wms": "check"}


def story(im, gift, route=(), col="#FFC20E", badge=None, pin=True, ring=1.0):
    k = 2  # supersample
    W, H = im.size
    lay = Image.new("RGBA", (W * k, H * k))
    d = ImageDraw.Draw(lay)
    P = lambda p: (p[0] * k, p[1] * k)
    if route:
        pts = [P(p) for p in route]
        for w, c in ((26, "white"), (15, col)):
            d.line(pts, fill=c, width=w * k // 2 * 2, joint="curve")
            for q in pts[:-1]:
                d.ellipse([q[0] - w, q[1] - w, q[0] + w, q[1] + w], fill=c)
        (x0, y0), (x1, y1) = pts[-2], pts[-1]  # arrowhead
        L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 or 1
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        tri = lambda s: [(x1 + ux * s * 1.2, y1 + uy * s * 1.2), (x1 - ux * s + uy * s, y1 - uy * s - ux * s), (x1 - ux * s - uy * s, y1 - uy * s + ux * s)]
        d.polygon(tri(46), fill="white")
        d.polygon(tri(32), fill=col)
    gx, gy = P(gift)
    rx, ry = 96 * ring, 76 * ring
    d.ellipse([gx - rx, gy - ry, gx + rx, gy + ry], fill=(0, 0, 0, 0))  # the route leaves the ring, not the gift
    glow = Image.new("RGBA", lay.size)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([gx - rx - 28, gy - ry - 28, gx + rx + 28, gy + ry + 28], fill=(255, 214, 80, 170))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    ImageDraw.Draw(glow).ellipse([gx - rx, gy - ry, gx + rx, gy + ry], fill=(0, 0, 0, 0))  # keep the gift itself clear
    lay = Image.alpha_composite(glow, lay)
    d = ImageDraw.Draw(lay)
    for w, c in ((14, "white"), (8, "#FFC20E")):
        d.ellipse([gx - rx, gy - ry, gx + rx, gy + ry], outline=c, width=w)
    tip = gy - 90  # pin pointing down at the gift
    for g, c in ((12, "white"), (0, "#FFC20E")) if pin else ():
        d.polygon([(gx, tip + g * 0.8), (gx - 36 - g, tip - 60 - g / 2), (gx + 36 + g, tip - 60 - g / 2)], fill=c)
    if badge and route:
        bx, by = P(route[len(route) // 2]) if badge != "check" else P(route[-1])
        by -= 96
        r = 60
        d.ellipse([bx - r - 7, by - r - 7, bx + r + 7, by + r + 7], fill="white")
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col)
        if badge == "clock":
            d.ellipse([bx - 38, by - 38, bx + 38, by + 38], outline="white", width=10)
            d.line([(bx, by - 24), (bx, by), (bx + 18, by + 10)], fill="white", width=10, joint="curve")
        elif badge == "check":
            d.line([(bx - 32, by + 2), (bx - 8, by + 26), (bx + 34, by - 24)], fill="white", width=15, joint="curve")
        else:  # magnifier
            d.ellipse([bx - 34, by - 34, bx + 16, by + 16], outline="white", width=11)
            d.line([(bx + 10, by + 10), (bx + 34, by + 34)], fill="white", width=15)
    lay = lay.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")


def webp(src, dst, size, frame=None, name=None):
    im = Image.open(src).convert("RGB").resize(size, Image.LANCZOS)
    if frame and name in STORY:
        st = frame["story"]
        route = st["route"] if name in ("keeper", "wms") else [st["gift"]] + st["route"][1:]  # the gift is where the walk starts
        if name == "keeper":  # the spot itself is right (short green way out); finding it is the problem
            im = story(im, st["gift"], st["hot"], STORY["wms"], "check", pin=False)
        im = story(im, st["gift"], route, STORY[name], BADGE.get(name, "clock"))
    elif frame:
        # Tight ring a little below the gift top, clear of the receiving sign above.
        dy, ring = (25, 0.78) if size[0] > size[1] else (30, 0.95)  # px below the gift top; the tall frame shows it bigger
        im = story(im, (frame["gift"][0], frame["gift"][1] + dy), pin=False, ring=ring)
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
# The WMS story ends at dispatch: frame the terminal and the forklift taking the gift out.
focus["inventory-wms"] = "42%"
out["focus"] = focus
print(json.dumps(out, ensure_ascii=False, indent=1))
