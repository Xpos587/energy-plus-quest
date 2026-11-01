# Vehicle tap zones: OpenCV GrabCut inside the boxes below on gen/{wide,tall}-arseniy-ext.png.
#   uv run --with opencv-python-headless --with numpy python contours.py  -> contours.json
import json
import cv2, numpy as np
cfg = {'wide': {'helicopter': (50, 160, 435, 348), 'pipe-carrier': (85, 350, 376, 524), 'rover': (350, 380, 560, 540), 'robot': (562, 450, 695, 537)},
       'tall': {'helicopter': (62, 635, 492, 858), 'pipe-carrier': (196, 830, 517, 1046), 'rover': (490, 880, 730, 1062), 'robot': (746, 942, 900, 1054)}}
# Boxes are in composed-map pixels; extend.py places the map at SHIFT in the outpainted canvas.
SHIFT = {'wide': (0, 226), 'tall': (128, 0)}
out = {}
for f, boxes in cfg.items():
    img = cv2.imread(f'gen/{f}-arseniy-ext.png'); dx, dy = SHIFT[f]; H, W = img.shape[:2]
    out[f] = {'width': W, 'height': H, 'regions': {}}; vis = img.copy()
    for k, (x0, y0, x1, y1) in boxes.items():
        x0, x1, y0, y1 = x0 + dx, x1 + dx, y0 + dy, y1 + dy
        mask = np.zeros((H, W), np.uint8); bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
        cv2.grabCut(img, mask, (x0, y0, x1 - x0, y1 - y0), bg, fg, 8, cv2.GC_INIT_WITH_RECT)
        m = np.isin(mask, (1, 3)).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8)); m = cv2.dilate(m, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m); m = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); c = max(cs, key=cv2.contourArea)
        c = cv2.approxPolyDP(c, 1.5, True)[:, 0, :]
        out[f]['regions'][k] = {'path': "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in c) + " Z"}
        cv2.polylines(vis, [c.reshape(-1, 1, 2)], True, (255, 0, 255), 2)
        print(f, k, len(c), m.sum() / ((x1 - x0) * (y1 - y0)))
    cv2.imwrite(f'gen/contours-{f}.png', vis)
json.dump(out, open('contours.json', 'w'))
