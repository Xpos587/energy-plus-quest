# Vehicle tap zones for revision-16: GrabCut inside the old (revision-12) region bbox +margin on the half-size final map.
#   uv run --with opencv-python-headless --with numpy python contours.py  -> gen/contours.json, gen/contours-{wide,tall}.png
import json, re
from pathlib import Path
import cv2, numpy as np
here = Path(__file__).parent; root = here.parents[2]
old = json.loads((root / "src/scenes/lastmile/segmentedContours.json").read_text())
out = {}
for f, o in old.items():
    W, H = o["width"], o["height"]
    img = cv2.resize(cv2.imread(str(here / f"gen/final-{f}-arseniy.png")), (W, H), interpolation=cv2.INTER_AREA)
    vis = img.copy(); out[f] = {"width": W, "height": H, "regions": {}, "source": f"scene-art/lastmile-family-v1/revision-16/choice-{f}-*.webp"}
    for k, r in o["regions"].items():
        pts = np.array([[float(a), float(b)] for a, b in re.findall(r"(-?[\d.]+),(-?[\d.]+)", r["path"])])
        x0, y0 = np.floor(pts.min(0)).astype(int) - 16; x1, y1 = np.ceil(pts.max(0)).astype(int) + 16
        x0, y0 = max(x0, 1), max(y0, 1); x1, y1 = min(x1, W - 2), min(y1, H - 2)
        mask = np.zeros((H, W), np.uint8); bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
        cv2.grabCut(img, mask, (x0, y0, x1 - x0, y1 - y0), bg, fg, 8, cv2.GC_INIT_WITH_RECT)
        m = np.isin(mask, (1, 3)).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8)); m = cv2.dilate(m, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m); m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); c = cv2.approxPolyDP(max(cs, key=cv2.contourArea), 1.5, True)[:, 0, :]
        oldarea = cv2.contourArea(pts.astype(np.float32)); newarea = cv2.contourArea(c.astype(np.float32))
        print(f, k, "area ratio new/old", round(newarea / oldarea, 2))
        out[f]["regions"][k] = {"path": "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in c) + " Z"}
        cv2.polylines(vis, [c.reshape(-1, 1, 2)], True, (255, 0, 255), 2)
    cv2.imwrite(str(here / f"gen/contours-{f}.png"), vis)
(here / "gen/contours.json").write_text(json.dumps(out, separators=(",", ":")))
